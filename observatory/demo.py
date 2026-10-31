"""Deterministic **SYNTHETIC** EVM-like block headers for offline tests/demo.

These data are NOT claimed to correspond to any real Ethereum block.
"""
from __future__ import annotations
from datetime import datetime, timezone
import hashlib, random

def make_demo(n=96, seed=31):
    if not 3<=n<=200:raise ValueError('3..200 blocks')
    rng=random.Random(seed)
    start=21_000_000
    gas_limit=30_000_000
    base_fee=19_000_000_000
    timestamp=1_704_067_200  # arbitrary UTC anchor; fictional data
    prevhash='0x'+'0'*64
    blocks=[]
    for i in range(n):
        util= min(.98,max(.15,rng.gauss(.58,.16)))
        if i in {20,52,77}: util=.985
        gas_used=int(gas_limit*util)
        header_hash='0x'+hashlib.sha256(f'SYNTHETIC_ETH_BLOCK::{start+i}::{seed}'.encode()).hexdigest()
        num_tx=max(1,int(gas_used / 160_000))
        tx=['0x'+hashlib.sha256(f'SYNTHETIC_TX::{i}::{j}'.encode()).hexdigest() for j in range(num_tx)]
        blocks.append({
            'number':hex(start+i),'hash':header_hash,'parentHash':prevhash,
            'timestamp':hex(timestamp),'gasUsed':hex(gas_used),'gasLimit':hex(gas_limit),
            'baseFeePerGas':hex(base_fee),'transactions':tx,
        })
        target=gas_limit//2
        if gas_used==target:pass
        elif gas_used>target:
            change=max(base_fee*(gas_used-target)//target//8,1)
            base_fee+=change
        else:
            change=base_fee*(target-gas_used)//target//8
            base_fee-=change
        prevhash=header_hash
        timestamp += max(10,int(rng.gauss(12,2)))
    return {
        'mode':'synthetic_demo',
        'network':'FICTIONAL_ETHEREUM_LIKE_DATA_NOT_MAINNET',
        'chain_id':None,
        'generation':'Deterministic random synthetic headers and toy tx hashes; seed=31',
        'disclaimer':'ALL VALUES ARE SYNTHETIC. Not real chain activity or market signals.',
        'blocks':blocks,
    }
