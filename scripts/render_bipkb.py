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

def nested_diagram(source):
    """Render the canonical annotated Mermaid group/text subset, without an engine dependency.

    Palette, text metrics and layout come from the source, as in OSDS/EIRKB.
    This branch leaves the earlier conceptual-map rendering byte-identical.
    """
    import xml.etree.ElementTree as ET
    text = source.read_text(encoding='utf-8')
    width, height = map(int, re.search(r'^%% @canvas (\d+) (\d+)$', text, re.M).groups())
    title = re.search(r'^%% @title (.+)$', text, re.M)[1]
    description = re.search(r'^%% @description (.+)$', text, re.M)[1]
    labels = dict(re.findall(r'^\s*(?:subgraph\s+)?(\w+)\["([^"\n]+)"\]', text, re.M))
    hints = re.findall(r'^%% @(box|group) (\w+) (\d+) (\d+) (\d+) (\d+) (\w+)$', text, re.M)
    boxes = {n: tuple(map(int, (x, y, w, h))) for _, n, x, y, w, h, _ in hints}
    styles = {n: dict(item.split(':', 1) for item in values.split(','))
              for n, values in re.findall(r'^\s*classDef (\w+) ([^\n;]+);', text, re.M)}
    if set(boxes) != set(labels) or len(boxes) != len(hints):
        raise ValueError('Every unique label needs exactly one layout hint')
    # Validate actual Mermaid nesting against the supplied layout, not just drawn rectangles.
    stack = []
    for line in text.splitlines():
        group = re.match(r'^\s*subgraph (\w+)\[', line)
        node = re.match(r'^\s*(\w+)\[', line)
        name = group[1] if group else node[1] if node else None
        if name and stack:
            x, y, w, h = boxes[name]; px, py, pw, ph = boxes[stack[-1]]
            if not (px <= x and py <= y and x+w <= px+pw and y+h <= py+ph):
                raise ValueError('Nested item outside parent: '+name)
        if group: stack.append(name)
        elif line.strip() == 'end':
            if not stack: raise ValueError('Unmatched Mermaid end')
            stack.pop()
    if stack: raise ValueError('Unclosed Mermaid subgraph')
    esc = html.escape
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
           f'<title id="title">{esc(title)}</title><desc id="desc">{esc(description)}</desc>',
           '<defs><marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10z" fill="#637286"/></marker></defs>',
           '<rect width="100%" height="100%" fill="#ffffff"/>',
           '<g font-family="Arial, Helvetica, sans-serif" text-anchor="middle">']
    for a, relationship, b in re.findall(r'^\s*(\w+) (<-->|-->) (\w+)\s*$', text, re.M):
        ax, ay, aw, ah = boxes[a]; bx, by, bw, bh = boxes[b]
        if by <= ay+ah: raise ValueError('Layer connectors must run downward')
        start = ' marker-start="url(#arrow)"' if relationship == '<-->' else ''
        out.append(f'<path d="M{ax+aw/2:g} {ay+ah+4} L{bx+bw/2:g} {by-5}" fill="none" stroke="#637286" stroke-width="1.6" marker-end="url(#arrow)"{start}/>')
    for kind, name, _, _, _, _, role in hints:
        x, y, w, h = boxes[name]; style = styles[role]
        if not (0 <= x < x+w <= width and 0 <= y < y+h <= height): raise ValueError('Outside canvas: '+name)
        dash = ' stroke-dasharray="6 4"' if name == 'DRM' else ''
        out.append(f'<rect id="box-{name}" x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{style["fill"]}" stroke="{style["stroke"]}" stroke-width="{style.get("stroke-width", "1.5")}"{dash}/>')
        hint = re.search(r'^%% @text '+name+r' ([\d.,]+) ([\d.,]+) ([\d,]+)$', text, re.M)
        if not hint: raise ValueError('Missing typography: '+name)
        sizes, offsets, weights = [list(map(float, values.split(','))) for values in hint.groups()]
        lines = labels[name].split('<br/>')
        if not len(lines) == len(sizes) == len(offsets) == len(weights): raise ValueError('Typography count: '+name)
        for line, size, offset, weight in zip(lines, sizes, offsets, weights):
            if not (offset-size*.8 > 0 and offset+size*.25 < h): raise ValueError('Vertical text bounds: '+name)
            out.append(f'<text data-box="{name}" x="{x+w/2:g}" y="{y+offset:g}" font-size="{size:g}" font-weight="{weight:g}" fill="{style["color"]}">{esc(line)}</text>')
    out.append('</g></svg>')
    svg = '\n'.join(out)+'\n'
    ET.fromstring(svg)
    return svg


def diagram(source):
    """Render a deliberately small annotated Mermaid subset; reject unsupported graphs."""
    if re.search(r'^%% @group ', source.read_text(), re.M):
        return nested_diagram(source)
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
