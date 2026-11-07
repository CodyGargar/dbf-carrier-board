# Full avionics wiring diagram for the DBF Logger + Stabilizer (Rev B). Writes SVG + PNG.
W,H=1920,1080
out=[]
def box(x,y,w,h,title,sub='',fill='#FFFFFF',stroke='#10241A',tc='#10241A',sc='#45524A',r=14,tw=24,sw=17,lw=3):
    out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{lw}"/>')
    lines=sub.split('|') if sub else []
    ty=y+h/2-(len(lines)*sw*1.25)/2
    out.append(f'<text x="{x+w/2}" y="{ty}" font-size="{tw}" font-weight="700" fill="{tc}" text-anchor="middle" dominant-baseline="central">{title}</text>')
    for i,l in enumerate(lines):
        out.append(f'<text x="{x+w/2}" y="{ty+tw*0.9+i*sw*1.25}" font-size="{sw}" fill="{sc}" text-anchor="middle" dominant-baseline="central">{l}</text>')
def wire(pts,color,w=5,dash=None,arrow=True,start=False):
    d='M'+' L'.join(f'{x} {y}' for x,y in pts)
    da=f' stroke-dasharray="{dash}"' if dash else ''
    me=f' marker-end="url(#a_{color[1:]})"' if arrow else ''
    ms=f' marker-start="url(#a_{color[1:]})"' if start else ''
    out.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w}"{da}{me}{ms} stroke-linejoin="round"/>')
def label(x,y,t,c='#45524A',s=17,anchor='start',bold=False):
    out.append(f'<text x="{x}" y="{y}" font-size="{s}" fill="{c}" text-anchor="{anchor}" font-weight="{700 if bold else 400}">{t}</text>')
PWR_M='#C2572B'; PWR_R='#2E7D52'; SIG='#2B5FA8'; DATA='#7A4FB0'; RF='#8A6418'
cols=[PWR_M,PWR_R,SIG,DATA,RF]
defs=''.join(f'<marker id="a_{c[1:]}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="{c}"/></marker>' for c in cols)
# title
label(60,70,'MIT DBF 2027 · Avionics wiring with the Logger + Stabilizer board (Rev B)',c='#10241A',s=36,bold=True)
label(60,108,'Two separate batteries (rules 3.2.3). The pilot always flies; the board adds gyro corrections and hands control back to the receiver on any fault.',s=20)
# --- propulsion row (bottom)
label(60,880,'PROPULSION SIDE: motor battery only',c=PWR_M,s=20,bold=True)
py=905; ph=110
box(60,py,250,ph,'8S LiPo 29.6 V','≤ 100 Wh propulsion pack',stroke=PWR_M)
box(380,py,200,ph,'Fuse','≤ 100 A',stroke=PWR_M)
box(650,py,220,ph,'Arming plug','external, separate|from radio switch',stroke=PWR_M)
box(930,py,370,ph,'Castle Phoenix Edge 100','34 V max · BEC red wire pulled|Link Live telemetry ON',stroke=PWR_M,tw=22)
box(1370,py,220,ph,'Main motor','~500 kV',stroke=PWR_M)
for a,b in [(310,380),(580,650),(870,930),(1300,1370)]: wire([(a,py+ph/2),(b-4,py+ph/2)],PWR_M,w=8)
# --- receiver battery + switch (left)
label(60,170,'RECEIVER SIDE: separate receiver battery',c=PWR_R,s=20,bold=True)
box(60,530,250,100,'Receiver battery','2S LiFe 6.6 V (suggested)',stroke=PWR_R)
box(60,700,250,110,'External radio switch','on the fuselage skin',stroke=PWR_R)
wire([(185,630),(185,696)],PWR_R,w=7)
# --- pilot radio + laptop
box(60,195,250,110,'Pilot’s radio','EdgeTX, ELRS 2.4 GHz|shows telemetry + alarms',stroke=RF)
box(60,360,250,110,'Laptop','USB on the bench|(test radio for test flights)',stroke='#6A756E')
# --- receiver
box(470,195,330,150,'RadioMaster ER8','ELRS PWM receiver|8 PWM outputs + CRSF port|fail-safe positions set here',stroke=SIG)
wire([(314,250),(466,250)],RF,w=4,dash='12 8',start=True)
label(322,236,'2.4 GHz link',c=RF,s=16); label(322,276,'sticks / telemetry',c=RF,s=16)
# --- the board
bx,by,bw,bh=560,430,640,400
out.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="22" fill="#10241A"/>')
label(bx+30,by+44,'OUR BOARD',c='#D9AE55',s=22,anchor='start',bold=True); label(bx+bw-30,by+44,'Logger + Stabilizer, Rev B',c='#F4F2EA',s=22,anchor='end',bold=True)
def ib(x,y,w,h,t,s): box(x,y,w,h,t,s,fill='#1C3A2A',stroke='#D9AE55',tc='#F4F2EA',sc='#BFD3C6',tw=20,sw=15,lw=2)
ib(bx+30,by+70,280,100,'Teensy 4.1','stabilization code|microSD flight log')
ib(bx+330,by+70,280,100,'IMU + barometer','gyro/accel ICM-42688-P|altitude DPS368')
ib(bx+30,by+190,280,90,'5 V + 3.3 V regulators','fed from the XT30 rail')
ib(bx+330,by+190,280,90,'Failover switch','2× mux + watchdog|→ receiver in ~50 ms')
ib(bx+30,by+300,180,80,'XT30 in','receiver battery')
ib(bx+230,by+300,180,80,'FROM RX','7 backup PWM')
ib(bx+430,by+300,180,80,'TO SERVOS','6 servos + T')
# switch -> XT30 (power)
wire([(310,770),(bx+26,770)],PWR_R,w=7)
label(330,758,'6.6 V receiver power',c=PWR_R,s=17)
# receiver CRSF to board
wire([(600,345),(600,426)],DATA,w=5,start=True)
label(610,395,'CRSF (JST-GH)',c=DATA,s=17)
# receiver PWM backup to board FROM RX
wire([(760,345),(760,400),(bx+320,400),(bx+320,by+296)],SIG,w=5)
label(770,395,'7 PWM leads (ch 1–6 + T)',c=SIG,s=17)
# laptop USB
wire([(314,415),(500,415),(500,520),(bx+26,520)],DATA,w=4,dash='8 6',start=True)
label(330,404,'USB',c=DATA,s=17)
# --- servos (right)
label(1290,170,'CONTROL SURFACES (through the board)',c=SIG,s=20,bold=True)
names=[('Left aileron','ch 1'),('Right aileron','ch 2'),('Elevator','ch 3'),('Rudder','ch 4'),('Left flap','ch 5'),('Right flap','ch 6')]
for i,(n,c) in enumerate(names):
    yy=195+i*78
    box(1500,yy,300,62,n,c,stroke=SIG,tw=20,sw=15)
    wire([(1240,yy+31),(1496,yy+31)],SIG,w=3)
wire([(bx+bw-30,by+340),(1240,by+340),(1240,195+31)],SIG,w=5,arrow=False)
label(1250,690,'signal + Rx power',c=SIG,s=17)
# throttle from board to ESC
wire([(bx+bw-110,by+bh),(bx+bw-110,870),(1105,870),(1105,py-4)],SIG,w=5,start=True)
label(1115,862,'throttle (T) + Castle Link Live telemetry back',c=SIG,s=17)
# mission servos on receiver ch8
box(870,195,330,110,'Mission servos (×2)','sensor deploy / winch|receiver ch 8 via Y-cable',stroke=SIG,tw=20,sw=15)
wire([(800,250),(866,250)],SIG,w=4)
# airspeed
box(1290,750,240,95,'Airspeed','Matek ASPD-4525 + pitot',stroke=DATA,tw=20,sw=15)
wire([(bx+bw+4,805),(1286,805)],DATA,w=4,start=True)
label(1208,826,'JST-GH',c=DATA,s=15)
# legend
lx,ly=1590,700
items=[(PWR_M,'Motor power (thick)',None),(PWR_R,'Receiver-battery power',None),(SIG,'Servo / throttle signal',None),(DATA,'Sensor / data link',None),(RF,'Radio link (wireless)','12 8')]
out.append(f'<rect x="{lx-20}" y="{ly-30}" width="330" height="{len(items)*36+30}" rx="12" fill="#FFFFFF" stroke="#DEDBCF" stroke-width="2"/>')
for i,(c,t,d) in enumerate(items):
    yy=ly+i*36
    wire([(lx,yy),(lx+50,yy)],c,w=5,dash=d,arrow=False); label(lx+64,yy+6,t,s=17)
svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Helvetica, Arial, sans-serif"><defs>{defs}</defs><rect width="{W}" height="{H}" fill="#F6F5EF"/>'+''.join(out)+'</svg>'
import sys
open(sys.argv[1]+'.svg','w').write(svg)
import cairosvg; cairosvg.svg2png(bytestring=svg.encode(),write_to=sys.argv[1]+'.png',output_width=1920)
