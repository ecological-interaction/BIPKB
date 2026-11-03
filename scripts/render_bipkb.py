#!/usr/bin/env python3
"""Deterministic presentation of the JSON authority and annotated Mermaid sources."""
import argparse
import html
import json
import re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
COLLECTIONS = ('records', 'references', 'classifications', 'memberships', 'relationships', 'examples', 'methodological_notes', 'research_queue', 'assertions')
FAMILY_NAMES = dict(zip('DNSGCETRIOHBUKXFLQZ', ['Decisions and developments','Naming history','Scope and boundaries','Research stages','Scientific concepts','Illustrative examples','Research territories','Resources and programmes','Indicator families','Standards, ontologies and services','Historical people','Bibliographic leads','Institutions','Communities','Discovery, reference and software','Classification dimensions','Relationship proposals','Verification tasks','Coverage gaps']))

def source_text(data, source):
    spans = [(p['start_line'], p['text']) for p in data['unindexed_material'] if p['source'] == source]
    spans += [(p['line'], p['raw_line']) if source == 'A1' else (p['a2']['line'], p['a2']['raw_line']) for p in data['provenance']]
    return ''.join(text for _, text in sorted(spans))

def scientific(data):
    rev=data['metadata']['corpus_revision']
    out=[f'# BIPKB — Scientific Reference Register\n\n**Corpus revision:** {rev} · Documentary candidates; not a research release.\n',
         'This generated presentation preserves full original A1 wording, including superseded claims, and places corrections alongside it. Historical references to an untouched repository or unavailable baseline describe the source edition, not current development. The [Machine Reference](BIPKB_Machine_Reference.json) is the sole structured authority; [Research Protocol](BIPKB_Research_Protocol.md) explains evidence, independent statuses and limitations.\n',
         '## Current documentary inventory\n\n| Collection | Entries |\n|---|---:|']
    out += [f'| {c.replace("_", " ")} | {len(data[c])} |' for c in COLLECTIONS]
    out += ['\n146 research leads are mentions, not identity-resolved entities. No empirical observations, accepted classifications or inferred memberships are asserted. All scientific verification is pending; rights remain unknown.\n', '## Reading index\n']
    families=list(dict.fromkeys(p['origin_id'].split('-')[-1][0] for p in data['provenance']))
    out += [f'- [{f} — {FAMILY_NAMES[f]}](#family-{f.lower()})' for f in families]
    out += ['- [Correction proposals](#corrections)', '- [Identity questions](#identity-questions)', '- [Preserved context](#preserved-context)\n', '## Candidate register\n']
    byid={x['id']:x for c in COLLECTIONS for x in data[c]}
    contexts={x['id']:x for x in data['unindexed_material']}
    for f in families:
        rows=[p for p in data['provenance'] if p['origin_id'].split('-')[-1].startswith(f)]
        out += [f'<a id="family-{f.lower()}"></a>\n\n### {FAMILY_NAMES[f]}\n',
                'Original fields are reproduced verbatim below. A1 inherited qualifications apply; every entry remains a documentary candidate, with proposal review pending, source lifecycle not established, scientific verification unverified, access not assessed and reuse rights unknown.\n']
        if f=='D':out += ['Reported user instructions and assistant proposals retain their distinct A1 status text. None is authenticated against original decision messages.\n']
        if f=='E':out += ['**Illustrative only:** these are hypothetical examples, not measurements or demonstrated environmental diagnoses.\n']
        if f in 'TF':out += ['**Local proposals:** definitions are distinct from assignments; no classification scheme is adopted. Mixed-dimension refinements appear in the correction ledger.\n']
        headers=rows[0]['headers'];out+=['| Origin ID | '+' | '.join(headers)+' |','|'+'---|'*(len(headers)+1)]
        for p in rows:
            e=byid[p['target']]; values=[e['fields'][h] for h in p['headers']]
            out += ['| <a id="'+p['origin_id'].lower()+'"></a>'+p['origin_id']+' | '+' | '.join(values)+' |']
        out+=['\n<details markdown="1">\n<summary>Disposition and source locators</summary>\n\n| Origin | Local documentary ID | A1 line | A2 line | Recommendation / limits |\n|---|---|---:|---:|---|']
        for p in rows:
            out += [f'| {p["origin_id"]} | {p["target"]} | {p["line"]} | {p["a2"]["line"]} | {p["a2"]["recommended_disposition"]}; {p["a2"]["limits"]} |']
        out+=['\n</details>\n']
    out+=['<a id="corrections"></a>\n\n## Correction proposals\n\nOriginal claims above remain unchanged. These twelve assertions are review-supported or conversation-reported, **not independently verified in this intake**. Edition-specific counts are not timeless resource totals.\n\n| Origin | Correction / qualification | Evidence and limits |\n|---|---|---|']
    for x in data['assertions']:out += [f'| {", ".join(x["origin_ids"])} | {x["assertion"]} | A2 line {x["line"]}; {x["evidence_origin"]}; {x["verification_limit"]} |']
    out+=['\n## Identity questions\n']+[f'- {x["claim"]} ({", ".join(x["origins"])}). {x["status"]}.' for x in data['identity_review']]
    out+=['\n<a id="preserved-context"></a>\n\n## Preserved context\n\nThe following source-context spans preserve evidence keys, interpretation levels, the proposed source-field contract, classification stewardship, inherited section statuses, limitations and historical QA declarations. Each is explicitly historical evidence; it does not issue current instructions or claim that old tests were rerun. Source rows are presented above, not repeated here.\n']
    for p in data['unindexed_material']:
        text=p['text'].strip()
        if not text:continue
        # Heading demotion avoids taking historical titles as the current document title.
        text=re.sub(r'(?m)^(#{1,6}) ', lambda m: '#' * min(6,len(m[1])+3)+' ',text)
        out += [f'### {p["id"]} — {p["source"]} lines {p["start_line"]}–{p["end_line"]}\n\n{text}\n']
    out += ['## Supplementary recovered research context\n\nOne separately counted later reconciliation fragment includes additional reported details not fully captured in A2. It is not the original complete transcript, an independently verified source or an adopted classification. Transient citation tokens are omitted only in this human presentation; exact returned text and its fragment hash remain in JSON.\n']
    for fragment in data['supplementary_material']:
        body=re.sub(r'\ue200[^\ue201]*\ue201','',fragment['text'])
        body=re.sub(r'(?m)^(#{1,6}) ',lambda m:'#'*min(6,len(m[1])+2)+' ',body)
        out += [f"### {fragment['id']} — retrieved fragment\n\nMessage `{fragment['message_id']}`, assistant, turn started {fragment['turn_started_utc']}. {fragment['truncation']}. Scientific status: unverified.\n\n{body}\n\n**Retrieved fragment ends here; continuation unavailable.**\n"]
    out+=['## Citation and limits\n\nJonathan Minchin, Ecological Interaction, [ORCID](https://orcid.org/0000-0001-8152-1796). See [CITATION.cff](CITATION.cff). No licence, release, scientific acceptance, primary-source verification or DRM conformance is assigned. Original conversation completeness and original conceptual-map recovery remain unresolved.\n']
    return '\n'.join(out)

PALETTE={'heading':('#cce3f9','#173b6b'),'knowledge':('#e1f0e6','#41744d'),'method':('#e1daf0','#574087'),'sources':('#feeec9','#a16a16'),'output':('#eaedf1','#7c8c9d')}

def diagram(source):
    """Render a deliberately small annotated Mermaid subset; reject unsupported graphs."""
    text=source.read_text(); canvas=re.search(r'^%% @canvas (\d+) (\d+)$',text,re.M)
    if not canvas:raise ValueError('missing canvas')
    w,h=map(int,canvas.groups()); nodes={k:v.split('<br/>') for k,v in re.findall(r'^\s*(\w+)\["([^"\n]+)"\]',text,re.M)}
    boxes={}
    for ident,x,y,bw,bh,style in re.findall(r'^%% @box (\w+) (\d+) (\d+) (\d+) (\d+) (\w+)$',text,re.M):boxes[ident]=tuple(map(int,(x,y,bw,bh)))+(style,)
    if nodes.keys()!=boxes.keys():raise ValueError('layout/node mismatch')
    title=re.search(r'^%% @title (.+)$',text,re.M)[1];desc=re.search(r'^%% @description (.+)$',text,re.M)[1]
    esc=html.escape
    out=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc">',f'<title id="title">{esc(title)}</title><desc id="desc">{esc(desc)}</desc>', '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8" fill="none" stroke="#65758b"/></marker></defs>', '<rect width="100%" height="100%" fill="white"/>']
    edges=re.findall(r'^\s*(\w+) -\.->\|([^|]+)\| (\w+)\s*$',text,re.M)
    for s,label,t in edges:
        if s not in boxes or t not in boxes:raise ValueError('unknown endpoint')
        x,y,bw,bh,_=boxes[s]; tx,ty,tw,th,_=boxes[t]
        sx=x+bw/2; sy=y+bh; ex=tx+tw/2; ey=ty
        out+=[f'<path d="M{sx:g},{sy:g} L{ex:g},{ey:g}" stroke="#65758b" fill="none" stroke-dasharray="5 4" marker-end="url(#arrow)"/>',f'<text x="{(sx+ex)/2:g}" y="{(sy+ey)/2-5:g}" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" fill="#36445b">{esc(label)}</text>']
    for ident,lines in nodes.items():
        x,y,bw,bh,style=boxes[ident];fill,stroke=PALETTE[style];out+=[f'<rect x="{x}" y="{y}" width="{bw}" height="{bh}" rx="10" fill="{fill}" stroke="{stroke}" stroke-width="2"/>']
        top=y+bh/2-(len(lines)-1)*14
        for i,line in enumerate(lines):
            size=24 if i==0 else 20
            # Conservative Arial estimate rejects clipped lines before generation.
            if len(line)*size*.57>bw-30 or len(lines)*28>bh-18:raise ValueError('text exceeds box '+ident)
            out += [f'<text x="{x+bw/2:g}" y="{top+i*28:g}" dominant-baseline="middle" text-anchor="middle" font-family="Arial, sans-serif" font-size="{size}" font-weight="{600 if i==0 else 400}" fill="#25334a">{esc(line)}</text>']
    out+=['</svg>'];return '\n'.join(out)+'\n'

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');args=p.parse_args()
    d=json.loads((ROOT/'BIPKB_Machine_Reference.json').read_text()); outputs={ROOT/'BIPKB_Scientific_Reference_Register.md':scientific(d)}
    outputs.update({s.with_suffix('.svg'):diagram(s) for s in sorted((ROOT/'assets/diagrams').glob('*.mmd'))})
    for path,text in outputs.items():
        if args.check:
            if not path.exists() or path.read_bytes()!=text.encode('utf-8'):raise SystemExit('Presentation drift: '+str(path))
        else:path.write_text(text,encoding='utf-8')
    print('PASS: deterministic Scientific Register and diagram parity.' if args.check else 'Generated Scientific Register and SVG diagrams from their authorities.')
if __name__=='__main__':main()
