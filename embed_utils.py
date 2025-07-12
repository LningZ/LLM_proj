import json
import pathlib
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# === Initialize embedding model ===
# Using MiniLM for sentence-level semantic encoding
MODEL = SentenceTransformer("all-MiniLM-L6-v2")

# === Load machining examples from JSON database ===
# File: ./data/examples.json
# Format: List[{"part": str, "material": str, "detail": List[Dict]}]
DB_PATH = pathlib.Path(__file__).with_name("data") / "examples.json"
EXAMPLES = json.loads(DB_PATH.read_text(encoding="utf-8"))

# === Precompute embeddings for all (part + material) in the example database ===
# Each input: a single string like "aluminum bracket"
EMB_MATRIX = MODEL.encode([
    example["part"] + " " + example["material"] for example in EXAMPLES
])

def fetch_examples(part: str, material: str, k: int = 2):
    """
    Fetch the top-k most similar machining examples given a part and material.
    
    Args:
        part (str): Part description, e.g. "bracket"
        material (str): Material name, e.g. "aluminum"
        k (int): Number of top similar examples to return (default: 2)

    Returns:
        List[List[Dict]]: A list of 'detail' fields from the top-k examples.
                          Each detail is a list of machining steps (dicts).
    """
    # Encode the input query as a single string
    query_text = part + " " + material
    q_emb = MODEL.encode([query_text])  # shape: (1, emb_dim)

    # Compute cosine similarity with all stored examples
    sims = cosine_similarity(q_emb, EMB_MATRIX)[0]  # shape: (num_examples,)

    # Get indices of top-k most similar examples (highest similarity)
    top_idx = sims.argsort()[-k:][::-1]

    # Return only the 'detail' field of the top-k examples
    return [EXAMPLES[i]["detail"] for i in top_idx]
