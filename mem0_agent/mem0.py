from mem0 import Memory
import os

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
config = {
    "version": "v1.1",

    # Embeddings (Gemini via OpenRouter)
    "embedder": {
        "provider": "openai", 
        "config": {
            "api_key": OPENROUTER_API_KEY,
            "base_url": "https://openrouter.ai/api/v1",
            "model": "google/text-embedding-3-small"
        }
    },

    # LLM (Gemini via OpenRouter)
    "llm": {
        "provider": "openai",
        "config": {
            "api_key": OPENROUTER_API_KEY,
            "base_url": "https://openrouter.ai/api/v1",
            "model": "google/gemini-1.5-flash"
        }
    },

    #  Vector Store
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "host": "localhost",
            "port": 6333
        }
    }
}
mem_client= Memory.from_config(config)
