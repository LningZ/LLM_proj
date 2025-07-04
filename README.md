Here is the English version of your README, fully detailed and structured for sharing with teammates or writing reports.

---

## 📂 Project Structure Overview

| Path                     | Description                                                    |
| ------------------------ | -------------------------------------------------------------- |
| `cnc_llm.ipynb`          | Main notebook: UI, pipeline workflow, and result visualization |
| `llm_utils.py`           | OpenAI API interaction, auto-retry logic, and token counting   |
| `requirements.txt`       | Dependencies (`openai · tenacity · pandas · ipywidgets`)       |
| `.env`                   | Private environment file (stores `OPENAI_API_KEY=...`)         |
| `LLMs_projet_note.ipynb` | Early experiments (optional to archive)                        |

---

## 1️⃣ `llm_utils.py` — LLM Interaction Core

```python
load_dotenv()                        # Load .env securely
client = openai.OpenAI(api_key=...)  # OpenAI client initialization
TOKENS_USED: int = 0                 # Global token counter
```

### Function: `chat_completion(prompt, ..., verbose=True)`

> **What it does:**
>
> 1. Uses a fixed `system_prompt` to ensure JSON array outputs.
> 2. Handles errors with `tenacity` — retries up to 3 times with exponential backoff (1–10 seconds).
> 3. Tracks token usage via `response.usage.total_tokens` added to `TOKENS_USED`.
> 4. Has a `verbose` flag — prints raw JSON when debugging, silent in production.

---

## 2️⃣ `cnc_llm.ipynb` — Workflow Breakdown

| Step                 | Functions/Cells                                                     | Logic Description                                                                                                |
| -------------------- | ------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| **UI Setup**         | `desc_input`, `material_selector`, `generate_button`, `output_area` | Built with `ipywidgets`; displayed together at the end with `display(...)`.                                      |
| **Button Callback**  | `on_generate_clicked(b)`                                            | Main pipeline logic.                                                                                             |
| ① Get Outline        | `get_outline(part, material)` → `chat_completion(verbose=False)`    | Returns high-level steps like "Rough Machining".                                                                 |
| ② Get Detailed Plan  | `get_detail(outline, ...)`                                          | Generates JSON array with step, tool, rpm, and feed based on outline.                                            |
| ③ Parse Output       | `parse_llm_output(raw_json)`                                        | Parses JSON into DataFrame with renamed columns.                                                                 |
| ④ Dual Table Display | `df_full_valid` (full process)<br>`df_cut_valid` (machining only)   | • Adds validation columns (`RPM Valid`, `Feed Valid`)<br>• `display_plan_table()` highlights invalid parameters. |
| ⑤ Reflection Summary | `reflect_summary(raw_json, df_full_valid)`                          | Summarizes total steps, invalid counts, token usage, and human oversight suggestions.                            |

> **Function: `validate_plan(df, material)`**
> Checks spindle speed and feed rates against limits based on the material.

> **Function: `highlight_invalid(val)`**
> Returns CSS style (`background-color:#FFD2D2`) for invalid entries.
> Switched from `applymap()` to `map()` (Pandas ≥ 2.2) to avoid deprecation warnings.

---

## 3️⃣ Key Implementation Details

| Feature                | Why It’s Important                                          |
| ---------------------- | ----------------------------------------------------------- |
| `.env + load_dotenv()` | Keeps API keys secure; complies with course requirements.   |
| `TOKENS_USED` Tracking | Adds transparency about token cost for reporting.           |
| Dual Table View        | Shows the full process and highlights only machining steps. |
| `verbose` Flag         | Allows clean UI during runs and full debugging when needed. |

---

## 4️⃣ Next Development Roadmap (Phase 2–6)

| Phase                                       | Goal                                                                                                             | Key Changes                                                        |
| ------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------ |
| **Phase 2 — Chain Prompt + Multi-material** | • Separate `get_outline` and `get_detail` into true two-step prompts.<br>• Add material/tool dropdowns in UI.    | Inject material constraints into the prompt for accurate rpm/feed. |
| **Phase 3 — Externalize Validation Data**   | • Move parameter limits into `materials.json`.<br>• Refactor `validate_plan()` to read dynamically.              | Create `materials.json` and `validation.py`.                       |
| **Phase 4 — Power Check + CSV Export**      | • Implement `add_power_check(df)` for torque/power limits.<br>• Add a save-to-CSV button.                        | Extend UI with `widgets.Button("💾 Export")`.                      |
| **Phase 5 — Few-shot Retrieval**            | • Create embeddings for 5 handcrafted process plans.<br>• Retrieve similar plans dynamically to enhance prompts. | Add `examples/` directory and build `retriever.py`.                |
| **Phase 6 — Auto-Correction Loop**          | • If `RPM Valid` or `Feed Valid` fails, prompt LLM to revise steps automatically.                                | Add retry loops inside `on_generate_clicked()`.                    |

> ✅ Completing Phase 2–4 is enough for high marks.
> 🔥 Phase 5–6 are bonus for innovation.

---

## 5️⃣ Usage Instructions for Teammates

1. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API Key**
   Create a `.env` file in the root directory:

   ```env
   OPENAI_API_KEY=sk-xxxx
   ```

3. **Run the Notebook**
   Open `cnc_llm.ipynb` → Run All

4. **Input**
   Describe your part and select the material → Click **"Generate CNC Plan"**.

5. **Output**

   * **Full Process Plan**: Includes selection, preparation, inspection, etc.
   * **Machining-only Plan**: Filters to only the steps with spindle/feed parameters.

6. **Review the Reflection Summary**
   Understand step count, validation results, and token usage.

7. **Next Steps**
   Follow the development roadmap outlined above to continue upgrading the project.

---

This README fully documents the current work, technical decisions, function logic, and the plan for the next steps. It is suitable both as team documentation and for submitting as part of your project report.










---

### 🚀 Phase 2 — Chain Prompt + Multi-material Support

**Status: ✅ Completed**

### 🔥 Summary of Changes

* ✔️ Upgraded from single-prompt to **chain-prompt architecture**:
  → First ask for a high-level outline (`get_outline()`),
  → Then request detailed steps with parameters (`get_detail()`).

* ✔️ Added a **Material Selector Dropdown** to the UI.
  → Supports 5 materials: **aluminum, steel, brass, titanium, plastic**.

* ✔️ **Material-specific constraints are dynamically injected into prompts.**
  → Example:
  *“For titanium, spindle speed must be 100–500 rpm and feed 50–200 mm/min.”*

* ✔️ Defined a global dictionary `MATERIAL_LIMITS` with rpm/feed ranges for each material.

* ✔️ The validation logic (`validate_plan()`) now automatically checks spindle speed and feed against material constraints.

* ✔️ Output now includes:

  * **Full Process Plan:** Includes setup, fixturing, inspection steps.
  * **Machining-only Plan:** Filters only steps with valid spindle/feed parameters.

* ✔️ Reflection Summary shows:

  * Total steps generated
  * Number of invalid RPM/Feed
  * Token usage
  * Human oversight recommendation

### 💡 Example Improvements (Titanium):

| Before (Incorrect)                  | After (Correct)                       |
| ----------------------------------- | ------------------------------------- |
| Feed = 1000 mm/min (❌ way too high) | Feed = 120 mm/min (✔️ correct)        |
| RPM = 6000 (❌ aluminum speed)       | RPM = 350 (✔️ realistic for titanium) |

---

### 🔗 Phase 3 (Next) – Planned Improvements

* Externalize `MATERIAL_LIMITS` into **`materials.json`** for better scalability.
* Optionally link tool-specific parameters (`tool_catalog.json`).
* Implement power and torque checks.
* Add CSV/Excel export for process plans.

---

### 📍 Files Updated in Phase 2

| File             | Updates                                              |
| ---------------- | ---------------------------------------------------- |
| `cnc_llm.ipynb`  | UI update + chain prompt logic                       |
| `llm_utils.py`   | `get_outline()`, `get_detail()` improved             |
| *Notebook Cells* | `MATERIAL_LIMITS` defined, `validate_plan()` updated |

---

## 📄 README.md (English, updated to Phase 3)

````markdown
# CNC-LLM Process Planner 🛠️🤖

A Python notebook that lets an OpenAI LLM draft, validate and present CNC machining process plans from plain-language part descriptions.

> **Course project**: *LLM-Assisted Process Planning for CNC Machining*

---

## 1. Quick Run

```bash
# install
pip install -r requirements.txt

# put your key in .env
echo "OPENAI_API_KEY=sk-…" > .env
````

Open **`cnc_llm.ipynb`** → *Run All* →
Describe a part → pick a material → **Generate CNC Plan**.

---

## 2. Project Tree

```
ML_pro/
├─ cnc_llm.ipynb      # main demo notebook (UI + pipeline)
├─ llm_utils.py       # LLM wrapper + prompt helpers
├─ validation.py      # rpm/feed + power validation  ← Phase 3
├─ materials.json     # machining limits database  ← Phase 3
├─ requirements.txt
└─ README.md
```

---

## 3. Pipeline Overview

| Stage        | Function                                                 | Details                                                        |
| ------------ | -------------------------------------------------------- | -------------------------------------------------------------- |
| **Outline**  | `get_outline()`                                          | LLM returns JSON list `[{step}]`                               |
| **Detail**   | `get_detail()`                                           | Adds tool, operation, rpm, feed – **material limits injected** |
| **Parse**    | `parse_llm_output()`                                     | JSON → DataFrame                                               |
| **Validate** | `validate_plan()` (rpm/feed)<br>`add_power_check()` (kW) | Adds `RPM Valid, Feed Valid, Power Valid`                      |
| **Display**  | `display_plan_table()`                                   | Full process & machining-only tables, invalid cells red        |
| **Reflect**  | `reflect_summary()`                                      | counts invalids, token cost, human-oversight tips              |

All LLM calls use `chat_completion(messages=…)` with auto-retry and a global token counter.

---

## 4. Material Database (Phase 3)

`materials.json`

| material | rpm (min-max) | feed (min-max) |
| -------- | ------------- | -------------- |
| aluminum | 3000-12000    | 800-1500       |
| steel    | 500-1500      | 100-300        |
| brass    | 1500-6000     | 400-800        |
| titanium | 100-500       | 50-200         |
| plastic  | 2000-8000     | 500-1500       |

`validation.py` loads this database once; adding a new material requires only editing the JSON.

---

## 5. Power Check (Phase 3)

`add_power_check()` estimates spindle power per step

```
Power ≈ cutting force × cutting speed
```

Default limits: Ø10 mm cutter, 5 kW machine, 80 % safety.
`Power Valid` is automatically highlighted.

---

## 6. User Interface

* Textarea for part description
* Dropdown with 5 materials
* **Generate** button
* Two tables with automatic highlighting
* Reflection block with statistics

![screenshot](docs/screenshot.png) <!-- optional -->

---

## 7. Roadmap

| Phase | Goal                          | Status            |
| ----- | ----------------------------- | ----------------- |
| 0-1   | prototype, API safety         | ✅ done            |
| 2     | chain prompts, multi-material | ✅ done            |
| **3** | external DB & power check     | ✅ **this commit** |
| 4     | CSV / Excel export, nicer UI  | planned           |
| 5     | few-shot retrieval examples   | optional          |
| 6     | auto-correction loop          | optional          |

---

## 8. Credits

Implements all required elements of the course rubric:

1. **LLM Call** – clearly shown in `llm_utils.py`
2. **Post-processing** – JSON parsing, DataFrame styling
3. **Validation Logic** – rpm, feed, power checks
4. **Notebook Output** – full & machining-only tables
5. **Reflection Section** – reliability analysis and token cost

Feel free to fork, extend, or integrate into shop-floor tooling!





## ✅ README Update – Phase 4

*(English & 中文双语部分，可直接复制到 README.md “Changelog / 项目进度” 区域)*

---

### 🚀 Phase 4 — Export & UI Polish

**Status:** ✅ *Completed*

#### ✨ What’s new

| Feature                             | Details                                                                                                                                                       |
| ----------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **One-click CSV export**            | • New **“💾 Export CSV”** button<br>• Auto-names file `plan_<material>_<YYYY-MM-DD>.csv`<br>• Saves to notebook folder and shows an in-notebook download link |
| **Shared output area**              | All messages from *Generate* and *Export* now appear in the same `output_area`, keeping the interface tidy                                                    |
| **Reflection shows exported file**  | Summary adds line:<br>`- Exported file : plan_aluminum_2025-06-29.csv`                                                                                        |
| **UI cosmetics**                    | • Horizontal rule (`---`) between Full / Machining tables<br>• Emoji section titles 🗂️ / 🛠️<br>• Download link prefixed with 👉                             |
| **Power column always highlighted** | `display_plan_table()` subset now includes `"Power Valid"`                                                                                                    |

#### 📄 Files touched

| File                   | Key edits                                                       |
| ---------------------- | --------------------------------------------------------------- |
| `cnc_llm.ipynb`        | + export button & callback; UI divider; titles                  |
| `reflect_summary()`    | Adds exported-file line; single display (no duplication)        |
| `display_plan_table()` | Highlights *Power Valid*                                        |
| *(minor)*              | top-level placeholder `df_full_valid = None` to satisfy linters |

---

### 🌟 Typical workflow now

1. Describe part → choose material → **Generate CNC Plan**
2. Review Full & Machining tables (invalid cells in red)
3. Click **Export CSV** → see ✅ message & 👉 download link
4. Reflection Summary lists invalid counts, token usage **and** exported filename

---


### 🔜 Next (Phase 5 / 6) – Optional

* Excel (multi-sheet) export
* Few-shot example retrieval
* Auto-correction loop for invalid parameters

Feel free to copy-paste this section into your README and push with a commit like:

```
docs: update README for Phase 4 – CSV export & UI polish
```


按照plan还要做的，但是基本的应该做完了，readme要重写，这只是为了让你们看懂，所以都是笔记。然后LLMs_projet_note那个文件也是笔记，为最后的rapport写的，你可以看看。


理论上剩这两个阶段

## 🌟 阶段 5–6 加分选项（按精力选做）

1. **向量检索 Few-shot**

   * 用 `sentence_transformers` 把 5 条手工工艺示例嵌入向量库 → 按余弦近邻找最相似示例拼进 prompt。
2. **自动纠错循环**

   * 如果 `RPM Valid` 为 False → 重新调用 LLM 要求修正这些步。
3. **批量 CSV**

   * `parts.csv` 每行一个描述；循环输出多 sheet Excel 并汇总合规率柱状图。

---



今天做了：用 Pydantic 对 LLM 输出做格式校验 + 自动重试
Robust JSON parsing & automatic retry using Pydantic

构建了 OutlineStep 和 DetailStep 数据模型，对 LLM 返回的 JSON 格式进行字段校验。

若格式错误（缺字段、数据类型错误等），会自动触发重试，直到返回合法 JSON 或达到最大重试次数。

极大提升了系统的稳定性、鲁棒性和 AI 输出的可靠性。

2️⃣ ✅ Prompt 中动态注入材料物理约束


根据 materials.json 中的材料参数，自动在 Prompt 中加入当前材料的主轴转速 (RPM) 和进给速度 (Feed) 上下限。

LLM 在生成工艺参数时就会遵守物理约束，避免出现超速、过快进给等物理不合理的数值。

让 LLM 更像一个有“工艺意识”的专业工程师，减少无效输出，提高整体结果质量。


7.2 更新：

### ✅ 这两个方向非常棒，而且是**高级功能**，体现出真正的「AI 工程思维」而不只是 Prompt 调教。

---

## 1️⃣ **向量检索 Few-shot — 质量型优化 ✔️**

### ✔️ 核心思路：

* 不再是死板的 Few-shot 示例，而是基于 **相似零件描述、相似材料** 自动检索最相关的示例。
* 检索到的示例可以拼进 `get_outline()` 和 `get_detail()` 的 Prompt 中，给 LLM 提供强力的上下文引导。

### ✔️ 技术方案：

* 使用 `sentence_transformers`（BGE、小型模型即可）对手工制作的工艺示例向量化。
* 检索方式用 FAISS / sklearn NearestNeighbor（都很轻量）。

### ✔️ 价值：

* LLM 更容易生成结构正确、风格统一的工艺。
* 明显降低 LLM 出错概率，特别适合「冷启动零件」或者「非典型结构」。

### ✔️ 工程上 ✅ 非常推荐。

---

## 2️⃣ **自动纠错循环 — 稳定性提升 ✔️**

### ✔️ 核心逻辑：

* 如果 `validate_plan()` 检查发现某一行 rpm/feed 超限：

  * → 构造一个新的 Prompt：

    > “In step 2 'Rough Machining', the spindle speed 9000 exceeds the material limit (max 1500). Please suggest corrected parameters within limits.”
  * → 只针对错误的行调用 LLM，获得修正后的参数。

### ✔️ 技术上很简单：

* 检查 `df.loc[df["RPM Valid"] == False]` 是否存在。
* 针对每一行构造 Prompt → `chat_completion()` 获取修改建议。

### ✔️ 优势：

* 即使第一次生成出错，**系统可以自修正，而不是完全靠用户发现。**
* 提高可靠性，显著减少人工干预。

### ✔️ 非常推荐。

---

## 🚀 综合判断：

| 功能              | 技术复杂度   | 工程价值  | 推荐度  |
| --------------- | ------- | ----- | ---- |
| ✅ 向量检索 Few-shot | ⭐⭐⭐ 中-高 | 💎 极高 | ★★★★ |
| ✅ 自动纠错循环        | ⭐⭐ 低-中  | 🔧 很高 | ★★★★ |

→ **两个建议都强烈推荐纳入下一个 Sprint 开发。**

---

## 💡 小结一句：

> 这两个功能做出来，你的项目就不仅仅是“一个用 LLM 拼 Prompt 的玩具”，而是一个真正具备「自学习」「自修正」「自适应」能力的 AI 工艺规划工具。

真正能走进工程师的工作流。


“非切削工序（如Inspection）由 validate_plan() 自动识别为合法，无需修正。只有真正违反材料物理上限的工序（如rpm超速）会进入阶段B自动纠错。”


完成了这两个 Few-shot向量检索增强 和自动纠错循环（Self-repair），其实大概差不多了。