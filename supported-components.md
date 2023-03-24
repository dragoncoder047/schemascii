# Supported Schemascii Components

<!--
AUTOMATICALLY GENERATED FILE!
DO NOT EDIT!
Your changes will simply be overwritten.
Instead, edit the docstrings in schemascii/components_render.py
and run scripts/docs.py to re-generate this file.
-->

| Reference Designators | Description | BOM Syntax | Supported Flags |
|:--:|:--|:--:|:--|
| `R`, `RV`, `VR` | Resistor, Variable resistor, etc. | `ohms[,watts]` |  |
| `C`, `CV`, `VC` | Draw a capacitor, variable capacitor, etc. | `farads[,volts]` | `+` = positive |
| `L`, `VL`, `LV` | Draw an inductor (coil, choke, etc) | `henries` |  |
| `B`, `BT`, `BAT` | Draw a battery cell. | `volts[,amp-hours]` | `+` = positive |
| `D`, `LED`, `CR`, `IR` | Draw a diode or LED. | `part-number` | `+` = positive |
| `U`, `IC` | Draw an IC. | `part-number[,pin1-label[,pin2-label[,...]]]` |  |
| `J`, `P` | Draw a jack connector or plug. | `label` |  |
| `Q`, `MOSFET`, `MOS`, `FET` | Draw a bipolar transistor (PNP/NPN) or FET (NFET/PFET). | `{npn/pnp/nfet/pfet}:part-number` | `s` = source<br>`d` = drain<br>`g` = gate<br>`e` = emitter<br>`c` = collector<br>`b` = base |
