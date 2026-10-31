from __future__ import annotations
import json,argparse,csv
from pathlib import Path
from .rpc import collect, DEFAULT_RPC_URL
from .demo import make_demo
from .analyze import metrics
from .dashboard import write_html

ROOT=Path(__file__).resolve().parents[1]

def run(argv=None):
    p=argparse.ArgumentParser(description='ETH block headers; demo synthetic by default; live explicitly opt-in')
    p.add_argument('mode',nargs='?',choices=['demo','live','report'],default='demo')
    p.add_argument('--count',type=int,default=96)
    p.add_argument('--rpc-url',default=DEFAULT_RPC_URL)
    p.add_argument('--end-tag',choices=['safe','finalized'],default='finalized')
    p.add_argument('--input',type=Path,default=ROOT/'data/example_blocks_SYNTHETIC.json')
    p.add_argument('--out',type=Path,default=ROOT/'artifacts')
    a=p.parse_args(argv)
    a.out.mkdir(parents=True,exist_ok=True)
    if a.mode=='demo':
        snapshot=make_demo(a.count)
        (ROOT/'data').mkdir(exist_ok=True)
        (ROOT/'data/example_blocks_SYNTHETIC.json').write_text(json.dumps(snapshot,indent=2)+'\n')
    elif a.mode=='live':
        snapshot=collect(url=a.rpc_url,count=a.count,end_tag=a.end_tag)
        (a.out/'last_live_rpc_snapshot.json').write_text(json.dumps(snapshot,indent=2)+'\n')
    else:
        snapshot=json.loads(a.input.read_text())
    summary,rows=metrics(snapshot)
    if snapshot['mode']=='live_rpc':
        html=a.out/'LIVE_RPC_dashboard.html'
        csvpath=a.out/'LIVE_RPC_metrics.csv'
        jsonpath=a.out/'LIVE_RPC_summary.json'
    else:
        html=a.out/'SYNTHETIC_demo_dashboard.html'
        csvpath=a.out/'SYNTHETIC_demo_metrics.csv'
        jsonpath=a.out/'SYNTHETIC_demo_summary.json'
    write_html(html,summary,rows)
    with csvpath.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
    jsonpath.write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({'mode':snapshot['mode'],'block_count':len(rows),
                      'mean_gas_utilization':summary['mean_utilization'],'dashboard':str(html)},indent=2))

if __name__=='__main__':run()
