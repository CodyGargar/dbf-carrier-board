# Rev B connections (netlist). Executed by make_board.py after placement; `b` is the board.
# Pin maps checked against datasheets: see ../design-spec.md section "Pin sources".

# Teensy 4.1 edge pins, from the USB end. Row A = J1 (top edge of the board), row B = J2.
ROW_A = ['VIN', 'GND', '3V3', 23, 22, 21, 20, 19, 18, 17, 16, 15, 14, 13, 'GND', 41, 40, 39, 38, 37, 36, 35, 34, 33]
ROW_B = ['GND', 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, '3V3', 24, 25, 26, 27, 28, 29, 30, 31, 32]
def T(pin):
    for ref, row in (('J1', ROW_A), ('J2', ROW_B)):
        if pin in row: return (ref, str(row.index(pin) + 1))
    raise KeyError(pin)

# Pololu S7V7F5 header order (U5 pads 1..4)
U5_PINS = {'VIN': '1', 'GND': '2', 'VOUT': '3'}   # 3-pin module; order VIN-GND-VOUT to confirm on the module silkscreen
# SN74LVC1G123 (DCU): 1 A, 2 B, 3 CLR, 4 GND, 5 Q, 6 Cext, 7 Rext/Cext, 8 VCC
# SN74LVC157A (PW): 1 A/B, 2 1A, 3 1B, 4 1Y, 5 2A, 6 2B, 7 2Y, 8 GND, 9 3Y, 10 3B, 11 3A, 12 4Y, 13 4B, 14 4A, 15 G, 16 VCC
MUX = [('1', '2', '3', '4'), ('2', '5', '6', '7'), ('3', '11', '10', '9'), ('4', '14', '13', '12')]  # section, A, B, Y
# ICM-42688-P: 1 SDO, 4 INT1, 5 VDDIO, 6 GND, 8 VDD, 9 FSYNC, 12 CS, 13 SCLK, 14 SDI; 2,3,10,11 NC, 7 RESV->GND
# DPS368: 1 GND, 2 CSB, 3 SDI, 4 SCK, 5 SDO, 6 VDDIO, 7 GND, 8 VDD
# Buzzer CMT-8504-100-SMT: KiCad Fab layer marks pad 1 as +; pads 3/4 are dummy pads
BZ_POS, BZ_NEG = '1', '2'

NETS = {
    'GND': [('U5', U5_PINS['GND']), ('J12', '1'), ('U4', '2'), ('C1', '2'), ('C2', '2'), ('C3', '2'),
            ('U2', '6'), ('U2', '7'), ('U2', '9'), ('C4', '2'), ('C5', '2'), ('C12', '2'),
            ('U3', '1'), ('U3', '7'), ('U3', '5'), ('C6', '2'),
            ('U6', '8'), ('U6', '15'), ('U7', '8'), ('U7', '15'), ('C8', '1'), ('C9', '2'),
            ('U8', '4'), ('U8', '1'), ('C10', '2'), ('R11', '2'), ('U9', '3'), ('C11', '1'),
            ('SW1', '2'), ('D2', '1'), ('D3', '1'), ('Q1', '2'),
            ('J4', '4'), ('J6', '4'), ('J11', '4'), ('J7', '5'), ('J7', '6'), ('TP4', '1')]
           + [('J23', str(i)) for i in range(1, 9)] + [('J33', str(i)) for i in range(1, 9)],
    'VSERVO': [('J12', '2'), ('U5', U5_PINS['VIN'])]
              + [('J22', str(i)) for i in range(1, 9)] + [('J32', str(i)) for i in range(1, 9)],
    '+5V': [('U5', U5_PINS['VOUT']), ('D1', '2'), ('TP1', '1')],
    'VIN': [T('VIN'), ('D1', '1'), ('U4', '1'), ('U4', '3'), ('C1', '1'), ('J4', '1'), ('J11', '1'),
            ('R12', '1'), ('TP2', '1')],
    'BUZ_P': [('R12', '2'), ('BZ1', BZ_POS), ('D4', '1')],
    '+3V3S': [('U4', '5'), ('C2', '1'), ('C3', '1'), ('U2', '5'), ('U2', '8'), ('C4', '1'), ('C5', '1'), ('C12', '1'),
              ('U3', '2'), ('U3', '6'), ('U3', '8'), ('C6', '1'), ('R1', '2'), ('R2', '2'), ('R3', '2'), ('R4', '2'), ('R5', '2'),
              ('U6', '16'), ('U7', '16'), ('C8', '2'), ('C9', '1'), ('U8', '8'), ('U8', '3'), ('C10', '1'), ('R8', '2'),
              ('U9', '5'), ('C11', '2'), ('R9', '2'), ('TP3', '1')],
    # sensors
    'SDA': [T(18), ('U3', '3'), ('R2', '1'), ('TP5', '1')],
    'SCL': [T(19), ('U3', '4'), ('R3', '1'), ('TP6', '1')],
    'SDA1': [T(17), ('J4', '3'), ('R4', '1')],
    'SCL1': [T(16), ('J4', '2'), ('R5', '1')],
    'IMU_CS': [T(10), ('U2', '12'), ('R1', '1')],
    'IMU_SCK': [T(13), ('U2', '13')],
    'IMU_MOSI': [T(11), ('U2', '14')],
    'IMU_MISO': [T(12), ('U2', '1')],
    'IMU_INT': [T(30), ('U2', '4')],
    # radios
    'CRSF_TX': [T(14), ('J6', '2')],
    'CRSF_RX': [T(15), ('J6', '3')],
    'TEL_TX': [T(1), ('J11', '2')],
    'TEL_RX': [T(0), ('J11', '3')],
    # analog battery sense from the optional power module
    'BATT_I': [T(41), ('J7', '3')],
    'BATT_V': [T(40), ('J7', '4')],
    # button, LEDs, buzzer
    'BTN': [T(32), ('SW1', '1')],
    'LED_G': [T(36), ('R6', '1')], 'LED_G_A': [('R6', '2'), ('D2', '2')],
    'LED_R': [T(37), ('R7', '1')], 'LED_R_A': [('R7', '2'), ('D3', '2')],
    'BUZ': [T(33), ('R10', '1')], 'BUZ_B': [('R10', '2'), ('Q1', '1')],
    'BUZ_C': [('Q1', '3'), ('BZ1', BZ_NEG), ('D4', '2')],
    # failover watchdog
    'HEARTBEAT': [T(24), ('U8', '2'), ('R11', '1')],
    'TEENSY_OK': [T(25), ('U8', '5'), ('U6', '1'), ('U7', '1')],
    'WD_C': [('U8', '6'), ('C7', '1')],
    'WD_RC': [('U8', '7'), ('C7', '2'), ('R8', '1')],
    # Castle Link Live: mux throttle -> open-drain buffer -> ESC lead, pulled up, read on pin 28
    'THR_MUX': [('U7', '9'), ('U9', '2')],
    'OUT_T': [('U9', '4'), ('R9', '1'), ('J31', '7'), T(28)],
}
# 8 channels: (receiver pin col, teensy pin, mux ref, section)
CH = [(1, 2, 'U6', 0), (2, 3, 'U6', 1), (3, 4, 'U6', 2), (4, 5, 'U6', 3),
      (5, 6, 'U7', 0), (6, 9, 'U7', 1), (7, 22, 'U7', 2), (8, 23, 'U7', 3)]
LBL = ['1', '2', '3', '4', '5', '6', 'T', '8']
for col, tp, u, sec in CH:
    _, a, bb, y = MUX[sec]
    NETS['RX_CH' + LBL[col - 1]] = [('J21', str(col)), (u, a)]
    NETS['PWM_CH' + LBL[col - 1]] = [T(tp), (u, bb)]
    if LBL[col - 1] != 'T':
        NETS['OUT_CH' + LBL[col - 1]] = [(u, y), ('J31', str(col))]
assert NETS['THR_MUX'][0] == ('U7', MUX[2][3])
# Teensy GND pins on both rows
NETS['GND'] += [('J1', '2'), ('J1', '15'), ('J2', '1')]

_fps = {f.GetReference(): f for f in b.GetFootprints()}
_seen = {}
for name, pins in NETS.items():
    ni = pcbnew.NETINFO_ITEM(b, name); b.Add(ni)
    for ref, num in pins:
        key = (ref, num)
        assert key not in _seen, (key, name, _seen.get(key))
        _seen[key] = name
        hit = [p for p in _fps[ref].Pads() if p.GetNumber() == num]
        assert hit, (ref, num)
        for p in hit:
            p.SetNet(ni)
            # big servo/battery current: solid plane connection, no thermal spokes
            if ref in ('J12', 'J22', 'J23', 'J32', 'J33'):
                p.SetZoneConnection(pcbnew.ZONE_CONNECTION_FULL)
print('nets:', len(NETS), 'pins:', len(_seen))
