import copy, json
from pathlib import Path
import pytest
from observatory.demo import make_demo
from observatory.rpc import validate_blocks, collect, RPCError
from observatory.analyze import metrics
from observatory.dashboard import write_html


def snapshot(n=40): return make_demo(n)

def test_deterministic_synthetic_fixture():
    assert snapshot()==snapshot()
    assert snapshot()['mode']=='synthetic_demo'

def test_contiguous_parent_hashes():
    assert validate_blocks(snapshot()['blocks'])

def test_parent_hash_tampering_fails():
    blocks=snapshot()['blocks']
    blocks[3]['parentHash']='0x'+'a'*64
    with pytest.raises(ValueError):validate_blocks(blocks)

def test_gas_used_out_of_range_fails():
    blocks=snapshot()['blocks']; blocks[0]['gasUsed']=hex(2000000000)
    with pytest.raises(ValueError):validate_blocks(blocks)

def test_execution_burn_exact_formula():
    s=snapshot();summary,rows=metrics(s)
    for b,r in zip(s['blocks'],rows):
        assert r['execution_base_fee_burn_eth']==pytest.approx(int(b['gasUsed'],16)*int(b['baseFeePerGas'],16)/1e18)
    assert summary['total_execution_base_fee_burn_eth']==pytest.approx(sum(r['execution_base_fee_burn_eth'] for r in rows))

def test_anomalies_do_not_use_future():
    s=snapshot()
    _,a=metrics(s)
    t=copy.deepcopy(s)
    t['blocks'][-1]['gasUsed']=hex(29_999_999)
    _,b=metrics(t)
    for old,new in zip(a[:-1],b[:-1]):
        assert old['anomaly_z_past_only']==new['anomaly_z_past_only']

def test_network_off_by_default_in_demo():
    s=snapshot()
    assert 'rpc_source' not in s and s['network'].startswith('FICTIONAL')

def test_live_rpc_accepts_only_mainnet():
    def fake(url,method,params):
        assert method=='eth_chainId'
        return '0x89'
    with pytest.raises(RPCError):collect(count=5,rpc_call=fake)

def test_rpc_mock_accepts_finalized_headers():
    rows=snapshot(9)['blocks']
    def mock(url,method,params):
        if method=='eth_chainId':return '0x1'
        if method=='eth_getBlockByNumber':
            if params[0]=='finalized':return rows[-1]
            ix=int(params[0],16)-int(rows[0]['number'],16)
            return rows[ix]
        raise AssertionError(method)
    s=collect(count=9,rpc_call=mock)
    assert s['mode']=='live_rpc' and len(s['blocks'])==9

def test_unknown_provenance_denied():
    s=snapshot();s['mode']='real'
    with pytest.raises(ValueError):metrics(s)

def test_embedded_dashboard_offline_and_labels(tmp_path):
    s=snapshot(); summary,rows=metrics(s)
    path=tmp_path/'index.html';write_html(path,summary,rows)
    html=path.read_text()
    assert 'SYNTHETIC DEMO' in html and '<svg' in html and '<table' in html
    assert 'https://cdn' not in html

def test_guard_large_public_queries():
    with pytest.raises(ValueError):collect(count=500)
