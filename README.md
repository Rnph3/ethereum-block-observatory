# Ethereum Block Observatory — Read-only RPC + Offline Dashboard

**Scope:** Fetch Ethereum mainnet **execution-layer block headers** through `eth_getBlockByNumber`, compute transparent EIP-1559 block metrics, flag unusually full blocks using only earlier observations, and write an entirely self-contained HTML dashboard.

## Data integrity: demo versus live

This package contains a working **offline synthetic demo** in `data/example_blocks_SYNTHETIC.json`, plus a read-only `live` collector. Because the build sandbox could not reach public RPC endpoints, **no live mainnet collection was executed or claimed**. Every demo dashboard prominently says `SYNTHETIC DEMO — NOT REAL CHAIN DATA`. Synthetic block hashes, values and transaction counts are fictional.

## Quick start — entirely offline

```bash
python -m observatory.main demo
python -m pytest -q
```

Open `artifacts/SYNTHETIC_demo_dashboard.html` in any browser. It includes inline SVG charts, summary KPIs, 20-row table, and limitations. No dependencies, CDN or JavaScript needed.

## Real Ethereum mainnet — explicit opt-in network request

```bash
python -m observatory.main live --count 32 --end-tag finalized
# or use your own compatible RPC
python -m observatory.main live --rpc-url https://ethereum-rpc.publicnode.com --count 48
```

Outputs: `artifacts/last_live_rpc_snapshot.json`, `artifacts/LIVE_RPC_dashboard.html`, `artifacts/LIVE_RPC_metrics.csv`, `artifacts/LIVE_RPC_summary.json`. Default public endpoint is https://ethereum-rpc.publicnode.com; availability, rate limits, privacy and region restrictions depend on provider. Never put a secret RPC API token into publicly committed files. The script checks `eth_chainId == 0x1`, retrieves a consecutive `finalized` (or `safe`) range and validates consecutive parent hashes. Up to 200 blocks maximum to avoid excessive requests.

## What is really measured?

| Metric | Formula / meaning |
|---|---|
| Transaction count | Length of block `transactions` hash list |
| Execution gas utilization | `gasUsed / gasLimit` |
| EIP-1559 base fee (Gwei) | `baseFeePerGas / 1e9` |
| Execution base-fee burn (ETH) | `baseFeePerGas × gasUsed / 1e18` |
| Anomaly flag | Current gas utilization exceeds rolling prior 12 blocks median by 3× robust scale (MAD with floor 0.05) |

**These metrics are not:** total ETH burn (excludes blob gas fee burning), validator income, stablecoin volume, DeFi protocol use, user counts or proof of profit. Transactions count refers only to transactions included in the sampled execution block. Block data is onchain **header** data, not Dune protocol-level analytics.

## Reproducibility

- Offline `demo` is deterministic (same seed and count, same hashes and metrics).
- `report` can re-run a previously collected JSON snapshot without network:
  `python -m observatory.main report --input artifacts/last_live_rpc_snapshot.json`
- No credentials, wallets, signing, swaps, sends or smart-contract state mutation.
- Tests mock RPC network and verify chain-id enforcement, continuity, fee formula, no future leakage in anomaly scores and output labels.

## Suggested next step for an on-chain analyst portfolio

Add event-log decoding for a clearly defined ERC-20 contract using `eth_getLogs` with verified contract addresses and token decimals; establish data completeness and reorg handling; compare decoded events to a trusted block explorer or an independent Dune query. **Not implemented in this version.**

## Literature / API references

- Ethereum JSON-RPC block method: https://ethereum.org/developers/docs/apis/json-rpc/#eth_getblockbynumber
- EIP-1559: https://eips.ethereum.org/EIPS/eip-1559
- PublicNode endpoint listing: https://ethereum.publicnode.com/

## License

MIT for original project code and synthetic fixture. Confirm copyright owner before publication.
