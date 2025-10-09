# GCode Tutorial

## Commands

### G-Commands

- `G0 XA YB ZC`: rapid move to coordinates `A, B, C`, probably the only command we need. Units of measure should be specified before
- `G01 XA YB ZC FD`: controlled move to coordinates. Feed rate needs to be specified with `G94 FD`, which tells the program what speed in mm/min to move. Units of measure should be specified before
- `G02 XA YB ZC RD`: cut in a clockwise circular arc with radius `D` and move by (or to) `A, B, C` to do it (only specify 2 at a time)
- `G02 IA`: cut a full circle starting at current position, radius `A`
- `G03 XA YB ZC RD`: cut in a counter-clockwise circular arc
- `G20`: imperial mode
- `G21`: metric mode
- `G90`: absolute programming. 'Move to' coordinates specified with `G0` or `G1` will specify coordinates with respect to the global zero. Motions will be carried out by moving the tool from the last coordinates to the new global coordinates
- `G91`: incremental programming. 'Move to' coordinates specified with `G0` or `G1` will specify coordinates with respect current positioning, 'moving' the zero to the current position. Motions will be carried out by moving the tool from the last coordinates to the last coordinates plus the components specified in `G0` or `G1`. This resets to global zero at every different `Z`-level
- `G53`: machine coordinate
- `G54`: coordinate system offset

### M-commands

- `M0`: pause the machine, can be resumed
- `M2`: end the program
- `M8`: activate SSR relay
- `M9`: deactivate SSR relay
- `M30`: program stop and rewind to first line

### Letter Codes

- `F`: feed rate
- `R`: radius of semicircle
- `S`: spindle speed
- `X/Y/Z`: move directions
- `N`: line number
- `I`: radius of full circle
