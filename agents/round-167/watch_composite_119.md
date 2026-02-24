# Agent: watch_composite_119.py — R167 CANONICAL

| field | value |
|-------|-------|
| round | 167 |
| N | 119 |
| N_factored | 7x17 |
| tau | 4 |
| omega_k | 2 |
| topo | 1.3 |
| poly_c | 0.448366 |
| fire_ignited | NO FIRE |
| delta_V | 0.035869 |
| V_global_prev | 5.456121 |
| V_global_new | 5.491990 |
| ceiling_tick | 85 |
| truth_plane | CANONICAL |
| generated_at | 2026-02-24T01:16:49-08:00 |

## Verification
- topo = 1.0 + 0.15*2 = 1.3
- ln(tau=4) = 1.386294
- log2(N+2=121) = 6.918863
- poly_c = 1.3*(1+1.386294)/6.918863 = 0.448366
- fire = 0.448366 >= 0.500 => False => NO FIRE
