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






以下内容可直接存成 **`README.md`** 或者粘到报告笔记中。已按 *目录->文件->函数->逻辑* 层级完整梳理，并列出下一阶段开发计划，便于同学快速理解并继续迭代。
（所有路径均以 `ML_pro/` 为根）

---

## 📂 项目结构一览

| 路径                       | 说明                                              |
| ------------------------ | ----------------------------------------------- |
| `cnc_llm.ipynb`          | 主 Notebook：UI、业务流程、结果可视化                        |
| `llm_utils.py`           | 与 OpenAI API 交互、自动重试、token 统计                   |
| `requirements.txt`       | 项目依赖（`openai · tenacity · pandas · ipywidgets`） |
| `.env`                   | 私密环境变量，仅存 `OPENAI_API_KEY=...`                  |
| `LLMs_projet_note.ipynb` | 早期实验草稿（可忽略或存档）                                  |

---

## 1️⃣ `llm_utils.py` —— LLM 调用核心

```python
load_dotenv()                        # 读取 .env
client = openai.OpenAI(api_key=...)  # 初始化安全客户端
TOKENS_USED: int = 0                 # 全局 token 计数
```

### chat\_completion(prompt,…, verbose=True)

> **功能**：
>
> 1. 固定 system prompt，确保输出为 *JSON array*。
> 2. `tenacity` 自动重试，最大 3 次、指数退避 1–10 s。
> 3. 成功后累加 `response.usage.total_tokens` 到 `TOKENS_USED`。
> 4. `verbose` 开关：调试期打印原始 JSON，生产期静默。

---

## 2️⃣ `cnc_llm.ipynb` —— 主流程拆解

| 步骤           | 对应单元函数                                                                | 关键逻辑                                                                                  |
| ------------ | --------------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| **UI 定义**    | `desc_input / material_selector / generate_button / output_area`      | 纯 `ipywidgets`，最后一次性 `display(...)`                                                   |
| **按钮回调**     | `on_generate_clicked(b)`                                              | 整个业务管线                                                                                |
| ① 获取 outline | `get_outline(part, material)`<br>→ `chat_completion(verbose=False)`   | 生成高阶工序列表，如 “Rough Machining”                                                          |
| ② 获取 detail  | `get_detail(outline, …)`                                              | 传入 outline，请求带 rpm/feed 的 JSON                                                        |
| ③ 解析         | `parse_llm_output(raw_json)`                                          | `json.loads` → DataFrame 列重命名                                                         |
| ④ 两视图展示      | *同一单元内*<br>`df_full_valid`（完整流程）<br>`df_cut_valid`（过滤 rpm>0 & feed>0） | <br>• 用 `validate_plan` 添列 `RPM Valid / Feed Valid`<br>• `display_plan_table()` 高亮非法值 |
| ⑤ 反思摘要       | `reflect_summary(raw_json, df_full_valid)`                            | 步数、非法计数、Token、人工提示                                                                    |

> **validate\_plan(df, material)**
> 读取内置区间（铝/钢），用 `between()` 判断合法。

> **highlight\_invalid(val)**
> 返回红底 CSS。pandas≥2.2 使用 `df.style.map` 避免未来废弃警告。

---

## 3️⃣ 已实现的小细节

| 细节                        | 为什么要这样                      |
| ------------------------- | --------------------------- |
| `.env + load_dotenv()`    | 不泄漏 API Key，符合课程“安全 & 费用”要求 |
| `TOKENS_USED` 统计          | 便于写在报告里评估成本                 |
| 双视图：Full & Machining-only | 让阅卷老师既看全流程，又能专注切削参数         |
| `verbose` 开关              | Demo 时界面干净，调试时可追 JSON       |

---

## 4️⃣ 下一阶段路线图（对应原蓝图 Phase 2-3）

| 阶段                                | 目标                                                                               | 关键修改点                                                    |
| --------------------------------- | -------------------------------------------------------------------------------- | -------------------------------------------------------- |
| **Phase 2**<br>链式 Prompt & 多材料    | - 将 `get_outline` + `get_detail` 明确分成两轮 prompt（已具雏形）<br>- 在 UI 加刀具/材料下拉框扩展更多材料   | `get_detail` prompt 中注入材料区间，让 LLM 自动调 rpm/feed           |
| **Phase 3**<br>外部化材料-参数数据库        | - 把 `LIMITS` 写入 `materials.json`<br>- `validate_plan` 动态读取                       | 新建 `materials.json` 并调整 `validation.py`（待创建）             |
| **Phase 4**<br>功率/扭矩校验 + CSV 导出   | - `add_power_check(df)` 估算功率并验证<br>- `widgets.Button("💾 Export")` 输出 `plan.csv` | Notebook UI 再加一个导出按钮                                     |
| **Phase 5**<br>Few-shot vector 召回 | 选 5 条人工优质工艺 → `sentence_transformers` 建索引，近邻拼进 prompt                            | 另建 `examples/` 目录，写 `retriever.py`                       |
| **Phase 6**<br>自动纠错循环             | 若 `RPM Valid`=False → 自动回写提示并二次调用 LLM 修正                                         | 在 `on_generate_clicked` 里做 while-loop with max 2 retries |

> 可以按时间/精力只实现 2 – 3 – 4 就能拿高分；5 – 6 作为加分项。

---

## 5️⃣ 对同学的使用指引

1. **安装依赖**

   ```bash
   pip install -r requirements.txt
   ```
2. **配置 Key**
   在项目根建 `.env` ✍️

   ```env
   OPENAI_API_KEY=sk-xxxx
   ```
3. **运行 Notebook**
   `cnc_llm.ipynb` → *Run All*
4. **输入零件描述 & 选材料** → 点击 **Generate CNC Plan**
5. **查看两张表**

   * *Full Process Plan*：含选料/检验
   * *Machining-only Plan*：仅切削步骤
6. **阅读 Reflection Summary** → 了解非法参数与 token 成本
7. **下一步**：按 README 的“阶段路线图”实现 Phase 2 …

---


