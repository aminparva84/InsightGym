#!/usr/bin/env python3
"""Test embedding API - run from backend dir: python test_embedding.py"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

import requests

def test():
    api_key = (
        os.getenv("GOOGLE_API_KEY") or
        os.getenv("GEMINI_API_KEY") or
        os.getenv("VERTEX_API_KEY") or
        ""
    ).strip()
    if not api_key:
        try:
            from app import app
            with app.app_context():
                from services.ai_provider import get_provider_api_key, _get_settings
                for p in ("vertex", "gemini"):
                    k, _ = get_provider_api_key(p, _get_settings())
                    if k:
                        api_key = k
                        print(f"Using key from Admin ({p})")
                        break
        except Exception as e:
            print(f"Could not load from DB: {e}")
    if not api_key:
        print("Set GOOGLE_API_KEY or GEMINI_API_KEY in .env, or configure Vertex/Gemini in Admin")
        return

    model = os.getenv("VERTEX_EMBEDDING_MODEL", "text-embedding-004")
    endpoint = f"https://aiplatform.googleapis.com/v1/publishers/google/models/{model}:predict"
    payload = {"instances": [{"content": "Hello world"}]}
    print(f"\nVertex predict (Real_State style, no project_id): ...{model}:predict?key=***")
    r = requests.post(endpoint, params={"key": api_key}, json=payload, timeout=30)
    print(f"Status: {r.status_code} | {r.text[:200]}")
    if r.status_code == 200:
        data = r.json()
        vals = (data.get("predictions") or [{}])[0].get("embeddings", {}).get("values")
        print(f"SUCCESS. Embedding dims: {len(vals) if vals else 0}")
    return r.status_code

if __name__ == "__main__":
    test()
