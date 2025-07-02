import json, pathlib
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# === 初始化嵌入模型 ===
MODEL = SentenceTransformer("all-MiniLM-L6-v2")

# === 读取示例库 ===
DB_PATH = pathlib.Path(__file__).with_name("data") / "examples.json"
EXAMPLES = json.loads(DB_PATH.read_text(encoding="utf-8"))

# === 计算示例嵌入矩阵 ===
EMB_MATRIX = MODEL.encode([e["part"] + " " + e["material"] for e in EXAMPLES])

def fetch_examples(part: str, material: str, k: int = 2):
    """
    检索与 (part + material) 最相似的 k 个示例。
    返回示例中的 detail 字段（加工步骤列表）。
    """
    q_emb = MODEL.encode([part + " " + material])
    sims = cosine_similarity(q_emb, EMB_MATRIX)[0]
    top_idx = sims.argsort()[-k:][::-1]
    return [EXAMPLES[i]["detail"] for i in top_idx]
