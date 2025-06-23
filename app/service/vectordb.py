import os
from chromadb import PersistentClient
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction


# Resolve path to Chroma DB
CHROMA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "processed", "chroma_store"))

def get_chroma_collections(config):
    openai_key = os.environ.get("OPENAI_API_KEY")
    if not openai_key:
        raise EnvironmentError("OPENAI_API_KEY is not set in the environment.")

    os.environ["CHROMA_OPENAI_API_KEY"] = openai_key
    client = PersistentClient(path=CHROMA_DIR)

    collections = {}

    for framework in config.get("coaching_frameworks", []):
        name = framework.get("name")
        if not name:
            continue  # Skip unnamed frameworks

        collection = client.get_collection(
            name=name,
            embedding_function=OpenAIEmbeddingFunction(model_name="text-embedding-3-small")
        )
        collections[name] = collection

    return collections
