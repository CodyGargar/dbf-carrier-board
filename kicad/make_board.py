# Rev B board placement: logger + telemetry + stabilization with hardware failover.
# Regenerate: /usr/bin/python3 make_board.py   (KiCad 7 pcbnew)
import os, pcbnew, itertools
FP='/usr/share/kicad/footprints/'
W,H=86.0,66.0
OX,OY=100.0,100.0
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'dbf-carrier.kicad_pcb')
mm=lambda v: pcbnew.FromMM(v)
P=lambda x,y: pcbnew.VECTOR2I(mm(OX+x),mm(OY+y))
b=pcbnew.BOARD(); b.SetCopperLayerCount(4)
items=[]
def fp(lib,name,ref,val,x,y,rot=0):
    f=pcbnew.FootprintLoad(FP+lib+'.pretty',name)
    f.SetReference(ref); f.SetValue(val); b.Add(f)
    f.SetPosition(P(x,y)); f.SetOrientationDegrees(rot)
    f.Value().SetVisible(False); f.Reference().SetVisible(False)
    for it in f.GraphicalItems():
        if it.GetClass()=='PCB_TEXT': it.SetVisible(False)
    items.append(f); return f
def line(x1,y1,x2,y2,layer=pcbnew.Edge_Cuts,w=0.1):
    s=pcbnew.PCB_SHAPE(b); s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetStart(P(x1,y1)); s.SetEnd(P(x2,y2)); s.SetLayer(layer); s.SetWidth(mm(w)); b.Add(s)
def rect(x1,y1,x2,y2,layer=pcbnew.F_SilkS,w=0.15):
    for a in [(x1,y1,x2,y1),(x2,y1,x2,y2),(x2,y2,x1,y2),(x1,y2,x1,y1)]: line(*a,layer=layer,w=w)
def text(t,x,y,size=1.0,layer=pcbnew.F_SilkS,rot=0):
    s=pcbnew.PCB_TEXT(b); s.SetText(t); s.SetPosition(P(x,y)); s.SetLayer(layer)
    s.SetTextSize(pcbnew.VECTOR2I(mm(size),mm(size))); s.SetTextThickness(mm(size*0.15))
    s.SetTextAngleDegrees(rot); b.Add(s)
def circle(x,y,r,layer,w):
    c=pcbnew.PCB_SHAPE(b); c.SetShape(pcbnew.SHAPE_T_CIRCLE); c.SetCenter(P(x,y)); c.SetEnd(P(x+r,y)); c.SetLayer(layer); c.SetWidth(mm(w)); b.Add(c)

c=2.0
for a in [(c,0,W-c,0),(W,c,W,H-c),(W-c,H,c,H),(0,H-c,0,c),(0,c,c,0),(W-c,0,W,c),(W,H-c,W-c,H),(c,H,0,H-c)]: line(*a)
for i,(x,y) in enumerate([(3.5,3.5),(W-3.5,3.5),(3.5,H-3.5),(W-3.5,H-3.5)]):
    fp('MountingHole','MountingHole_3.2mm_M3','H%d'%(i+1),'M3',x,y)
    circle(x,y,3.0,pcbnew.F_SilkS,0.15); circle(x,y,1.6,pcbnew.Dwgs_User,0.3)

# Teensy 4.1 sockets
TX0,TY0=8.27,9.2
fp('Connector_PinSocket_2.54mm','PinSocket_1x24_P2.54mm_Vertical','J1','Teensy row A',TX0,TY0,90)
fp('Connector_PinSocket_2.54mm','PinSocket_1x24_P2.54mm_Vertical','J2','Teensy row B',TX0,TY0+15.24,90)
bx1,bx2=TX0-1.27,TX0+23*2.54+1.27; by1,by2=TY0+7.62-8.89,TY0+7.62+8.89
rect(bx1,by1,bx2,by2,pcbnew.F_SilkS,0.2)
text('TEENSY 4.1  (plugs in here)',(bx1+bx2)/2,TY0+7.62,1.5)
text('USB',bx1+3.2,TY0+4.2,1.0); text('microSD',bx2-5,TY0+4.2,1.0)

# power: 5V regulator module fed from the receiver bus, diode, 3.3V LDO
fp('Connector_PinHeader_2.54mm','PinHeader_1x03_P2.54mm_Vertical','U5','Pololu S7V7F5 5V reg',9.5,30.0,90)
text('5V REG',14.6,27.0,0.8)
fp('Diode_SMD','D_SMA','D1','SS24 Schottky',12.5,35,0)
fp('Package_TO_SOT_SMD','SOT-23-5','U4','AP2112K-3.3',12.5,39.5,0)
fp('Capacitor_SMD','C_0805_2012Metric','C1','10uF',9.3,39.5,90)
fp('Capacitor_SMD','C_0805_2012Metric','C2','10uF',15.7,39.5,90)
fp('Capacitor_SMD','C_0603_1608Metric','C3','100nF',12.5,42.4,0)

# sensors
fp('Package_LGA','Bosch_LGA-8_2x2.5mm_P0.65mm_ClockwisePinNumbering','U3','DPS368',22,35.5,0)
fp('Capacitor_SMD','C_0603_1608Metric','C6','100nF',22,38.3,0)
for i,(r,v) in enumerate([('R2','4.7k SDA'),('R3','4.7k SCL'),('R4','2.2k SDA1'),('R5','2.2k SCL1')]):
    fp('Resistor_SMD','R_0603_1608Metric',r,v,19.0+i*2.0,41.8,90)
text('BARO',23.6,31.4,0.9); text('(foam)',23.6,32.7,0.6)
fp('Package_LGA','Bosch_LGA-14_3x2.5mm_P0.5mm','U2','ICM-42688-P',33,37,0)
fp('Capacitor_SMD','C_0603_1608Metric','C4','100nF',30,35,90)
fp('Capacitor_SMD','C_0603_1608Metric','C5','100nF',36,35,90)
fp('Resistor_SMD','R_0603_1608Metric','R1','10k CS pull-up',33,40.4,0)
fp('Capacitor_SMD','C_0603_1608Metric','C12','2.2uF',36,38.2,90)
rect(28,31.8,38,42.8,pcbnew.F_SilkS,0.12); text('IMU',33,30.8,0.9)

# event button, LEDs, buzzer
fp('Button_Switch_SMD','SW_SPST_TL3342','SW1','Event button',43.5,33,0)
text('EVENT',43.5,29.2,0.8)
fp('LED_SMD','LED_0603_1608Metric','D2','GRN',42,38.6,0)
fp('LED_SMD','LED_0603_1608Metric','D3','RED',45.5,38.6,0)
fp('Resistor_SMD','R_0603_1608Metric','R6','1k',42,40.6,0)
fp('Resistor_SMD','R_0603_1608Metric','R7','1k',45.5,40.6,0)
text('LEDS',43.7,42.5,0.6)
fp('Buzzer_Beeper','MagneticBuzzer_CUI_CMT-8504-100-SMT','BZ1','Buzzer',57,33.5,0)
text('BUZZER',57,39.4,0.7)
fp('Package_TO_SOT_SMD','SOT-23','Q1','MMBT3904 NPN',51.5,42,0)
fp('Resistor_SMD','R_0603_1608Metric','R10','1k buzzer base',48.5,42.2,90)
fp('Diode_SMD','D_SOD-123','D4','1N4148W flyback',57,41.6,0)
fp('Resistor_SMD','R_0805_2012Metric','R12','18R buzzer current limit',50.3,30.0,90)

# connectors: left edge
fp('Connector_JST','JST_GH_SM06B-GHS-TB_1x06-1MP_P1.25mm_Horizontal','J7','Power module (sense only)',3.2,33.5,270)
text('BATT V/I',4.2,25.9,0.65)
fp('Connector_JST','JST_GH_SM04B-GHS-TB_1x04-1MP_P1.25mm_Horizontal','J4','Airspeed',3.2,45,270)
text('AIRSPD',4.2,39.6,0.65)
# right edge
fp('Connector_JST','JST_GH_SM04B-GHS-TB_1x04-1MP_P1.25mm_Horizontal','J6','RX CRSF',W-3.2,29,90)
text('RX CRSF',W-4.2,23.6,0.65)
fp('Connector_JST','JST_GH_SM04B-GHS-TB_1x04-1MP_P1.25mm_Horizontal','J11','Test radio (testing only)',W-3.2,41,90)
text('TEST RADIO',W-5.2,35.6,0.65)
fp('Connector_AMASS','AMASS_XT30U-M_1x02_P5.0mm_Vertical','J12','Rx battery in (from radio switch)',70.5,47.5,0)
text('RX BATT IN',73,43.4,0.7)

# servo blocks: 3 rows (signal, +, GND) x 8 channels
def servo_block(x0,y0,refbase,label):
    for i,row in enumerate(['S','+','-']):
        fp('Connector_PinHeader_2.54mm','PinHeader_1x08_P2.54mm_Vertical','%s%d'%(refbase,i+1),label+' '+row,x0,y0+i*2.54,90)
        text(row,x0-2.6,y0+i*2.54,0.8)
    rect(x0-1.27,y0-1.27,x0+7*2.54+1.27,y0+2*2.54+1.27,pcbnew.F_SilkS,0.15)
    text(label,x0+3.5*2.54,y0-2.6,0.9)
    for ch in range(8):
        text(['1','2','3','4','5','6','T','8'][ch],x0+ch*2.54,y0+3*2.54+0.9,0.75)
servo_block(10.5,55,'J2','FROM RECEIVER')
servo_block(54.5,55,'J3','TO SERVOS + ESC')
# failover: 2x quad 2:1 mux, watchdog one-shot, open-drain buffer for Castle Link Live throttle
fp('Package_SO','TSSOP-16_4.4x5mm_P0.65mm','U6','SN74LVC157A ch1-4',37.5,56.5,90)
fp('Package_SO','TSSOP-16_4.4x5mm_P0.65mm','U7','SN74LVC157A ch5-8',45.5,56.5,90)
fp('Package_SO','VSSOP-8_2.3x2mm_P0.5mm','U8','74LVC1G123 watchdog',41.5,46.0,0)
fp('Capacitor_SMD','C_0603_1608Metric','C7','watchdog RC',44.5,46.0,90)
fp('Resistor_SMD','R_0603_1608Metric','R8','watchdog RC',46.3,46.0,270)
fp('Package_TO_SOT_SMD','SOT-353_SC-70-5','U9','74LVC1G07 throttle open-drain',50.5,51,0)
fp('Resistor_SMD','R_0603_1608Metric','R9','10k throttle pull-up',53,51,90)
fp('Resistor_SMD','R_0603_1608Metric','R11','100k heartbeat pull-down',38.2,44.0,90)
fp('Capacitor_SMD','C_0603_1608Metric','C8','100nF',33.0,53.6,0)
fp('Capacitor_SMD','C_0603_1608Metric','C9','100nF',41.5,55.5,90)
fp('Capacitor_SMD','C_0603_1608Metric','C10','100nF',43.6,43.6,0)
fp('Capacitor_SMD','C_0603_1608Metric','C11','100nF',51.0,48.6,0)
text('FAILOVER',41.5,61.5,0.8)

# test points
for i,t in enumerate(['5V','VIN','3V3','GND','SDA','SCL']):
    x=21+i*3.3
    fp('TestPoint','TestPoint_Pad_D1.5mm','TP%d'%(i+1),t,x,47,0); text(t,x,48.9,0.6)

text('MIT DBF Logger + Stabilizer  Rev B',W/2,1.8,1.0)
exec(open(__file__.replace('make_board.py','netlist.py')).read())
pcbnew.SaveBoard(OUT,b)

def cy(f):
    sh=f.GetCourtyard(pcbnew.F_CrtYd)
    bb=sh.BBox() if sh.OutlineCount() else f.GetBoundingBox(False,False)
    return (pcbnew.ToMM(bb.GetLeft())-OX,pcbnew.ToMM(bb.GetTop())-OY,pcbnew.ToMM(bb.GetRight())-OX,pcbnew.ToMM(bb.GetBottom())-OY)
for a,c2 in itertools.combinations(items,2):
    A,B=cy(a),cy(c2)
    if A[0]<B[2] and B[0]<A[2] and A[1]<B[3] and B[1]<A[3]:
        print('OVERLAP',a.GetReference(),c2.GetReference(),[round(v,1) for v in A],[round(v,1) for v in B])
for f in items:
    x1,y1,x2,y2=cy(f)
    if x1<-0.5 or y1<-0.5 or x2>W+0.5 or y2>H+0.5: print('EDGE',f.GetReference(),[round(v,1) for v in (x1,y1,x2,y2)])
