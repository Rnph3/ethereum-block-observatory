"""Ethereum JSON-RPC read-only collector; requires explicit `live` CLI mode."""
from __future__ import annotations
import json, urllib.request, urllib.error, time
from typing import Callable

DEFAULT_RPC_URL='https://ethereum-rpc.publicnode.com'

class RPCError(RuntimeError):pass

def call(url: str, method: str, params: list, timeout: float=15):
    payload=json.dumps({'jsonrpc':'2.0','id':1,'method':method,'params':params}).encode()
    request=urllib.request.Request(url,data=payload,headers={'Content-Type':'application/json','User-Agent':'ETHBlockObservatory/0.1'},method='POST')
    try:
        with urllib.request.urlopen(request,timeout=timeout) as response:
            if response.status != 200:raise RPCError(f'RPC HTTP {response.status}')
            result=json.load(response)
    except (urllib.error.URLError,ValueError,TimeoutError) as exc:
        raise RPCError(f'Unable to access Ethereum RPC: {type(exc).__name__}') from exc
    if not isinstance(result,dict) or result.get('error') or result.get('result') is None:
        raise RPCError(f'RPC method {method!r} returned null or error')
    return result['result']


def collect(url: str=DEFAULT_RPC_URL, count: int=48, end_tag='finalized', rpc_call: Callable=call):
    if not (3<=count<=200):raise ValueError('count must be 3..200; avoid large public-RPC requests')
    if end_tag not in ('safe','finalized'):raise ValueError('Use safe or finalized blocks only')
    chain=rpc_call(url,'eth_chainId',[])
    if chain!='0x1':raise RPCError('This demo only accepts Ethereum mainnet (chain id=1)')
    tip=rpc_call(url,'eth_getBlockByNumber',[end_tag,False])
    if not isinstance(tip,dict):raise RPCError('Missing tip block')
    top=int(tip['number'],16)
    if top<count:raise RPCError('Chain too short')
    blocks=[]
    for height in range(top-count+1,top+1):
        block=tip if height==top else rpc_call(url,'eth_getBlockByNumber',[hex(height),False])
        if not isinstance(block,dict) or int(block.get('number','0x0'),16)!=height:
            raise RPCError(f'Missing or wrong block height {height}')
        blocks.append(block)
        if rpc_call is call:time.sleep(.06)  # public endpoint courtesy throttle; no background polling
    validate_blocks(blocks)
    return {'mode':'live_rpc','network':'ethereum-mainnet','chain_id':1,
            'rpc_source':'Ethereum JSON-RPC (public or user supplied; credentials redacted)',
            'block_tag':end_tag,'blocks':blocks,
            'coverage_warning':'N consecutive execution-layer blocks, not full onchain ecosystem'}


def validate_blocks(blocks: list[dict]):
    if len(blocks)<3:raise ValueError('At least 3 blocks required')
    prev=None
    for b in blocks:
        try:
            n=int(b['number'],16)
            timestamp=int(b['timestamp'],16)
            used=int(b['gasUsed'],16)
            limit=int(b['gasLimit'],16)
            fee=int(b['baseFeePerGas'],16)
            block_hash=b['hash']
            parent=b['parentHash']
            tx=b['transactions']
        except (KeyError,ValueError,TypeError) as exc:raise ValueError('Missing/invalid block field') from exc
        if not (0<=used<=limit and limit>0 and fee>=0 and timestamp>0):
            raise ValueError('Invalid gas/fee/timestamp')
        if not isinstance(tx,list) or not isinstance(block_hash,str) or len(block_hash)!=66 or not isinstance(parent,str) or len(parent)!=66:
            raise ValueError('Expected hashes and transaction hash list')
        if not all(isinstance(x,str) and x.startswith('0x') for x in tx):
            raise ValueError('Expected tx hash strings')
        if prev is not None:
            if n!=int(prev['number'],16)+1 or parent.lower()!=prev['hash'].lower():
                raise ValueError('Discontinuous parent hashes or block numbers')
            if timestamp< int(prev['timestamp'],16):
                raise ValueError('Nonmonotonic block timestamp')
        prev=b
    return True
