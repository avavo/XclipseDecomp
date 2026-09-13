# G3D DVFS table — s5e9945 / Xclipse 940 (second device)

GPU power/clocks from sysfs on another S24+ unit (`sgpu@22200000`,
`genID = 1`, chip `0x02600200`, EVT0 `0x02600100`):

- 14 frequency states: 252 → 315 → 350 → 400 → 450 → 500 → 545 → 600 →
  650 → 700 → 800 → 900 → 1000 → 1095 MHz
- min 252 MHz, max / `cl_boost` 1095 MHz, highspeed 450 MHz
- MIF locks scale with GPU clock (450 MHz → 1.352 GHz …
  1095 MHz → 4.206 GHz); 4 GL2 ACE instances
- Power: coefficient 625, domain `pd_g3dcore`, DVFS calibration
  `ACPM_DVFS_G3D`, `IFPO_ABORT`, calibration ID `0x23`
