import os
import requests
import re
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

class PerplexityClient:
    def __init__(self):
        self.api_key = os.getenv('PERPLEXITY_API_KEY')
        if not self.api_key:
            raise ValueError("PERPLEXITY_API_KEY not set")
        self.base_url = 'https://api.perplexity.ai/chat/completions'
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
        }
        # session with retries
        self.session = requests.Session()
        retries = Retry(total=3, backoff_factor=1,
                        status_forcelist=[500,502,503,504])
        self.session.mount('https://', HTTPAdapter(max_retries=retries))

    def query(self, prompt, model=None):
        if model is None:
            model = os.getenv('PERPLEXITY_MODEL', 'sonar-small-chat')

        payload = {
            'model': model,
            'messages': [
                {'role': 'system', 'content': 'You are a market research expert. Provide concise, data-driven responses with citations.'},
                {'role': 'user', 'content': prompt}
            ],
            'max_tokens': 1500,
            'temperature': 0.7,
        }

        response = self.session.post(self.base_url, json=payload, headers=self.headers)
        if response.status_code == 200:
            data = response.json()
            answer = data['choices'][0]['message']['content']
            citations = self._extract_citations(answer)
            return answer, citations
        else:
            # parse error details
            try:
                error_json = response.json()
                error_msg = error_json.get("error", {}).get("message", "")
            except:
                error_msg = response.text

            if response.status_code == 400 and "invalid model" in error_msg.lower():
                # fallback to alternate model
                fallback = os.getenv('PERPLEXITY_FALLBACK_MODEL', 'sonar-pro')
                if model != fallback:
                    return self.query(prompt, fallback)
            raise Exception(f"API error {response.status_code}: {error_msg}")

    def _extract_citations(self, content):
        citations = []
        matches = re.findall(r'\[(\d+)\]\s*(https?://[^\s\]]+)', content)
        for num, url in matches:
            citations.append({'id': num, 'source': url})
        if not citations:
            urls = re.findall(r'https?://[^\s\]]+', content)
            for i, url in enumerate(urls[:10], 1):
                citations.append({'id': str(i), 'source': url})
        return citations
