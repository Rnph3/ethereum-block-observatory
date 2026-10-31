"""Generate standalone, local HTML using SVG. No CDN, cookies or network calls."""
from __future__ import annotations
from html import escape
from pathlib import Path
import json, math

def line_chart(rows:list[dict], key:str, title:str, unit:str='',color:str='#4adfd4') -> str:
    values=[float(x[key]) for x in rows]
    n=len(values);mn=min(values);mx=max(values)
    if mx==mn:mx+=1
    pts=[]; circles=[]
    for i, v in enumerate(values):
        x=44+ i* (790/(n-1))
        y=220-(v-mn)/(mx-mn)*178
        pts.append(f'{x:.1f},{y:.1f}')
        if i % max(1,n//20)==0:
            circles.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.6" fill="{color}"><title>Block {rows[i]["block"]}: {v:.5g} {escape(unit)}</title></circle>')
    horizontal=''.join(f'<line x1="44" y1="{y}" x2="835" y2="{y}" stroke="#253144" stroke-width="1" />' for y in [40,85,130,175,220])
    return f'''<section class="panel"><h2>{escape(title)}</h2><svg class="plot" viewBox="0 0 870 256" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{escape(title)}">
    {horizontal}<text x="44" y="24" fill="#8da3b7" font-size="12">Max: {mx:.4g} {escape(unit)}</text>
    <text x="44" y="242" fill="#8da3b7" font-size="12">Min: {mn:.4g} {escape(unit)}</text>
    <polyline fill="none" stroke="{color}" stroke-width="3" points="{' '.join(pts)}" />{''.join(circles)}</svg></section>'''

def write_html(path:str|Path,summary:dict,rows:list[dict]):
    synth=summary['provenance']=='synthetic_demo'
    label='SYNTHETIC DEMO — NOT REAL CHAIN DATA' if synth else 'LIVE MAINNET RPC BLOCK SNAPSHOT'
    subtitle='Offline fixture; all hashes and numbers are illustrative.' if synth else 'Read-only mainnet block data; inspect the source record for timestamp and height.'
    cards=[
       ('Blocks',str(summary['block_count'])),
       ('Mean gas use',f"{summary['mean_utilization']:.1%}"),
       ('Mean base fee',f"{summary['mean_base_fee_gwei']:.3f} gwei"),
       ('Execution base-fee burn',f"{summary['total_execution_base_fee_burn_eth']:.4f} ETH"),
       ('High-utilization flags',str(summary['anomaly_count'])),
    ]
    card_html=''.join(f'<div class="card"><div class="k">{escape(k)}</div><div class="v">{escape(v)}</div></div>' for k,v in cards)
    lines=''.join(f'''<tr><td>{r['block']:,}</td><td>{escape(r['utc_time'][11:19])}</td><td>{r['tx_count']}</td>
      <td>{r['gas_utilization']:.1%}</td><td>{r['base_fee_gwei']:.3f}</td><td>{r['execution_base_fee_burn_eth']:.5f}</td>
      <td>{'YES' if r['unusually_high_utilization'] else '—'}</td></tr>''' for r in rows[-20:][::-1])
    html=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Ethereum Block Observatory · {escape(label)}</title>
    <style>:root{{font-family:ui-sans-serif,system-ui,Arial;color:#dae8ef;background:#0e1421}}*{{box-sizing:border-box}}main{{max-width:1120px;margin:auto;padding:32px 20px 80px}}h1{{font-size:2.2rem;letter-spacing:-.05rem;margin-bottom:8px}}h2{{font-size:1.1rem}}p,.muted{{color:#9fb4c8}}.flag{{display:inline-block;background:{'#392019' if synth else '#163c33'};color:{'#ffd2a7' if synth else '#8cf3c4'};border:1px solid {'#99572e' if synth else '#34735d'};padding:8px 12px;border-radius:6px;font-size:.78rem;letter-spacing:.06rem;font-weight:700}}.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px;margin:26px 0}}.card,.panel{{background:#161f30;border:1px solid #2b3950;border-radius:12px;padding:20px}}.k{{color:#95abc0;font-size:.84rem}}.v{{font-weight:750;font-size:1.42rem;margin-top:8px}}.grid{{display:grid;grid-template-columns:1fr 1fr;gap:14px}}@media(max-width:760px){{.grid{{grid-template-columns:1fr}}}}.plot{{width:100%;height:auto}}.wide{{overflow-x:auto}}table{{width:100%;min-width:710px;border-collapse:collapse;font-size:.86rem}}td,th{{padding:11px;border-bottom:1px solid #2c3a4c;text-align:right}}td:first-child,th:first-child{{text-align:left}}.panel{{margin-top:14px}}a{{color:#64d8db}}code{{color:#ffd39a}}</style></head><body><main><div class="flag">{escape(label)}</div>
    <h1>Ethereum Block Observatory</h1><p>{escape(subtitle)}</p><p>Range: {summary['start_height']:,}–{summary['end_height']:,} · {escape(summary['start_utc'])} to {escape(summary['end_utc'])}</p>
    <div class="cards">{card_html}</div><div class="grid">
    {line_chart(rows,'base_fee_gwei','EIP-1559 execution base fee','gwei')}
    {line_chart(rows,'gas_utilization','Execution gas utilization','fraction','#b19bff')}
    </div>{line_chart(rows,'execution_base_fee_burn_eth','Execution-layer base-fee burn (per block)','ETH','#e9bb75')}
    <section class="panel wide"><h2>Last 20 observed blocks</h2><table><thead><tr><th>Block</th><th>UTC</th><th>TX</th><th>Gas use</th><th>Base gwei</th><th>Base burn ETH</th><th>Anomaly</th></tr></thead><tbody>{lines}</tbody></table></section>
    <section class="panel"><h2>Method and limitations</h2><p>Execution gas utilization = gasUsed/gasLimit; base-fee burn = gasUsed × baseFeePerGas. The latter excludes blob base fees, priority tips, MEV and other economics. Only the previous 12 blocks enter each robust anomaly baseline.</p><p>This small header sample does <strong>not</strong> measure total Ethereum users, DeFi TVL, token transfers, stablecoins, or financial profit. RPC snapshots may differ across providers at forks. See the GitHub README and sources.</p><p>Built with Python standard library, and generated as a standalone offline HTML file. No trackers, CDN scripts or external chart services.</p></section></main></body></html>'''
    p=Path(path);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(html,encoding='utf-8')
