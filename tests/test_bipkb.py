"""Bounded preservation regressions; no archive, network or writable temp area required."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('bipkb_validator',ROOT/'scripts/validate_bipkb.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)

class DocumentaryPreservationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original=v.load(ROOT/'BIPKB_Machine_Reference.json');cls.schema=v.load(ROOT/'BIPKB_Machine_Reference.schema.json')
    def setUp(self):self.data=copy.deepcopy(self.original)
    def reject(self):self.assertTrue(v.validate(self.data,self.schema))
    def test_valid_documentary_intake(self):self.assertEqual(v.validate(self.data,self.schema),[])
    def test_all_293_origins_and_nineteen_families(self):
        self.assertEqual(len(self.data['provenance']),293);self.assertEqual(len(self.data['metadata']['origin_family_counts']),19)
    def test_both_source_editions_reconstructed_exactly(self):
        for source in ['A1','A2']:self.assertEqual(hashlib.sha256(v.renderer.source_text(self.data,source).encode()).hexdigest(),v.PINS[source])
    def test_dropped_original_column_rejected(self):
        self.data['records'][0]['fields'].pop('Important distinction / question');self.reject()
    def test_full_relationship_object_preserved(self):
        self.data['relationships'][0]['fields']['Object']='Wrong object';self.reject()
    def test_lost_caveat_rejected(self):
        self.data['unindexed_material'][0]['text']=self.data['unindexed_material'][0]['text'].replace('not a claim','a claim');self.reject()
    def test_lost_inherited_context_rejected(self):
        self.data['provenance'][0]['inherited_context'].pop();self.reject()
    def test_duplicate_ids_rejected(self):
        self.data['records'][1]['id']=self.data['records'][0]['id'];self.reject()
    def test_cross_collection_duplicate_rejected(self):
        self.data['references'][0]['id']=self.data['records'][0]['id'];self.reject()
    def test_missing_origin_rejected(self):self.data['provenance'].pop();self.reject()
    def test_dangling_provenance_rejected(self):
        self.data['records'][0]['provenance']=['BIPKB:PV-missing'];self.reject()
    def test_dangling_target_rejected(self):
        self.data['provenance'][0]['target']='BIPKB:NOTE-missing';self.reject()
    def test_false_scientific_verification_rejected(self):
        self.data['records'][0]['status']['scientific_verification']='verified';self.reject()
    def test_false_rights_grant_rejected(self):
        self.data['records'][0]['status']['reuse_rights']='open';self.reject()
    def test_false_proposal_approval_rejected(self):
        self.data['records'][0]['status']['proposal_review']='accepted';self.reject()
    def test_assistant_proposal_not_promoted_to_user_decision(self):
        self.data['methodological_notes'][0]['reported_authority']='user-reported';self.reject()
    def test_decision_status_not_overwritten(self):
        self.data['methodological_notes'][0]['fields']['Status']='C-USER; DECIDED';self.reject()
    def test_examples_never_empirical(self):
        self.data['examples'][0]['empirical_status']='observed';self.reject()
    def test_relationship_warning_loss_rejected(self):
        self.data['relationships'][0]['qualification']='Unqualified';self.reject()
    def test_relationship_resolution_not_inferred(self):
        self.data['relationships'][0]['subject']['kind']='resolved';self.reject()
    def test_classification_not_adopted(self):
        self.data['classifications'][0]['adoption']='adopted';self.reject()
    def test_membership_not_inferred(self):
        self.data['memberships']=[{'id':'BIPKB:MEM-0001','record':'x','classification':'y','status':'proposed','provenance':'x'}];self.reject()
    def test_locator_drift_rejected(self):
        self.data['provenance'][0]['line']+=1;self.reject()
    def test_correction_original_retained(self):
        p=next(p for p in self.data['provenance'] if p['origin_id']=='BIPKB-A1-H017')
        self.assertIn('Hugo Ellenberg',p['raw_line']);self.assertTrue(any('Heinz Ellenberg' in x['assertion'] for x in self.data['assertions']))
    def test_correction_rewrite_rejected(self):
        self.data['assertions'][0]['assertion']='Different claim';self.reject()
    def test_correction_cannot_claim_verified(self):
        self.data['assertions'][0]['status']['scientific_verification']='verified';self.reject()
    def test_a2_disposition_not_rewritten(self):
        self.data['provenance'][0]['a2']['recommended_disposition']='ACCEPTED';self.reject()
    def test_record_count_mismatch_rejected(self):
        self.data['metadata']['research_record_count']+=1;self.reject()
    def test_independent_version_drift_rejected(self):
        self.data['metadata']['corpus_revision']='1.0.0';self.reject()
    def test_no_conformance_promotion(self):
        self.data['metadata']['drm_conformance']='conformant';self.reject()
    def test_source_pin_not_relabelled(self):
        self.data['source_editions'][0]['sha256']='0'*64;self.reject()
    def test_recovered_fragment_not_silently_rewritten(self):
        self.data['supplementary_material'][0]['text']+='Invented continuation';self.reject()
    def test_recovered_fragment_not_verified(self):
        self.data['supplementary_material'][0]['status']['scientific_verification']='verified';self.reject()
    def test_recovered_fragment_not_user_decision(self):
        self.data['supplementary_material'][0]['speaker']='user';self.reject()
    def test_unknown_not_silently_absent(self):
        self.data['records'][0]['fields']['Status']='ABSENT';self.reject()
    def test_register_and_diagram_parity(self):self.assertEqual(v.presentation_errors(self.data),[])
    def test_deterministic_generation(self):
        self.assertEqual(v.renderer.scientific(self.data),v.renderer.scientific(copy.deepcopy(self.data)))
        for path in (ROOT/'assets/diagrams').glob('*.mmd'):self.assertEqual(v.renderer.diagram(path),v.renderer.diagram(path))
    def test_presentation_drift_rejected(self):
        original=Path.read_text
        def read(path,*a,**kw):
            text=original(path,*a,**kw)
            return text+'\nChanged copy\n' if path.name=='BIPKB_Scientific_Reference_Register.md' else text
        with patch.object(Path,'read_text',read):self.assertIn('Scientific Register presentation drift',v.presentation_errors(self.data))
    def test_svg_accessible_and_all_labels_present(self):
        ns={'s':'http://www.w3.org/2000/svg'}
        for path in (ROOT/'assets/diagrams').glob('*.mmd'):
            tree=ET.fromstring(v.renderer.diagram(path));self.assertIsNotNone(tree.find('s:title',ns));self.assertIsNotNone(tree.find('s:desc',ns))
            self.assertEqual(tree.attrib['role'],'img');self.assertTrue(tree.findall('s:rect',ns))
    def test_reconstruction_not_called_original(self):
        self.assertIn('NOT the original',(ROOT/'assets/diagrams/bipkb_conceptual_reconstruction.mmd').read_text())
        self.assertIn('not the original conversation diagram',(ROOT/'README.md').read_text())
    def test_ambiguous_json_keys_rejected(self):
        class Input:
            def read_text(self,**kw):return '{"a":1,"a":2}'
        with self.assertRaises(ValueError):v.load(Input())
    def test_nonfinite_json_rejected(self):
        class Input:
            def read_text(self,**kw):return '{"a":NaN}'
        with self.assertRaises(ValueError):v.load(Input())
if __name__=='__main__':unittest.main()
