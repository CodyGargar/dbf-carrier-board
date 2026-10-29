# Grid A* autorouter for the Rev B board (KiCad 7 pcbnew + numpy).
# Signals on F.Cu and B.Cu (In2.Cu only where needed, at extra cost); In1.Cu = GND plane, In2.Cu = VSERVO plane around the tracks.
# Run after make_board.py:  /usr/bin/python3 route_board.py
import os, pcbnew, numpy as np, heapq, math, sys, time, random

BRD = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dbf-carrier.kicad_pcb')
RES = 0.1                 # grid pitch, mm
OX = OY = 100.0
W, H = 86.0, 66.0
CL = 0.2                  # routing clearance (DRC rule is 0.15, extra margin for the grid)
TW = 0.2                  # default track width
VIA_D, VIA_DRILL = 0.6, 0.3
VIA_COST = 12.0
NL = 3                    # grid layers: 0 F.Cu, 1 B.Cu, 2 In2.Cu
LAYERS = [pcbnew.F_Cu, pcbnew.B_Cu, pcbnew.In2_Cu]
IN2_COST = 2.5
PLANE = {'GND': 0, 'VSERVO': 1}          # net -> inner plane (In1, In2)
WIDTH = {'VIN': 0.5, '+5V': 0.5, '+3V3S': 0.3}
POWER_ORDER = ['VIN', '+5V', '+3V3S']

nx, ny = int(round(W / RES)) + 1, int(round(H / RES)) + 1
N = nx * ny
XS = np.arange(nx) * RES
YS = np.arange(ny) * RES
mm = pcbnew.FromMM
def tomm(v): return pcbnew.ToMM(v)

b = pcbnew.LoadBoard(BRD)
for t in list(b.GetTracks()): b.Remove(t)
for z in list(b.Zones()): b.Remove(z)

# ---------- obstacle model ----------
# own[L]: 0 free, >0 the only net whose track centreline may sit here, -1 nobody.
K_T = TW / 2 + CL          # copper edge -> track centreline
K_V = VIA_D / 2 + CL       # copper edge -> via centre

class Grids:
    def __init__(self):
        self.own = [np.zeros((ny, nx), np.int32) for _ in range(NL)]
        self.vown = [np.zeros((ny, nx), np.int32) for _ in range(NL)]
        self.vblock = np.zeros((ny, nx), bool)
    def copy(self):
        g = Grids.__new__(Grids)
        g.own = [a.copy() for a in self.own]; g.vown = [a.copy() for a in self.vown]
        g.vblock = self.vblock.copy(); return g

def window(x1, y1, x2, y2):
    i1 = max(0, int(math.floor(x1 / RES))); i2 = min(nx, int(math.ceil(x2 / RES)) + 1)
    j1 = max(0, int(math.floor(y1 / RES))); j2 = min(ny, int(math.ceil(y2 / RES)) + 1)
    return i1, i2, j1, j2

def put(grid, i1, i2, j1, j2, m, net):
    g = grid[j1:j2, i1:i2]
    cur = g[m]
    g[m] = np.where((cur == 0) | (cur == net), net, -1)

def d_rect(X, Y, r):
    x1, y1, x2, y2 = r
    dx = np.maximum(np.maximum(x1 - X, 0), X - x2)
    dy = np.maximum(np.maximum(y1 - Y, 0), Y - y2)
    return np.hypot(dx, dy)

def d_seg(X, Y, a, c):
    ax, ay = a; bx, by = c
    vx, vy = bx - ax, by - ay
    L2 = vx * vx + vy * vy
    t = np.clip(((X - ax) * vx + (Y - ay) * vy) / L2, 0, 1) if L2 > 0 else 0 * X
    return np.hypot(X - ax - t * vx, Y - ay - t * vy)

def mark_shape(G, layers, net, kind, geom, extra=0.0, vblock=False):
    """kind 'rect' geom=(x1,y1,x2,y2); 'circ' geom=(cx,cy,r); 'seg' geom=(a,b,halfwidth)"""
    if kind == 'rect': bb = geom
    elif kind == 'circ': bb = (geom[0] - geom[2], geom[1] - geom[2], geom[0] + geom[2], geom[1] + geom[2])
    else:
        (ax, ay), (bx, by), hw = geom
        bb = (min(ax, bx) - hw, min(ay, by) - hw, max(ax, bx) + hw, max(ay, by) + hw)
    kmax = K_V + extra
    i1, i2, j1, j2 = window(bb[0] - kmax, bb[1] - kmax, bb[2] + kmax, bb[3] + kmax)
    X, Y = np.meshgrid(XS[i1:i2], YS[j1:j2])
    if kind == 'rect': d = d_rect(X, Y, geom)
    elif kind == 'circ': d = np.hypot(X - geom[0], Y - geom[1]) - geom[2]
    else: d = d_seg(X, Y, geom[0], geom[1]) - geom[2]
    d = d - extra
    for L in layers:
        put(G.own[L], i1, i2, j1, j2, d < K_T - 1e-6, net)
        put(G.vown[L], i1, i2, j1, j2, d < K_V - 1e-6, net)
    if vblock:
        G.vblock[j1:j2, i1:i2] |= d <= K_V

def pad_geom(p):
    pos = p.GetPosition(); cx, cy = tomm(pos.x) - OX, tomm(pos.y) - OY
    sh = p.GetShape(); s = p.GetSize()
    if sh == pcbnew.PAD_SHAPE_CIRCLE or (sh == pcbnew.PAD_SHAPE_OVAL and s.x == s.y):
        return 'circ', (cx, cy, tomm(s.x) / 2)
    bb = p.GetBoundingBox()
    return 'rect', (tomm(bb.GetLeft()) - OX, tomm(bb.GetTop()) - OY, tomm(bb.GetRight()) - OX, tomm(bb.GetBottom()) - OY)

def inside(kind, geom, X, Y):
    if kind == 'circ': return np.hypot(X - geom[0], Y - geom[1]) <= geom[2] - 0.05
    x1, y1, x2, y2 = geom
    return (X >= x1 + 0.05) & (X <= x2 - 0.05) & (Y >= y1 + 0.05) & (Y <= y2 - 0.05)

netid = {}           # net name -> int id used in the grids
pads_by_net = {}
dummy = [100000]
def nid(name):
    if name not in netid: netid[name] = len(netid) + 1
    return netid[name]

base = Grids()
# board edge: chamfered rectangle (2 mm corners)
X, Y = np.meshgrid(XS, YS)
def edge_dist(X, Y):
    d = np.minimum(np.minimum(X, W - X), np.minimum(Y, H - Y))
    c = 2.0
    for sx, sy in [(0, 0), (W, 0), (0, H), (W, H)]:
        u = np.abs(X - sx) + np.abs(Y - sy)
        d = np.minimum(d, (u - c) / math.sqrt(2))
    return d
ED = edge_dist(X, Y)
for L in range(NL):
    base.own[L][ED < 0.3 + TW / 2 + 0.05] = -1
    base.vown[L][ED < 0.3 + VIA_D / 2 + 0.05] = -1

for f in b.GetFootprints():
    for p in f.Pads():
        kind, geom = pad_geom(p)
        name = p.GetNetname()
        if p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH:
            mark_shape(base, list(range(NL)), -1, kind, geom, vblock=True); continue
        if name:
            n = nid(name); pads_by_net.setdefault(name, []).append(p)
        else:
            dummy[0] += 1; n = dummy[0]
        layers = [L for L, lay in enumerate(LAYERS) if p.IsOnLayer(lay)]
        smd = p.GetAttribute() == pcbnew.PAD_ATTRIB_SMD
        mark_shape(base, layers, n, kind, geom, vblock=smd)

# reserve a short escape lane in front of every fine-pitch IC pin, so earlier routes can't seal pins in
ESC = 1.2
for f in b.GetFootprints():
    if not f.GetReference().startswith('U') or f.GetReference() == 'U5': continue
    fc = f.GetPosition(); fx, fy = tomm(fc.x) - OX, tomm(fc.y) - OY
    for p in f.Pads():
        if p.GetAttribute() != pcbnew.PAD_ATTRIB_SMD or not p.GetNetname(): continue
        kind, (x1, y1, x2, y2) = pad_geom(p)
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        if x2 - x1 >= y2 - y1:
            sgn = 1 if cx >= fx else -1
            end = ((x2 if sgn > 0 else x1) + sgn * ESC, cy)
        else:
            sgn = 1 if cy >= fy else -1
            end = (cx, (y2 if sgn > 0 else y1) + sgn * ESC)
        mark_shape(base, [0], netid[p.GetNetname()], 'seg', ((cx, cy), end, 0.0))

# ---------- search ----------
STATS = {'limit': 0, 'exhausted': 0}
SQ2 = math.sqrt(2)
DIRS = [(1, 0, 1.0), (-1, 0, 1.0), (0, 1, 1.0), (0, -1, 1.0), (1, 1, SQ2), (1, -1, SQ2), (-1, 1, SQ2), (-1, -1, SQ2)]
DOFF = [dy * nx + dx for dx, dy, _ in DIRS]

def dilate(m, r):
    if r <= 0: return m
    out = m.copy()
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if dx * dx + dy * dy > r * r + r: continue
            sh = np.roll(np.roll(m, dy, 0), dx, 1)
            out |= sh
    return out

def legal_maps(G, n, width):
    extra = max(0, int(math.ceil((width / 2 - TW / 2) / RES - 1e-6)))
    ok = []
    for L in range(NL):
        blk = (G.own[L] != 0) & (G.own[L] != n)
        ok.append(~dilate(blk, extra))
    vext = max(0, int(math.ceil((max(VIA_D, width) / 2 - VIA_D / 2) / RES - 1e-6)))
    vblk = np.zeros((ny, nx), bool)
    for L in range(NL): vblk |= (G.vown[L] != 0) & (G.vown[L] != n)
    vok = ~(dilate(vblk, vext) | G.vblock)
    return bytearray(np.concatenate([o.ravel() for o in ok]).astype(np.uint8).tobytes()), \
           bytearray(vok.ravel().astype(np.uint8).tobytes())

def astar(starts, goal, ok, vok, tgt, via_goal=False, limit=1500000):
    """starts: iterable of flat idx (layer*N + cell). goal: set/bytearray of idx, or None with via_goal."""
    tx1, ty1, tx2, ty2 = tgt
    def h(c):
        x = c % nx; y = c // nx
        dx = max(tx1 - x, 0, x - tx2); dy = max(ty1 - y, 0, y - ty2)
        return (dx + dy) + (SQ2 - 2) * min(dx, dy)
    g = {}; came = {}; pq = []
    for s in starts:
        g[s] = 0.0; came[s] = (-1, -1)
        heapq.heappush(pq, (h(s % N), 0.0, s))
    exp = 0
    while pq:
        f, gs, s = heapq.heappop(pq)
        if gs > g.get(s, 1e18): continue
        L, c = divmod(s, N)
        if via_goal:
            if vok[c] and came[s][0] != -1: return reconstruct(came, s)
        elif goal[s]: return reconstruct(came, s)
        exp += 1
        if exp > limit:
            STATS['limit'] += 1; return None
        pdir = came[s][1]
        x = c % nx
        for k in range(8):
            dx = DIRS[k][0]
            if (dx == 1 and x == nx - 1) or (dx == -1 and x == 0): continue
            t = s + DOFF[k]
            if t < L * N or t >= (L + 1) * N or not ok[t]: continue
            ng = gs + DIRS[k][2] * (IN2_COST if L == 2 else 1.0) + (0.0 if k == pdir or pdir < 0 else 0.15)
            if ng < g.get(t, 1e18):
                g[t] = ng; came[t] = (s, k)
                heapq.heappush(pq, (ng + h(t - L * N), ng, t))
        if vok[c]:
            for L2 in range(NL):
                if L2 == L: continue
                t = L2 * N + c
                if ok[t]:
                    ng = gs + VIA_COST
                    if ng < g.get(t, 1e18):
                        g[t] = ng; came[t] = (s, 8)
                        heapq.heappush(pq, (ng + h(c), ng, t))
    STATS['exhausted'] += 1
    return None

def reconstruct(came, s):
    path = [s]
    while came[s][0] != -1:
        s = came[s][0]; path.append(s)
    return path[::-1]

def path_to_items(path):
    """-> list of ('seg', L, (x,y), (x,y)) and ('via', (x,y))"""
    items = []
    def xy(c): return ((c % nx) * RES, (c // nx) * RES)
    i = 0
    while i < len(path) - 1:
        L, c = divmod(path[i], N)
        L2, c2 = divmod(path[i + 1], N)
        if L2 != L:
            items.append(('via', xy(c))); i += 1; continue
        d = c2 - c; j = i + 1
        while j + 1 < len(path):
            L3, c3 = divmod(path[j + 1], N)
            if L3 != L or c3 - divmod(path[j], N)[1] != d: break
            j += 1
        items.append(('seg', L, xy(c), xy(divmod(path[j], N)[1]))); i = j
    return items

def pad_cells(p, n_layers_ok, ok):
    kind, geom = pad_geom(p)
    bb = geom if kind == 'rect' else (geom[0] - geom[2], geom[1] - geom[2], geom[0] + geom[2], geom[1] + geom[2])
    i1, i2, j1, j2 = window(*bb)
    Xs, Ys = np.meshgrid(XS[i1:i2], YS[j1:j2])
    m = inside(kind, geom, Xs, Ys)
    jj, ii = np.nonzero(m)
    cells = (jj + j1) * nx + (ii + i1)
    out = []
    for L, lay in enumerate(LAYERS):
        if p.IsOnLayer(lay):
            out += [L * N + int(c) for c in cells]
    good = [s for s in out if ok[s]]
    return good if good else out, (i1, j1, i2 - 1, j2 - 1)

def pname(p):
    return pcbnew.Cast_to_FOOTPRINT(p.GetParent()).GetReference() + '.' + p.GetNumber() if False else p.GetParentAsString() + '.' + p.GetNumber()

def pad_center(p):
    q = p.GetPosition(); return (tomm(q.x) - OX, tomm(q.y) - OY)

def route_all(order, verbose=False):
    G = base.copy()
    result = {}; failed = []
    for name in order:
        n = netid[name]
        pads = pads_by_net[name]
        w0 = WIDTH.get(name, TW)
        items_all = []
        if name in PLANE:
            # every SMD pad drops a short stub + via into its plane; THT pads reach the plane directly
            for p in pads:
                if p.GetAttribute() != pcbnew.PAD_ATTRIB_SMD: continue
                done = False
                for w in (0.3, TW):
                    ok, vok = legal_maps(G, n, w)
                    st, bb = pad_cells(p, None, ok)
                    path = astar(st, None, ok, vok, bb, via_goal=True, limit=40000)
                    if path:
                        its = path_to_items(path); its.append(('via', ((path[-1] % N) % nx * RES, (path[-1] % N) // nx * RES)))
                        commit(G, n, its, w); items_all.append((w, its)); done = True; break
                if not done: failed.append((name, pname(p)))
            result[name] = items_all; continue
        # multi-pin net: grow a tree
        rem = list(pads)
        cx = sum(pad_center(p)[0] for p in rem) / len(rem); cy = sum(pad_center(p)[1] for p in rem) / len(rem)
        rem.sort(key=lambda p: (pad_center(p)[0] - cx) ** 2 + (pad_center(p)[1] - cy) ** 2)
        first = rem.pop(0)
        okt, _ = legal_maps(G, n, TW)
        tree = set(pad_cells(first, None, okt)[0]); tree_pts = [pad_center(first)]
        while rem:
            rem.sort(key=lambda p: min((pad_center(p)[0] - a) ** 2 + (pad_center(p)[1] - c) ** 2 for a, c in tree_pts))
            p = rem.pop(0)
            done = False
            for w in sorted({w0, 0.25, TW}, reverse=True):
                if w > w0: continue
                ok, vok = legal_maps(G, n, w)
                goal_cells, bb = pad_cells(p, None, ok)
                goal = bytearray(NL * N)
                for s in goal_cells: goal[s] = 1
                if any(goal[s] for s in tree):
                    done = True; break
                st = [s for s in tree if ok[s]] or list(tree)
                path = astar(st, goal, ok, vok, bb)
                if path:
                    its = path_to_items(path); commit(G, n, its, w); items_all.append((w, its))
                    tree.update(path); tree.update(goal_cells)
                    tree_pts += [((s % N) % nx * RES, (s % N) // nx * RES) for s in path[::10]] + [pad_center(p)]
                    done = True; break
            if not done:
                failed.append((name, pname(p)))
                tree.update(pad_cells(p, None, okt)[0]); tree_pts.append(pad_center(p))
        result[name] = items_all
        if verbose: print(' routed', name, 'fails so far', len(failed), flush=True)
    return result, failed

def commit(G, n, its, w):
    for it in its:
        if it[0] == 'seg':
            mark_shape(G, [it[1]], n, 'seg', (it[2], it[3], w / 2))
        else:
            mark_shape(G, list(range(NL)), n, 'circ', (it[1][0], it[1][1], VIA_D / 2))

def hpwl(name):
    pts = [pad_center(p) for p in pads_by_net[name]]
    return (max(x for x, _ in pts) - min(x for x, _ in pts)) + (max(y for _, y in pts) - min(y for _, y in pts))

if __name__ == '__main__':
    sig = [n for n in pads_by_net if n not in PLANE and n not in POWER_ORDER and len(pads_by_net[n]) > 1]
    sig.sort(key=hpwl)
    prio = []
    best = None
    random.seed(1)
    for it in range(int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 8):
        order = [n for n in POWER_ORDER if n in pads_by_net] + ['GND', 'VSERVO'] + prio + [n for n in sig if n not in prio]
        t0 = time.time()
        res, failed = route_all(order, verbose=('-v' in sys.argv))
        print('pass', it, 'failed', len(failed), failed[:12], '%.0fs' % (time.time() - t0), STATS, flush=True)
        if best is None or len(failed) < len(best[1]): best = (res, failed)
        if not failed: break
        for f, _ in failed:
            if f in prio: prio.remove(f)
            prio.insert(0, f)
    res, failed = best
    # write tracks and vias
    nets = b.GetNetsByName()
    for name, lst in res.items():
        net = nets[name]
        for w, its in lst:
            for it in its:
                if it[0] == 'seg':
                    if it[2] == it[3]: continue
                    t = pcbnew.PCB_TRACK(b); t.SetStart(pcbnew.VECTOR2I(mm(OX + it[2][0]), mm(OY + it[2][1])))
                    t.SetEnd(pcbnew.VECTOR2I(mm(OX + it[3][0]), mm(OY + it[3][1])))
                    t.SetWidth(mm(w)); t.SetLayer(LAYERS[it[1]]); t.SetNet(net); b.Add(t)
                else:
                    v = pcbnew.PCB_VIA(b); v.SetPosition(pcbnew.VECTOR2I(mm(OX + it[1][0]), mm(OY + it[1][1])))
                    v.SetWidth(mm(VIA_D)); v.SetDrill(mm(VIA_DRILL)); v.SetNet(net); b.Add(v)
    print('UNROUTED', failed)
    pcbnew.SaveBoard(BRD.replace('.kicad_pcb', '-routed-raw.kicad_pcb'), b)
