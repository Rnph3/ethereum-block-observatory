"""Standard-library block header metrics. No claim about complete ETH burn or DeFi activity."""
from datetime import datetime, timezone
import statistics
from .rpc import validate_blocks


def metrics(snapshot: dict, window=12, z_threshold=3.0) -> tuple[dict,list[dict]]:
    if snapshot.get('mode') not in {'synthetic_demo','live_rpc'}:
        raise ValueError('Unknown provenance. Synthetic vs live must be explicit.')
    if window < 3 or z_threshold<=0:raise ValueError('Invalid anomaly settings')
    blocks=snapshot['blocks'];validate_blocks(blocks)
    table=[]
    for i,b in enumerate(blocks):
        height=int(b['number'],16); gas_used=int(b['gasUsed'],16)
        gas_limit=int(b['gasLimit'],16); base_fee=int(b['baseFeePerGas'],16)
        ts=int(b['timestamp'],16)
        utilization=gas_used/gas_limit
        history=[r['gas_utilization'] for r in table[max(0,len(table)-window):]]
        # Center+scale use solely *previous* blocks, not the current observation.
        if len(history)>=window:
            median=statistics.median(history)
            mad=statistics.median(abs(x-median) for x in history)
            z=(utilization-median)/max(1.4826*mad,0.05)
            anomaly = bool(z>z_threshold)
        else:
            z=None;anomaly=False
        table.append({
            'block':height,
            'utc_time':datetime.fromtimestamp(ts,timezone.utc).isoformat(),
            'tx_count':len(b['transactions']),
            'gas_used':gas_used,
            'gas_limit':gas_limit,
            'gas_utilization':utilization,
            'base_fee_gwei':base_fee/1e9,
            'execution_base_fee_burn_eth':base_fee*gas_used/1e18,
            'seconds_since_previous': ts-int(blocks[i-1]['timestamp'],16) if i else None,
            'anomaly_z_past_only':z,
            'unusually_high_utilization':anomaly,
        })
    summary={
        'provenance':snapshot['mode'],
        'network':snapshot['network'],
        'block_count':len(table),
        'start_height':table[0]['block'],
        'end_height':table[-1]['block'],
        'start_utc':table[0]['utc_time'],
        'end_utc':table[-1]['utc_time'],
        'mean_utilization':statistics.mean(x['gas_utilization'] for x in table),
        'mean_base_fee_gwei':statistics.mean(x['base_fee_gwei'] for x in table),
        'total_execution_base_fee_burn_eth':sum(x['execution_base_fee_burn_eth'] for x in table),
        'anomaly_count':sum(x['unusually_high_utilization'] for x in table),
        'mean_tx_per_block':statistics.mean(x['tx_count'] for x in table),
        'methodology':{
            'utilization':'execution gasUsed / execution gasLimit',
            'execution_base_fee_burn_eth':'baseFeePerGas (wei) * gasUsed / 1e18; excludes blob gas burn, tips, MEV',
            'anomaly':'gas-utilization > rolling prior 12 blocks median + 3 * max(1.4826*MAD, 0.05)',
            'scope':'block-header observations only; does not measure token transfers, DeFi protocol flow, users or PnL',
        }
    }
    return summary,table
