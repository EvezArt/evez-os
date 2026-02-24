# Agent: watch_composite_120.py — R168 CANONICAL FIRE#26

| field | value |
|-------|-------|
| round | 168 |
| N | 120 |
| N_factored | 2^3x3x5 |
| tau | 16 |
| omega_k | 3 |
| topo | 1.45 |
| poly_c | 0.789274 |
| fire_ignited | FIRE#26 |
| delta_V | 0.063142 |
| V_global_prev | 5.491990 |
| V_global_new | 5.555132 |
| ceiling_tick | 86 |
| probe_id | ff4e215a-0873-4153-9265-0bac410b5eb3 |
| probe_match | CONFIRMED |
| truth_plane | CANONICAL |
| generated_at | 2026-02-24T01:30:19-08:00 |

## Verification
- topo = 1.0 + 0.15*3 = 1.45
- ln(tau=16) = 2.772589
- log2(N+2=122) = 6.930737
- poly_c = 1.45*(1+2.772589)/6.930737 = 0.789274
- fire = 0.789274 >= 0.500 => True => FIRE#26
- Probe ff4e215a: poly_c=0.789 diff=0.000274 CONFIRMED
