# EVEZ Energy Contribution Accounting — research and design v0.1

## Purpose

Create an auditable, voluntary accounting system for verified energy contributions and the people who perform the work that makes the grid operate. Do not claim to calculate a person's total human worth, net worth, or entitlement to a universal amount of currency. Keep physical energy, labor compensation, household wealth, environmental attributes, and token balances as distinct ledgers.

## Baseline facts (United States)

Use dated public aggregates as planning baselines, not as individual account balances:

- DOE's 2026 U.S. Energy & Employment Report says the energy economy employed 8.4 million workers in 2025, about 5% of the U.S. workforce; reported energy-sector median wages were $63,000.
- EIA reports U.S. net electricity generation of about 4,430 TWh in 2025.
- EIA reports 2025 U.S. retail electricity sales of about 4,058 billion kWh.
- EIA reports a 2025 all-sector average retail electricity price of about 13.63 cents/kWh.
- The Federal Reserve's 2025 Survey of Consumer Finances reports median family net worth of $215,900 and mean family net worth of $1.24 million (2025 dollars).

Sources:
- https://www.energy.gov/documents/2026-useer-national-report
- https://www.eia.gov/todayinenergy/detail.php?id=67284
- https://www.eia.gov/energyexplained/electricity/electricity-in-the-us-generation-capacity-and-sales.php
- https://www.eia.gov/energyexplained/electricity/prices-and-factors-affecting-prices.php
- https://www.federalreserve.gov/newsevents/pressreleases/other20261009a.htm

A rough calculation of 4.058 trillion kWh multiplied by 13.63 cents/kWh is about $553 billion of retail-bill-equivalent value. This is NOT generator revenue, wholesale market value, profit, or a fund available for distribution. Retail rates include costs beyond generation and the multiplication is a scale illustration only. Never use it as the EVEZ token backing number.

## Separate the ledgers

1. **Energy evidence ledger** — metered generation, imports, exports, storage charge/discharge, losses, time interval, location, meter identity, calibration, source signature, settlement state, and correction history.
2. **Market settlement ledger** — actual utility/PPA/RTO settlement price and quantity, fees, curtailment, imbalance charges, and payment status.
3. **Labor contribution ledger** — opt-in, attributable work records for installation, maintenance, dispatch, line work, engineering, safety, customer support, and other roles. Use employer/payroll or contract evidence where appropriate. Do not convert hours into energy units.
4. **Environmental attribute ledger** — RECs/EACs and ownership/retirement state. Do not issue or sell duplicate attributes for the same MWh.
5. **Personal financial ledger** — only with explicit consent and lawful data access; assets minus liabilities belong to the individual/family balance sheet and are not inferred from energy output or occupation.
6. **Token/liability ledger** — if legally approved, records issued units, backing assets, redemption rights, reserves, fees, supply, burns, and audited liabilities.

These ledgers may reference one another by unique IDs, but must not merge unlike measures or count the same economic benefit twice.

## Energy valuation formula

For each eligible settlement interval i:

net_export_MWh_i = metered_export_MWh_i - meter_corrections_i - excluded_or_reversed_MWh_i

settled_energy_value_i = net_export_MWh_i * actual_settlement_price_per_MWh_i

net_contribution_value_i = settled_energy_value_i + separately_settled_grid_services_i - attributable_fees_i - imbalance_costs_i - agreed_operating_costs_i

Use actual interval-specific settlement data and contracts. Retail average prices are not substitutes for wholesale prices or a participant's export tariff. Storage must be accounted for on both charge and discharge sides; do not treat the same stored MWh as newly created energy twice. Record losses explicitly.

For a household solar customer paid under a utility export tariff, use the actual credited amount from the utility statement. For wholesale participation, use the aggregator/RTO settlement statement and its allocation rules. Unsettled or estimated readings remain provisional and cannot support redemption-backed issuance.

## Worker attribution

Do not distribute the entire energy market's gross revenue to energy workers. That would double-count wages, utility revenue, equipment costs, taxes, capital returns, and energy sales.

For each worker or contractor, record only verified, consented contributions and compensation under an explicit program:
- payroll/contract payment already earned;
- optional additional incentive funded by a disclosed pool;
- share of net settlement attributable to a specific asset or service, where contractually agreed.

The incentive pool must be funded from an identified source (e.g., a contracted share of net settlement or a separately funded grant), not from speculative token price appreciation. Publish eligibility rules, rate schedule, caps, appeals, and distribution audits before enrollment.

No credit for merely running an app, claiming output, or submitting a self-attested meter reading. No worker's civic or human worth is determined by productivity, wealth, disability, unemployment, caregiving, or energy contribution. Participation is voluntary and should not affect access to essential electricity or public services.

## Double-counting controls

- One unique meter interval and settlement reference can be credited once.
- One MWh can have one energy settlement allocation per contractual right.
- RECs/EACs are distinct environmental attributes. Track ownership and retirement separately; do not imply an energy credit automatically conveys REC ownership.
- Prevent simultaneous duplicate compensation through retail net metering, aggregator, and wholesale programs; reconcile all contracts and program rules.
- Corrections are new, linked ledger events; never silently overwrite a settled record.
- Maintain independent audit exports and a public methodology.

EPA references:
- https://www.epa.gov/green-power-markets/energy-attribute-certificates-eacs
- https://www.epa.gov/green-power-markets/energy-attribute-tracking-systems
- https://www.epa.gov/green-power-markets/double-counting

## Market access and compliance

FERC Order 2222 provides a pathway for aggregations of distributed energy resources to participate in organized wholesale markets, subject to RTO/ISO tariffs, metering/telemetry, location, coordination, and anti-double-counting rules. Availability and timelines vary by market and are not universal. EVEZ should integrate with qualified utilities/aggregators rather than claim it can independently sell power into every market.

Before issuing a transferable or redeemable token, obtain specialist U.S. legal analysis of securities, money transmission/Bank Secrecy Act, commodities, consumer protection, energy regulation, privacy, sanctions, and tax. The label "utility token" or "energy-backed" does not determine legal treatment. IRS currently treats digital assets as property for federal tax purposes; FinCEN obligations can apply to administrators/exchangers depending on actual activity; SEC treatment depends on the asset and offering facts.

References:
- https://www.ferc.gov/media/ferc-order-no-2222-fact-sheet
- https://www.ferc.gov/ferc-order-no-2222-explainer-facilitating-participation-electricity-markets-distributed-energy
- https://www.sec.gov/resources-small-businesses/capital-raising-building-blocks/transactions-involving-crypto-assets
- https://www.fincen.gov/resources/statutes-regulations/guidance/application-fincens-regulations-persons-administering
- https://www.irs.gov/individuals/international-taxpayers/frequently-asked-questions-on-digital-asset-transactions

## Pilot sequence

1. Read-only ingestion of one participant's actual utility/inverter data, with consent.
2. Compare meter intervals against utility bill/settlement and record discrepancies.
3. Run a 90-day shadow ledger; no token issuance or money movement.
4. Independent auditor validates meter provenance, interval accounting, reconciliation, privacy, and duplicate controls.
5. Publish pilot results, error rates, operating costs, participant terms, and appeal process.
6. Only after legal review, test a small, prefunded, redeemable-or-nonredeemable incentive under clear terms. Never promise price appreciation or dollar parity without legally enforceable reserves and redemption mechanics.

## Decision

The initial EVEZ product should be an **auditable energy contribution registry and settlement reconciliation service**, not a currency claiming to replace the dollar. Its first defensible value proposition is proof: who contributed what, when, where, under which contract, what the market actually paid, and whether the contribution was already compensated or its environmental attributes transferred.
