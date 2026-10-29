# DBF Logger + Stabilizer board, Rev B

A custom PCB that a **Teensy 4.1** plugs into. It does three things:

1. **Auto-stabilizes** the plane. The Teensy reads the gyro and adds small corrections to the pilot's commands on 6 control servos.
2. **Sends telemetry to the pilot's radio** through the ELRS receiver, and to a laptop over USB on the bench (or an optional test radio during test flights).
3. **Logs every flight** to microSD.

The pilot always flies the plane. If the Teensy freezes, or the pilot flips stabilization off, a **hardware failover switch** hands every servo and the throttle straight back to the receiver.

Rules basis: last year's Q&A Q5 allowed custom microcontrollers in "flight stabilization and data collection sub-systems as long as this can be verified in tech inspection". The 2027 draft bans flight controllers but allows stabilization systems. **Confirm in this year's Q&A.** See [rules-check-2027.md](rules-check-2027.md).

Companion files: [pinout.csv](pinout.csv), [module-menu.md](module-menu.md), [bom.csv](bom.csv), [parts-list.xlsx](parts-list.xlsx), [kicad/](kicad/) (routed board), [jlcpcb/](jlcpcb/) (order files).

---

## 1. Hardware it works with

| Item | Model | Notes |
|---|---|---|
| ESC | Castle Creations Phoenix Edge Lite 100 | Telemetry over the throttle wire (Castle Link Live): voltage, current, mAh, RPM, temperature. Turn Link Live on and disable the BEC with a Castle Link USB adapter. |
| Receiver | RadioMaster ER-series ELRS PWM receiver (ER8 assumed) | 8 PWM outputs plus a 4-pin CRSF port. The board needs 7 backup channels (6 surfaces + throttle) and the 2 drop servos need 1, so an **ER8** fits only if both drop servos share one channel with a Y-cable. An ER6 is too small. |
| Servos | 6 control servos on the board, 2 drop servos on the receiver | |

## 2. How it connects

Full diagram: [wiring/avionics-wiring.png](wiring/avionics-wiring.png) (SVG alongside for editing).

```
 RECEIVER BATTERY ─► external radio switch ─► XT30 "RX BATT IN" on the board
                                                 │ (servo power rail on the board)
                                                 ├─► servo + pins (both header blocks)
                                                 ├─► receiver power, through its servo leads
                                                 └─► 5 V regulator ─► Teensy, sensors

 ELRS RECEIVER ── CRSF cable ─────────────► board (sticks in, telemetry out)
               ── PWM ch1-6 + throttle ───► board "FROM RECEIVER" header (backup signals)
               ── ch8 ─► 2 drop servos (Y-cable), not through the board

 board "TO SERVOS + ESC" header ─► 6 control servos + ESC throttle lead (ch T)

 MOTOR BATTERY ─► fuse ─► arming plug ─► ESC ─► motor      (never touches the board)
```

**Two batteries, required by the 2027 rules (3.2.3):** the motor pack runs only the
motor. The receiver pack runs the receiver, the board and every servo. The ESC's
BEC is disabled.

## 3. Failover switch (the safety part)

- Two **SN74LVC157A** chips (4 channels each) choose, for each of the 8 outputs, either the Teensy's signal or the receiver's signal.
- A **74LVC1G123** watchdog timer makes that choice. The Teensy toggles a heartbeat pin from its main loop. If the toggling stops for about 50 ms, the watchdog flips every channel back to the receiver.
- The Teensy **stops the heartbeat on purpose** when the pilot's stabilization switch is off, when the radio link is lost, or when a sensor fails. So manual mode and the required fail-safe positions always come from the receiver, never from our code.
- The Teensy reads the watchdog output (pin 25), so it knows who is in control and can log it.

## 4. ESC telemetry (Castle Link Live)

The Phoenix Edge Lite answers each throttle pulse with a short reply on the same
wire. The throttle channel goes through an open-drain buffer (74LVC1G07) with a 10k
pull-up, and the Teensy times the replies on pin 28. That gives voltage, current,
mAh, RPM and temperature with no extra sensor in the motor wiring.

To confirm on the bench before routing: the exact Link Live timing, and that the
ESC accepts a 3.3 V pull-up. The optional power-module input stays as a backup.

## 5. Power plan

| Rail | Source | Feeds |
|---|---|---|
| Servo rail | Receiver battery through the XT30 (2S LiFe, 6.6 V, suggested) | Servos, receiver; wide copper |
| 5 V | Pololu S7V7F5 module (2.7 to 11.8 V in) | Teensy VIN (through a Schottky diode), airspeed sensor |
| 3V3_SENS | AP2112K-3.3 LDO | IMU, barometer, muxes, watchdog |

USB on the bench powers the Teensy and sensors with no battery. The diode stops USB
from back-feeding. The servos need the receiver battery.

## 6. Pins

Full table: [pinout.csv](pinout.csv). Servo outputs are on pins 2, 3, 4, 5, 6 and 9, throttle on 22, a spare on 23, the heartbeat on 24 and the status input on 25. The sensors, CRSF and analog inputs are unchanged from Rev A. The test radio uses Serial1 (pins 0 and 1).

## 7. Connectors

- **XT30 RX BATT IN:** receiver battery, from the external radio switch.
- **FROM RECEIVER (3×8 header):** signal, +, GND for channels 1 to 6, T, 8.
- **TO SERVOS + ESC (3×8 header):** same order. The ESC throttle lead goes on T.
- **JST-GH:** RX CRSF (4-pin), airspeed (4-pin), test radio (4-pin, testing only), battery V/I (6-pin, optional).

## 8. Event button

- **Hold at power-up:** calibrate the gyro and zero the airspeed sensor (plane still, on the ground).
- **Tap on the ground:** start or stop a log, or drop a marker ("test 3 starts now").
- **In flight**, use a switch on the radio to drop markers. The Teensy reads it over CRSF.

## 9. Layout

Routed board: [kicad/board-top.png](kicad/board-top.png), 86 × 66 mm, 4 layers, four M3 holes.
Teensy across the top. Regulator, barometer, IMU, button, LEDs and buzzer in the middle.
Servo headers along the bottom, with the failover chips between them. Connectors on the left and right edges.
Layers: top and bottom carry the signals, inner layer 1 is a solid ground plane, inner layer 2 is the servo power plane (a few signals cross it). Signal traces are 0.2 mm, the 5 V and VIN feeds 0.5 mm, the 3.3 V feed 0.3 mm, vias 0.6/0.3 mm, clearance 0.15 mm or more. The battery and servo header pins connect solidly to the planes for current.
Connections are defined in [kicad/netlist.py](kicad/netlist.py). There is no separate schematic drawing; the netlist file is the schematic.
Regenerate: `make_board.py` (placement + connections) → `route_board.py` (traces) → `finish_board.py` (planes, design check, JLCPCB files).
Put the board in a case: no exposed wiring is allowed.

**Small parts added during routing:** R10 1k (buzzer transistor base), R12 18 Ω (limits buzzer current to about 150 mA), D4 1N4148W (buzzer flyback), R11 100k (holds the heartbeat low while the Teensy boots, so the receiver keeps control), C8 to C11 100 nF (one per logic chip), C12 2.2 µF (IMU). Watchdog timing is R8 100k with C7 0.47 µF, about 47 ms.

**Pin sources:** TI SN74LVC157A (SCAS292S), SN74LVC1G123 (SCES586E), SN74LVC1G07 (SCES296AG), Diodes AP2112K (DS39724), TDK ICM-42688-P (DS-000347), Infineon DPS368, PJRC Teensy 4.1 pinout card, Holybro PM02 and Matek ASPD-4525 port docs. The Pololu S7V7F5 has 3 pins, not 4.

**USB plus battery:** the Teensy joins VIN and USB power. When the receiver battery is on and the laptop is plugged in, the board's 5 V can feed back into the laptop's USB port. That is usually harmless, but PJRC recommends cutting the VIN/VUSB pads on the Teensy's underside if both will often be connected.

## 10. Bring-up order

1. Board without a Teensy: put power on the XT30 from a bench supply (current-limited). Check the 5 V and 3.3 V test points. Confirm the receiver's PWM passes straight through to the servo outputs (watchdog off = receiver in control).
2. Teensy on USB: scan the sensors, read the IMU.
3. CRSF: sticks in, test telemetry on the radio.
4. Heartbeat on: the Teensy drives the servos. Stop the code and confirm the receiver takes over within about 50 ms.
5. Castle Link Live on the bench with **props off**.
6. First flights with stabilization off (logging only), then turn it on at a safe altitude.

## 11. Next steps

1. Ask this year's Q&A to confirm that custom stabilization and the inline current sensor are allowed.
2. Confirm the receiver model (ER8) and how the drop servos are wired.
3. Check the pin orders listed in README.md, then order from JLCPCB (see jlcpcb/ORDERING.md).
