import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'backend'))
import server
from build_catalog import build
class CatalogTests(unittest.TestCase):
    def test_catalog_current(self):self.assertEqual(build(),server.CATALOG)
    def test_verified_prices_only(self):
        value=server.render({'intent':'recommend','resource_ids':['pdf-chatbot','made-up'],'explanation':'It costs €999'},'en')
        self.assertEqual(value['resources'][0]['price'],'€5');self.assertNotIn('999',json.dumps(value));self.assertEqual(len(value['resources']),1)
    def test_explicit_product_overrides_bad_routing(self):
        answer=server.render({'intent':'contact','resource_ids':['contact']},'en','Can I buy Python for AI Beginners now?')
        self.assertEqual(answer['resources'][0]['id'],'python-for-ai-beginners')
        self.assertNotIn('checkout',answer['resources'][0])
    def test_free_budget_enforced(self):
        answer=server.render({'intent':'recommend','resource_ids':['ai-nlp-fundamentals']},'en','Recommend free resources for a beginner')
        self.assertTrue(answer['resources'])
        self.assertTrue(all(r['price']=='Free' for r in answer['resources']))
    def test_concept_has_no_unsolicited_purchase(self):
        answer=server.render({'intent':'explain','resource_ids':['ai-nlp-fundamentals'],'explanation':'RAG retrieves relevant passages before generating an answer.'},'en','Explain RAG')
        self.assertEqual(answer['resources'],[])
    def test_planned_never_checkout(self):
        for x in server.CATALOG:
            if x['status'] in ('coming_soon','planned_service'):
                self.assertNotIn('checkout',server.resource(x,'en'));self.assertNotIn('download',server.resource(x,'fr'))
    def test_explanation_commercial_guard(self):
        for text in ['The course is free.','Le prix est de 99 euros.','Buy https://bad.test','GHINOVA has a discount.']:
            self.assertNotEqual(server.render({'intent':'explain','explanation':text},'en')['answer'],text)
