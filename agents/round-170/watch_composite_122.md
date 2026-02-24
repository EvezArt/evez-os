# Agent: watch_composite_122.py — R170 CANONICAL NO FIRE

| field | value |
|-------|-------|
| round | 170 |
| N | 122 |
| N_factored | 2x61 |
| tau | 4 |
| omega_k | 2 |
| topo | 1.30 |
| poly_c | 0.446088 |
| fire_ignited | NO |
| delta_V | 0.035687 |
| V_global_prev | 5.582942 |
| V_global_new | 5.618629 |
| ceiling_tick | 88 |
| probe_id | 64c57f06-b0b9-4cfa-ab66-05b8cc685705 |
| probe_match | CONFIRMED (delta=0.000000) |
| truth_plane | CANONICAL |
| generated_at | 2026-02-24T02:06:23-08:00 |

## Verification
- topo = 1.0 + 0.15*2 = 1.30
- ln(tau=4) = 1.386294
- log2(N+2=124) = 6.954196
- poly_c = 1.30*(1+1.386294)/6.954196 = 0.446088
- fire = 0.446088 >= 0.500 => False => NO FIRE
- Probe 64c57f06: delta=0.000000 PERFECT MATCH
