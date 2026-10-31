# X thread draft — Ethereum Block Observatory

1/3 A blockchain dashboard is only as credible as its data provenance. I built a read-only Ethereum JSON-RPC block observatory with explicit synthetic vs live modes.

2/3 Metrics: execution gas use, EIP-1559 base fee, base-fee burn (not all ETH burn), tx count, and past-only anomaly flags. Offline dashboard uses **SYNTHETIC** blocks—not live Ethereum data.

3/3 Python stdlib pipeline, continuity checks, tests and self-contained HTML: [GITHUB_URL]
Live RPC mode is implemented but NOT tested in this offline build. No wallets or trades.
