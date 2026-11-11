import os
import unittest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from app.main import app


class TriageTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def tearDown(self):
        self.client.close()

    def test_invalid_response_repaired_once(self):
        broken = {"choices": [{"message": {"content": '{"category":"unknown"}'}}], "usage": {}}
        fixed = {"choices": [{"message": {"content": '{"category":"billing","urgency":"medium","suggested_team":"billing","confidence":0.9}'}}], "usage": {}}
        with patch.dict(os.environ, {"LLM_ENABLED": "true", "LLM_STUB": "0"}), patch('app.triage.model_call', new_callable=AsyncMock, side_effect=[broken, fixed]) as call:
            response = self.client.post('/triage', json={'message': 'I was charged twice'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['category'], 'billing')
        self.assertEqual(call.await_count, 2)

    def test_missing_choices_cannot_crash_repair(self):
        with patch.dict(os.environ, {"LLM_ENABLED": "true", "LLM_STUB": "0"}), patch('app.triage.model_call', new_callable=AsyncMock, return_value={'choices': [], 'usage': {}}) as call:
            response = self.client.post('/triage', json={'message': 'Malformed output test'})
        self.assertEqual(response.status_code, 422)
        self.assertEqual(call.await_count, 2)
        self.assertNotIn('choices', response.text)


if __name__ == '__main__':
    unittest.main()
