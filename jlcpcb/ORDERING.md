# Ordering the Rev B board from JLCPCB

Files in this folder:
- **dbf-board-revB-gerbers.zip**: the board itself (4 copper layers, mask, silkscreen, paste, outline, drill).
- **bom-jlcpcb.csv**: the parts JLCPCB solders (every surface-mount part).
- **cpl-jlcpcb.csv**: where each of those parts sits and which way it is turned.

## Steps
1. On jlcpcb.com, click **Order now** and upload `dbf-board-revB-gerbers.zip`. It should read **86 × 66 mm, 4 layers**.
2. Board options: thickness 1.6 mm, **any color**, lead-free HASL or ENIG, 5 boards. Inner copper 1 oz is worth the small extra if offered (the servo current runs on an inner layer).
3. Turn on **PCB Assembly**, top side, Economic if it allows every part, otherwise Standard. Assemble 2 of the 5.
4. Upload `bom-jlcpcb.csv` and `cpl-jlcpcb.csv`. The LCSC part column is empty on purpose: JLCPCB's matcher will suggest parts from the part names. Check each match against the name and the package. For the resistors and capacitors any basic part of the same value and size is fine.
5. On the placement preview, check that each chip's pin-1 dot lines up with the marker on the board. JLCPCB's rotation sometimes differs from KiCad's. Fix any that are turned with the rotate button. Last time these needed fixing: **U4, Q1 and U9 turned 180°; U6, U7 and U8 turned 90° clockwise**. JLCPCB resets them every time you upload new files, so set them again. Turn on **Confirm Parts Placement** as a backstop.
   - Buzzer BZ1: its **+** laser mark should sit at the **top-left** pad (next to the + on the silkscreen).
   - SW1: use TL3342F260QG (LCSC C2886894) if the F160 is out of stock.
6. Parts JLCPCB may not stock (often the ICM-42688-P, DPS368, CMT-8504 buzzer or JST-GH connectors): choose "global sourcing" or leave them out and solder them yourself.

## Not soldered by JLCPCB (you solder these)
Teensy sockets (J1, J2), the Pololu 5 V regulator module (U5, 3-pin), the two 3 × 8 servo headers (J21 to J23, J31 to J33) and the XT30 battery plug (J12).
