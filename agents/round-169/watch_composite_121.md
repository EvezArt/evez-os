# Agent: watch_composite_121.py — R169 CANONICAL NO FIRE

| field | value |
|-------|-------|
| round | 169 |
| N | 121 |
| N_factored | 11^2 |
| tau | 3 |
| omega_k | 1 |
| topo | 1.15 |
| poly_c | 0.347627 |
| fire_ignited | NO |
| delta_V | 0.027810 |
| V_global_prev | 5.555132 |
| V_global_new | 5.582942 |
| ceiling_tick | 87 |
| probe_id | 1016d0ec-4ed6-43e1-835e-138baa795e98 |
| probe_match | CONFIRMED (delta=0.000000) |
| truth_plane | CANONICAL |
| generated_at | 2026-02-24T02:00:51-08:00 |

## Verification
- topo = 1.0 + 0.15*1 = 1.15
- ln(tau=3) = 1.098612
- log2(N+2=123) = 6.942515
- poly_c = 1.15*(1+1.098612)/6.942515 = 0.347627
- fire = 0.347627 >= 0.500 => False => NO FIRE
- Probe 1016d0ec: delta=0.000000 PERFECT MATCH
