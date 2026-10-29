# Board module menu (pick what you want)

For the new goals: auto-stabilize, telemetry to the hand-held radio, and a laptop link for testing.
Mark each row **Keep** or **Drop**. "Needed" means the goals above don't work without it.

## On the board today

| # | Module | What it does | Status |
|---|---|---|---|
| 1 | Teensy 4.1 | The brain. Runs stabilization, logging, telemetry. Built-in microSD for flight logs | Needed |
| 2 | ICM-42688-P IMU (gyro + accelerometer) | Senses roll, pitch, yaw rates. This is what stabilization reacts to | Needed |
| 3 | 5 V regulator (Pololu S7V7F5) + 3.3 V regulator | Powers the Teensy and sensors from the receiver battery | Needed |
| 4 | ELRS receiver (RadioMaster ER8), off board | Gets your sticks over CRSF and sends telemetry back to the radio | Needed |
| 5 | DPS368 barometer | Altitude and climb rate on the radio and in the log | Optional (cheap, ~$4) |
| 6 | Matek ASPD-4525 airspeed + pitot, off board | Airspeed on the radio; lets stabilization soften at high speed | Optional, recommended |
| 7 | ESC telemetry (Castle Link Live) | Battery voltage, current, mAh, RPM and temperature from the Castle ESC, read over the throttle wire | Kept |
| 8 | Holybro PM02 power module, off board | Battery voltage and current if the ESC can't report it. Sits in the motor wiring (rules gray area) | Optional, ask the Q&A |
| 9 | Event button | Marks a moment in the log | Optional |
| 10 | Buzzer + 2 LEDs | Status (armed, SD card OK, stabilization on) and lost-plane finder | Optional |

## Would be added back for stabilization

| # | Module | What it does | Status |
|---|---|---|---|
| 11 | 4 servo headers | Ailerons (x2), elevator, rudder plug into the board so the Teensy can correct them | Needed for stabilization |
| 12 | Hardware failover switch (mux chip) | If the Teensy freezes, hands those 4 servos straight back to the receiver | Strongly recommended |
| 13 | Test telemetry radio port (SiK 915 MHz or ESP32 Wi-Fi) | Live data on a laptop during test flights. **Unplug it for competition**: stand-alone telemetry radios are banned there | Optional, testing only |

USB to the laptop on the bench (coding, live sensor readout, log download) needs no extra part: it's the Teensy's own USB port.

## Not allowed or not needed

| Module | Why not |
|---|---|
| GPS | Banned by the 2027 rules |
| Compass | Only useful with GPS navigation |
| Throttle control from the board | Keep throttle on the receiver so the required fail-safe (throttle closed) never depends on our code |
