import unittest
from backend import server
class ConversationTests(unittest.TestCase):
 def test_followup_context_kept(self):
  history=[{'role':'user','content':'Explain RAG'},{'role':'assistant','content':'RAG retrieves document passages.'}]
  messages=server.messages_for('Et plus simplement ?', 'fr', history)
  self.assertEqual(messages[1:-1],history)
  self.assertIn('Reply language: fr',messages[0]['content'])
 def test_greeting_without_sales(self):
  result=server.render({'intent':'explain','resource_ids':['pdf-chatbot'],'explanation':'Hi! What would you like to explore?'},'en','Hi')
  self.assertEqual(result['resources'],[])
  self.assertEqual(result['answer'],'Hi! What would you like to explore?')
 def test_fallback_not_ai_and_no_invented_price(self):
  for lang in ['en','fr']:
   result=server.fallback(lang)
   self.assertFalse(result['ai'])
   self.assertEqual(result['resources'][0]['price'],'Free' if lang=='en' else 'Gratuit')
