# Carrier board vs. DBF 2026-27 rules draft

Source: https://aiaa.org/wp-content/uploads/2026/09/DBF-2027-Rules-Draft.pdf (draft, read 2026-10-17).
Quotes below are from the draft. The FAQ was checked for electronics rulings; the only one is how to disable an ESC's BEC.

## Not allowed: must change

| Board feature | Rule | Fix |
|---|---|---|
| GPS + compass module (Matek M10Q-5883) | §3.2.1 "No onboard GPS systems are allowed." Also checked at tech inspection (§4.2.1). | Remove the GPS module, its connector and Serial1 wiring. Airspeed + baro + IMU still give speed, altitude and attitude. |
| "Mode B": Teensy drives the servos/ESC | §3.2.1 "No autopilots/flight controllers are allowed under any circumstances, even in manual mode." Inspectors look for flight controllers (§4.2.1). | Teensy must only log and send telemetry ("Mode A"). Servos and ESC plug into the receiver. Recommend removing the servo/ESC output headers so the board can't be mistaken for a flight controller. |
| Separate telemetry radio option (SiK on Serial5) | §3.2.1 "Telemetry systems using stand-alone transmitters and receivers or ground stations are not allowed." | Drop the SiK radio and the telemetry connector. Telemetry through the ELRS receiver to the pilot's radio is explicitly allowed. |
| Servo/receiver power from a UBEC on the propulsion battery, avionics 5 V from the power module | §3.2.3 "A separate battery is required for the Rx/Servos on the airplane." and "If the ESC has a Battery Eliminator Circuit (BEC), it must be disabled." | Power the receiver, servos and the carrier board from a separate receiver battery, through the required external radio switch. The power module may only sense; its 5 V output is not used. Phoenix Edge 100 (5 A BEC): the board's T column + pin is unconnected, and the red wire is pulled from the ESC's throttle plug. |

## Allowed: keep

| Board feature | Rule |
|---|---|
| Logging to the Teensy's microSD | §3.2.1 "On-board data recording systems without the ability to transmit or receive radio frequency signals are allowed." The Teensy 4.1 has no radio. |
| Telemetry to the pilot's radio through ELRS | §3.2.1 "Telemetry data transmitted via the receiver to the pilot's RC controller are allowed." |
| ExpressLRS 2.4 GHz receiver | §3.2.1 commercially available, fail-safe capable, legal US frequency (2.4 GHz listed). |
| IMU, barometer, airspeed sensor | No rule against sensors; only GPS and cameras are named as illegal. |

## Rules the build must also meet

- **External radio switch** (§3.2.1): externally accessible, not under a hatch, separate from the arming plug. The carrier board should be powered through it.
- **Fully insulated wiring** (§3.2.1): "no visible wires or exposed surfaces which may conduct electricity." Put the board in an enclosure or shrink-wrap it, and cover exposed pins and test points.
- **Fail-safe** (§4.2.5): with the transmitter off, throttle closed, full up elevator, full right rudder, full right aileron, full flaps down. Set this in the ELRS receiver; it no longer depends on the Teensy.
- **Propulsion system** (§3.2.3.1, §3.2.2): one battery, one blade fuse in a separate harness, one external arming plug on the top surface, at least 6 in from the propeller, on the + wire between fuse and ESC. None of this is on the carrier board. The board's ARM button is only a software status button, not the arming plug.
- **Battery** (§3.2.3): unaltered COTS packs, 100 Wh max total propulsion energy, fuse rating up to 100 A.

## Grey area: ask the organizers

- **Current sensor in the propulsion line.** The propulsion system is defined as battery, fuse, arming plug, ESC(s) and motor(s) (§3.2.3.1). The rules don't mention a current sensor or power module inline. Options: ask in the official Q&A, or read current from ESC telemetry instead (no extra part in the propulsion wiring).
- **Custom board that only logs.** Logging is allowed, but an inspector may still ask about a board with a microcontroller wired to the receiver. Removing the servo outputs and bringing a one-page explanation to tech inspection makes this easy. Asking in the Q&A ahead of time is safest.

---

## Clarifications from last year's Q&A (2025-26 DBF Q&A #2)

Source: https://aiaa.org/wp-content/uploads/2026/01/QA-2.pdf (read through a web reader on 2026-10-17). These answers were for the 2025-26 rules, so confirm them again in the 2026-27 Q&A.

| Q | Question (short) | Answer (quoted) | What it means for this board |
|---|---|---|---|
| 5 | Are microcontrollers allowed for on-board data recording or flight stabilization, just no COTS flight controllers or GPS? | "Microcontrollers may be used in flight stabilization and data collection sub-systems as long as this can be verified in tech inspection." | The logger is clearly allowed. A **custom** Teensy stabilization system was also allowed last year, but a commercial flight controller was not. Bring code and wiring to tech inspection so they can verify what it does. |
| 6 | Is telemetry broadcasting allowed? | "Telemetry may only be broadcast between the airplane receiver and RC controller." | Matches our design: telemetry goes out only through the ELRS receiver. |
| 19 | Must the receiver battery switch follow the motor fuse placement rules? | "No." | The external radio switch can go where it is convenient. |
| (unnumbered) | Must the propulsion fuse housing be COTS? | "No." | Not board related. |

Nothing in that Q&A covers inline current sensors or power modules, so that question is still open.
