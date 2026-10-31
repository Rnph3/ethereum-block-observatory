# An Ethereum Block Dashboard That Tells You When Its Data Is Synthetic

*A small read-only RPC pipeline for block utilization, EIP-1559 fees, and reproducible provenance.*

A chart can look convincing while hiding the most important question: Where did the data come from?

I built **Ethereum Block Observatory** as a small data-engineering experiment. It fetches Ethereum execution-layer block headers using JSON-RPC (when explicitly invoked), validates block order and parent-hash continuity, calculates a few EIP-1559 metrics, and generates a self-contained HTML dashboard without a CDN.

## What the code measures

- Transaction hash count per execution block
- Gas utilization = `gasUsed / gasLimit`
- Base fee in Gwei = `baseFeePerGas / 1e9`
- **Execution-gas base-fee burn** = `baseFeePerGas × gasUsed / 1e18` ETH
- A simple high-utilization anomaly flag based exclusively on the previous 12 blocks

This is not a measure of all ETH burn: blob gas fee burning is excluded. It also does not decode token transfers, identify active users, measure DeFi TVL or support trading decisions.

## Two intentionally separate modes

**Offline demo:** The included 96-block fixture contains synthetic Ethereum-like blocks with deterministic fake hashes and transactions. Every corresponding file and dashboard states **SYNTHETIC DEMO — NOT REAL CHAIN DATA**. The values are illustrative, not observations of Ethereum in 2024 or 2026.

**Opt-in real collection:** On a machine with Internet access, `python -m observatory.main live --count 32 --end-tag finalized` queries an Ethereum mainnet RPC, validates chain ID 1 and block continuity, and writes a separately named LIVE_RPC snapshot and dashboard.

The real RPC path **was not executed in the offline build environment**. I do not claim to have gathered current chain observations in this release.

## Research and engineering lessons

The project makes the provenance flag part of the data contract, not a footnote. It also ensures an anomaly score for block `t` is computed only using data before `t`, and tests verify later data cannot change earlier scores.

For production, I would add independent RPC reconciliation, reorganization-safe persistence, monitoring and retries. The next analyst-facing extension would decode ERC-20 `Transfer` events and compare results against an independent source, with verified token decimals and block finality.

**Code, explicit provenance, tests, and offline HTML demo:** [GITHUB_URL]

**Screenshot:** Insert a screenshot of `artifacts/SYNTHETIC_demo_dashboard.html`, preserving the synthetic disclaimer visible in the image.

*References: Ethereum JSON-RPC docs (https://ethereum.org/developers/docs/apis/json-rpc/), EIP-1559 (https://eips.ethereum.org/EIPS/eip-1559), PublicNode's endpoint listing (https://ethereum.publicnode.com/). Prepared with AI assistance for final author review.*
