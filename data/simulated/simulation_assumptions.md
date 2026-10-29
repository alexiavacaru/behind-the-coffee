# Simulation assumptions

There is no public access to the transactions of a real 5 to go café, so everything in `data/simulated/` is
**fictional**, built around figures the company has made public. The generator is
`scripts/generate_simulated_data.py` (random seed 42, so results are reproducible).

**Period:** 2026-01-01 to 2026-03-31 (90 days, one café, open 07:00-19:59).

## Taken from public sources (see `data/raw/sources.csv`)

| Assumption | Value | Source |
|---|---|---|
| Espresso / americano / cappuccino / latte price | 5 / 5 / 8 / 9 RON | 5 to go co-founder interview, Playtech.ro, Feb 2026 |
| Raw materials, black coffee | 29% of price (company range: 28-30%) | same interview |
| Raw materials, milk drinks | 37.5% of price (company range: 37-38%) | same interview |
| Royalty / marketing fee | 4% / 1.5% of sales | same interview |
| Reported net profit of a franchise | 15-25% of sales | same interview |
| Break-even | ~80 receipts per day (rent ~720 EUR, one employee, average receipt 14 RON excl. VAT) | same interview |

## My own assumptions (not verified)

- **Volume:** ~255 items on a weekday (about 125 receipts at ~2 items each); Friday +5%, Saturday -15%,
  Sunday -30%; January -5%, March +5%; random daily noise of about 8%.
- **Hourly profile:** morning peak at 08:00 (14% of daily items), smaller peaks at 12:00-13:00 and 17:00.
- **Product mix:** espresso 30%, americano 14%, cappuccino 32%, latte 24% (slightly more espresso before 10:00).
- **Prices are constant** over the 90 days.
- **Operating costs per month:** rent 5,000 RON (about 1,000 EUR; the company says a good Bucharest spot is hard
  to find below that), salaries 12,000 RON (two baristas, total employer cost), utilities 1,900 / 1,800 / 1,600 RON,
  other costs 1,500 RON.
- **Inventory:** 9 g of beans per shot; 0.17 L of milk per cappuccino and 0.26 L per latte; one cup per drink;
  waste of about 0.5% (beans), 3% (milk) and 1% (cups).

## Limitations

- VAT is not separated: menu prices include it, so revenue is slightly overstated compared to a real P&L.
- Weather does not influence the simulated demand; any weather effect found later in the analysis comes from
  the data, not from the simulation.
- Contribution margin is not profit. `data/processed/monthly_profit.csv` shows the full chain down to operating
  profit (after royalty, marketing fee, rent, salaries, utilities and other costs).
