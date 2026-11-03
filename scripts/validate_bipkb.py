#!/usr/bin/env python3
"""Read-only BIPKB documentary preservation checks; no scientific or rights assurance."""
import argparse
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
COLLECTIONS=('records','references','classifications','memberships','relationships','examples','methodological_notes','research_queue','assertions')
PINS={'A1':'8b3741f4c658e40d2d67db2fc6a56c821856f0908f2d2fc6437fa18908ccaa99','A1-REVIEW':'c35f262efe3f229534d358d643782f9fab9ee458dc4336eab42242f1512aa210','A2':'fbf24240c00dd28a5150b2388eaf605831a3e73df0400a8b225392875775fa6e'}
COUNTS=dict(zip('DNSGCETRIOHBUKXFLQZ',[11,5,16,4,25,15,25,35,8,10,24,10,12,8,24,14,15,12,20]))
STATUS={'documentary_inclusion':'included-candidate','proposal_review':'pending','canonical_source_lifecycle':'not-established','scientific_verification':'unverified','access':'not-assessed','reuse_rights':'unknown'}
spec=importlib.util.spec_from_file_location('bipkb_render',ROOT/'scripts/render_bipkb.py');renderer=importlib.util.module_from_spec(spec);spec.loader.exec_module(renderer)

def load(path):
    def unique(pairs):
        d={}
        for k,v in pairs:
            if k in d:raise ValueError('duplicate JSON key: '+k)
            d[k]=v
        return d
    def nonfinite(value):raise ValueError('non-finite number: '+value)
    return json.loads(path.read_text(encoding='utf-8'),object_pairs_hook=unique,parse_constant=nonfinite)

def check_shape(value,rule,path='$',errors=None):
    """Closed schema subset used by this local edition, including disjoint oneOf."""
    if errors is None:errors=[]
    if 'oneOf' in rule:
        matches=[r for r in rule['oneOf'] if not check_shape(value,r,path,[])]
        if len(matches)!=1:errors.append(path+': must match exactly one typed shape')
        return errors
    kind=rule['type'];valid={'object':isinstance(value,dict),'array':isinstance(value,list),'string':isinstance(value,str),'integer':type(value)is int}[kind]
    if not valid:errors.append(path+': expected '+kind);return errors
    if 'const' in rule and value!=rule['const']:errors.append(path+': wrong fixed value')
    if kind=='object':
        for k in rule['required']:
            if k not in value:errors.append(path+': missing '+k)
        for k,v in value.items():
            if k not in rule['properties']:errors.append(path+': unsupported '+k)
            else:check_shape(v,rule['properties'][k],path+'.'+k,errors)
    elif kind=='array':
        if len(value)<rule.get('minItems',0) or len(value)>rule.get('maxItems',len(value)):errors.append(path+': wrong item count')
        if rule.get('uniqueItems') and len({json.dumps(x,sort_keys=True) for x in value})!=len(value):errors.append(path+': duplicate items')
        for i,v in enumerate(value):check_shape(v,rule['items'],path+'['+str(i)+']',errors)
    elif kind=='string' and (len(value)<rule.get('minLength',0) or not value.strip()):errors.append(path+': empty string')
    elif kind=='integer' and value<rule.get('minimum',value):errors.append(path+': below minimum')
    return errors

def cells(line):return [x.strip().strip('`') for x in line.strip().strip('|').split('|')]

def validate(data,schema):
    errors=check_shape(data,schema)
    if errors:return errors
    def require(ok,message):
        if not ok:errors.append(message)
    byid={};collections={}
    for c in COLLECTIONS+('provenance','source_editions','unindexed_material','identity_review','supplementary_material'):
        for x in data[c]:
            require(x['id'] not in byid,'duplicate local identity: '+x['id']);byid[x['id']]=x;collections[x['id']]=c
    prov={p['id']:p for p in data['provenance']};origin={p['origin_id']:p for p in prov.values()}
    require(len(origin)==293,'origin identity coverage differs')
    expected={f'BIPKB-A1-{f}{i:03}' for f,n in COUNTS.items() for i in range(0 if f=='G' else 1,n if f=='G' else n+1)}
    require(set(origin)==expected,'missing, extra or reused A1 identity')
    require(data['metadata']['origin_family_counts']==COUNTS,'family counts differ')
    require(data['metadata']['origin_row_count']==293,'origin count differs')
    require(data['metadata']['research_record_count']==len(data['records']),'record count differs')
    require(data['metadata']['collection_counts']=={c:len(data[c]) for c in COLLECTIONS},'collection counts differ')
    require(data['metadata']['document_version']==data['metadata']['corpus_revision']=='0.2.0','corpus/document version disagreement')
    require(data['metadata']['schema_version']=='0.2.0' and data['metadata']['protocol_edition']=='0.2.0','unsupported independent format/protocol edition')
    require(data['metadata']['drm_conformance']=='not claimed','unsupported conformance claim')
    require({s['id']:s['sha256'] for s in data['source_editions']}==PINS,'evidence edition pin changed')
    contexts={x['id'] for x in data['unindexed_material'] if x['source']=='A1'}
    for source in ['A1','A2']:
        text=renderer.source_text(data,source);b=text.encode('utf-8');lines=text.splitlines(keepends=True)
        require(hashlib.sha256(b).hexdigest()==PINS[source],source+': original bytes/caveats lost')
        require(len(b)==next(s['bytes'] for s in data['source_editions'] if s['id']==source),source+': byte count differs')
        for p in data['unindexed_material']:
            if p['source']==source:require(''.join(lines[p['start_line']-1:p['end_line']])==p['text'],source+': unindexed locator invalid')
        for pv in prov.values():
            p=pv if source=='A1' else pv['a2'];line=p['line']
            require(line<=len(lines) and lines[line-1]==p['raw_line'],source+': row locator invalid')
            if source=='A1':
                # Resolve the actual preceding table header, not just a supplied label.
                headers=[]
                for i in range(line-2,-1,-1):
                    if re.match(r'^\|\s*:?-',lines[i]):headers=[v.strip() for v in lines[i-1].strip().strip('|').split('|')][1:];break
                require(headers==pv['headers'],'source table header mismatch')
                require(pv['origin_id']==cells(pv['raw_line'])[0],'row identity mismatch')
                e=byid.get(pv['target']);require(e is not None and collections.get(pv['target'])==pv['target_collection'],'dangling target')
                if e is None:continue
                values=[v.strip() for v in pv['raw_line'].strip().strip('|').split('|')][1:]
                require(e.get('fields')==dict(zip(pv['headers'],values)),'original field dropped or rewritten: '+pv['origin_id'])
                require(e['provenance']==[pv['id']],'wrong origin provenance')
                require(set(pv['inherited_context'])==contexts,'lost inherited qualifications')
                a2=pv['a2'];v=cells(a2['raw_line']);require(v[0]==pv['origin_id'] and f'A1 line {line};' in v[-1],'A2 origin locator mismatch')
                require(a2['recommended_type']==v[2] and a2['recommended_disposition']==v[3] and a2['limits']==v[4],'A2 recommendation changed')
                if pv['origin_id'].startswith('BIPKB-A1-D'):
                    s=e['fields']['Status'];authority='mixed-user-and-assistant' if 'C-ASST' in s and 'C-USER' in s else ('user-reported' if 'C-USER' in s else 'assistant-reported')
                    require(e['reported_authority']==authority and 'no original' in e['authority_evidence'],'false decision authority promotion')
            # A2 source dossiers' raw text is preserved independently of original full fields.
    for c in COLLECTIONS:
        for e in data[c]:
            require(e.get('status')==STATUS,'unsupported verification/lifecycle/rights promotion: '+e['id'])
            if c!='assertions':require(bool(e.get('provenance')) and set(e.get('provenance',[])).issubset(prov),'invalid provenance')
    for e in data['examples']:require(e['empirical_status']=='illustrative-only','example promoted to empirical observation')
    for e in data['classifications']:require(e['adoption']=='not-adopted','scheme adopted without authority')
    require(not data['memberships'],'unapproved inferred membership')
    for e in data['relationships']:
        require(e['subject']=={'kind':'unresolved-label','label':e['fields']['Subject'],'reason':'No approved identity mapping'} and e['object']=={'kind':'unresolved-label','label':e['fields']['Object'],'reason':'No approved identity mapping'},'unresolved endpoint lost or silently resolved')
        require(e['predicate']==e['fields']['Relation'] and e['qualification']==e['fields']['Status / warning'],'relationship meaning/warning lost')
        require(e['relationship_review']=='pending; not approved','relationship falsely approved')
    a2lines=renderer.source_text(data,'A2').splitlines(keepends=True)
    require(len(data['assertions'])==12,'correction coverage lost')
    for e in data['assertions']:
        require(e['line']<=len(a2lines) and a2lines[e['line']-1]==e['raw_line'],'correction locator invalid')
        v=cells(e['raw_line']);require(e['origin_ids']==[v[0]] and v[0] in origin,'correction origin invalid')
        require(e['targets']==[origin[v[0]]['target']] if v[0] in origin else False,'correction target invalid')
        require([e['correction_type'],e['assertion'],e['evidence_origin'],e['verification_limit']]==v[1:],'correction assertion rewritten')
    for x in data['identity_review']:require(set(x['origins']).issubset(origin),'dangling identity question')
    require(data['metadata']['additional_recovered_evidence_units']==len(data['supplementary_material'])==1,'recovered evidence count differs')
    for fragment in data['supplementary_material']:
        require(hashlib.sha256(fragment['text'].encode()).hexdigest()==fragment['fragment_sha256']=='659d3fee858926fe5c78f35cca4b57847cfaaef5ab307639423cd226ddd24c2f','retrieved fragment bytes changed')
        require(fragment['retrieved_character_count']==len(fragment['text'])==20000 and fragment['retrieved_line_count']==len(fragment['text'].splitlines()),'fragment locator/count differs')
        require(fragment['status']==STATUS and set(fragment['origin_links']).issubset(origin),'supplementary provenance/status invalid')
        require(fragment['message_id']=='0a305b40-aa9f-4282-b7f8-c8603309996a' and fragment['speaker']=='assistant','recovered attribution changed')
    return errors

def presentation_errors(data,root=ROOT):
    errors=[]
    if (root/'BIPKB_Scientific_Reference_Register.md').read_text()!=renderer.scientific(data):errors.append('Scientific Register presentation drift')
    readme=(root/'README.md').read_text();requiretext='**Corpus revision:** '+data['metadata']['corpus_revision']
    if requiretext not in readme:errors.append('README corpus revision differs')
    for c in COLLECTIONS:
        if f'| {c.replace("_", " ")} | {len(data[c])} |' not in readme:errors.append('README count differs: '+c)
    if '![BIPKB' not in readme.split('##',1)[0]:errors.append('federation diagram not near top')
    for src in (root/'assets/diagrams').glob('*.mmd'):
        if src.with_suffix('.svg').read_text()!=renderer.diagram(src):errors.append('SVG drift: '+src.name)
    # Local documentation targets, explicit anchors and ordered GitHub-style slugs.
    for path in root.rglob('*.md'):
        text=path.read_text()
        for target in re.findall(r'\]\(([^)]+)\)',text):
            if re.match(r'^[a-z]+:',target) or target.startswith('//'):continue
            relative,_,fragment=target.partition('#');dest=(path.parent/relative).resolve() if relative else path
            if not dest.is_file():errors.append('missing link: '+str(path.name)+' -> '+target);continue
            if fragment and dest.suffix=='.md':
                body=dest.read_text();anchors=set(re.findall(r'<a id="([^"]+)"',body));seen={}
                for heading in re.findall(r'^#{1,6} (.+)$',body,re.M):
                    slug=re.sub(r'[^\w\- ]','',heading.lower()).replace(' ','-');n=seen.get(slug,0);seen[slug]=n+1;anchors.add(slug+(f'-{n}' if n else ''))
                if fragment not in anchors:errors.append('missing anchor: '+target)
    return errors

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--input',type=Path,default=ROOT/'BIPKB_Machine_Reference.json');parser.add_argument('--source-dir',type=Path);args=parser.parse_args()
    try:
        data=load(args.input);schema=load(ROOT/'BIPKB_Machine_Reference.schema.json');errors=validate(data,schema)
        if not errors:errors+=presentation_errors(data)
        if args.source_dir:
            for s in data['source_editions']:
                b=(args.source_dir/s['file']).read_bytes()
                if hashlib.sha256(b).hexdigest()!=s['sha256']:errors.append('external source changed: '+s['file'])
            print('External archived source hashes checked.')
        try:import jsonschema
        except ImportError:print('Optional full JSON Schema check unavailable (not installed); closed local schema checks ran.')
        else:
            jsonschema.Draft202012Validator.check_schema(schema);errors+=['JSON Schema: '+e.message for e in jsonschema.Draft202012Validator(schema).iter_errors(data)];print('Optional full Draft 2020-12 schema check completed.')
    except (OSError,ValueError,KeyError) as e:print('Input error: '+str(e),file=sys.stderr);return 2
    if errors:
        print('\n'.join(errors),file=sys.stderr);return 1
    print('PASS: 293 IDs, complete original fields/context, pinned editions, independent statuses, references, corrections, deterministic presentation, links and SVGs.')
    print('No scientific, rights, genuine authority, original-chat completeness or DRM conformance assurance.');return 0
if __name__=='__main__':sys.exit(main())
