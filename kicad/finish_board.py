# Planes, design rules, zone fill, DRC and JLCPCB outputs for the routed Rev B board.
# Run after route_board.py:  /usr/bin/python3 finish_board.py
import pcbnew, subprocess, csv, os, re, shutil
D = os.path.dirname(os.path.abspath(__file__)) + '/'
SRC = D + 'dbf-carrier-routed-raw.kicad_pcb'
OUT = D + 'dbf-carrier.kicad_pcb'
JLC = os.path.join(D, '..', 'jlcpcb') + '/'
mm = pcbnew.FromMM
OX = OY = 100.0
W, H = 86.0, 66.0

b = pcbnew.LoadBoard(SRC)
ds = b.GetDesignSettings()
ds.m_MinClearance = mm(0.15)
ds.m_TrackMinWidth = mm(0.15)
ds.m_ViasMinSize = mm(0.5)
ds.m_MinThroughDrill = mm(0.3)
ds.m_CopperEdgeClearance = mm(0.3)
ds.m_HoleClearance = mm(0.25)
nc = ds.m_NetSettings.m_DefaultNetClass
nc.SetClearance(mm(0.15)); nc.SetTrackWidth(mm(0.2)); nc.SetViaDiameter(mm(0.6)); nc.SetViaDrill(mm(0.3))

# silkscreen text at least 0.8 mm tall so it prints legibly
for d in b.GetDrawings():
    if d.GetClass() == 'PCB_TEXT' and d.GetTextHeight() < mm(0.8):
        d.SetTextSize(pcbnew.VECTOR2I(mm(0.8), mm(0.8))); d.SetTextThickness(mm(0.12))

# pin names under the Pololu S7V7F5 (U5) so the module goes in the right way round:
# VIN on the square pad, GND in the middle, VOUT on the right (matches the labels on the module's back)
for t, x in (('VIN', 9.5), ('GND', 12.04), ('OUT', 14.58)):
    s = pcbnew.PCB_TEXT(b); s.SetText(t); s.SetLayer(pcbnew.F_SilkS)
    s.SetPosition(pcbnew.VECTOR2I(mm(OX + x), mm(OY + 32.0)))
    s.SetTextSize(pcbnew.VECTOR2I(mm(0.8), mm(0.8))); s.SetTextThickness(mm(0.12)); b.Add(s)

# two plane-escape vias of the same net that landed on top of each other: keep one, bridge the other
vias = [t for t in b.GetTracks() if t.GetClass() == 'PCB_VIA']
gone = set()
for i, v in enumerate(vias):
    for u in vias[i + 1:]:
        if id(u) in gone or id(v) in gone or u.GetNetCode() != v.GetNetCode(): continue
        p, q = v.GetPosition(), u.GetPosition()
        if (p - q).EuclideanNorm() < mm(0.9):
            t = pcbnew.PCB_TRACK(b); t.SetStart(q); t.SetEnd(p); t.SetWidth(mm(0.3)); t.SetLayer(pcbnew.F_Cu); t.SetNet(u.GetNet()); b.Add(t)
            b.Remove(u); gone.add(id(u))
print('merged vias', len(gone))

def outline():
    c = 2.0
    pts = [(c, 0), (W - c, 0), (W, c), (W, H - c), (W - c, H), (c, H), (0, H - c), (0, c)]
    return pts

nets = b.GetNetsByName()
def zone(layer, net, prio):
    z = pcbnew.ZONE(b)
    z.SetLayer(layer); z.SetNet(nets[net]); z.SetAssignedPriority(prio)
    ol = z.Outline(); ol.NewOutline()
    for x, y in outline(): ol.Append(mm(OX + x), mm(OY + y))
    z.SetLocalClearance(mm(0.2)); z.SetMinThickness(mm(0.2))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
    z.SetThermalReliefGap(mm(0.25)); z.SetThermalReliefSpokeWidth(mm(0.4))
    z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    b.Add(z); return z

zone(pcbnew.In1_Cu, 'GND', 0)
zone(pcbnew.In2_Cu, 'VSERVO', 0)
zone(pcbnew.F_Cu, 'GND', 0)
zone(pcbnew.B_Cu, 'GND', 0)
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
pcbnew.SaveBoard(OUT, b)

rep = D + 'drc-report.txt'
pcbnew.WriteDRCReport(b, rep, pcbnew.EDA_UNITS_MILLIMETRES, True)
txt = open(rep).read()
print(re.findall(r'\*\* Found \d+ [^\n]*', txt))

# ---------- JLCPCB files ----------
os.makedirs(JLC, exist_ok=True)
g = JLC + 'gerbers/'
shutil.rmtree(g, ignore_errors=True); os.makedirs(g)
L = 'F.Cu,In1.Cu,In2.Cu,B.Cu,F.Paste,B.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts'
subprocess.run(['kicad-cli', 'pcb', 'export', 'gerbers', '--subtract-soldermask', '--no-x2', '-l', L, '-o', g, OUT], check=True, capture_output=True)
subprocess.run(['kicad-cli', 'pcb', 'export', 'drill', '--format', 'excellon', '--excellon-separate-th', '-o', g, OUT], check=True, capture_output=True)
zp = JLC + 'dbf-board-revB-gerbers'
if os.path.exists(zp + '.zip'): os.remove(zp + '.zip')
shutil.make_archive(zp, 'zip', g)

# assembly: factory places every SMD part; through-hole parts are hand-soldered
MPN = {
    'U2': 'ICM-42688-P', 'U3': 'DPS368XTSA1', 'U4': 'AP2112K-3.3TRG1', 'U6': 'SN74LVC157APWR', 'U7': 'SN74LVC157APWR',
    'U8': 'SN74LVC1G123DCUR', 'U9': 'SN74LVC1G07DCKR', 'Q1': 'MMBT3904', 'D1': 'SS24 (SMA)', 'D2': 'Green LED 0603',
    'D3': 'Red LED 0603', 'D4': '1N4148W (SOD-123)', 'SW1': 'TL3342F160QG', 'BZ1': 'CMT-8504-100-SMT-TR',
    'J4': 'SM04B-GHS-TB(LF)(SN)', 'J6': 'SM04B-GHS-TB(LF)(SN)', 'J11': 'SM04B-GHS-TB(LF)(SN)', 'J7': 'SM06B-GHS-TB(LF)(SN)',
}
VAL = {'C1': '10uF 25V X5R 0805', 'C2': '10uF 25V X5R 0805', 'C12': '2.2uF X7R 0603', 'C7': '0.47uF X7R 0603 (watchdog timing)', 'C5': '10nF X7R 0603',
       'R1': '10k', 'R2': '4.7k', 'R3': '4.7k', 'R4': '2.2k', 'R5': '2.2k', 'R6': '1k', 'R7': '1k', 'R8': '100k 1% (watchdog timing)', 'R12': '18R 0805',
       'R9': '10k', 'R10': '1k', 'R11': '100k'}
rows = []
for f in b.GetFootprints():
    ref = f.GetReference()
    if not any(p.GetAttribute() == pcbnew.PAD_ATTRIB_SMD for p in f.Pads()) or ref.startswith('TP'): continue
    if ref[0] in 'RC' and ref not in VAL: VAL[ref] = '100nF X7R 0603' if ref[0] == 'C' else f.GetValue()
    comment = MPN.get(ref) or VAL.get(ref) or f.GetValue()
    pos = f.GetPosition()
    rows.append((ref, comment, f.GetFPID().GetLibItemName().wx_str(), pcbnew.ToMM(pos.x), -pcbnew.ToMM(pos.y), f.GetOrientationDegrees() % 360))
rows.sort(key=lambda r: (r[0][0], int(re.sub(r'\D', '', r[0]) or 0)))
groups = {}
for r in rows: groups.setdefault((r[1], r[2]), []).append(r[0])
with open(JLC + 'bom-jlcpcb.csv', 'w', newline='') as fh:
    w = csv.writer(fh); w.writerow(['Comment', 'Designator', 'Footprint', 'LCSC Part #'])
    for (c, fpn), refs in groups.items(): w.writerow([c, ','.join(refs), fpn, ''])
with open(JLC + 'cpl-jlcpcb.csv', 'w', newline='') as fh:
    w = csv.writer(fh); w.writerow(['Designator', 'Mid X', 'Mid Y', 'Layer', 'Rotation'])
    for r in rows: w.writerow([r[0], '%.3fmm' % r[3], '%.3fmm' % r[4], 'Top', '%.0f' % r[5]])
print('BOM lines', len(groups), 'placements', len(rows))
