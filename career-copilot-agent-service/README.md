# Career Copilot Agent Service

AI 求职投递助手的 Agent MVP 后端服务。当前阶段不重构前端 Demo，只提供可被前端调用的 FastAPI 接口、结构化 JSON 输出和可验收的 Swagger 示例。

## 当前范围

- 保留 `.env` 管理密钥，不在代码或前端写入 OpenAI API Key。
- 使用 Pydantic 定义输入输出 schema，接口返回结构化 JSON。
- `/api/agent/run` 按固定工作流执行：JD解析 -> 简历匹配 -> 投递优先级判断 -> 材料生成 -> 质量审核。
- `quality_review` 检查虚构/待补充信息、夸大表述、遗漏 JD 关键词、过度营销语气。

## 启动方式

```powershell
cd "C:\Users\86173\Documents\AI求职投递助手\career-copilot-agent-service"
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

如果你使用 Codex bundled Python，也可以这样启动：

```powershell
cd "C:\Users\86173\Documents\AI求职投递助手\career-copilot-agent-service"
$env:PYTHONPATH='.'
C:\Users\86173\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

打开 Swagger：

```text
http://127.0.0.1:8000/docs
```

健康检查：

```text
GET http://127.0.0.1:8000/health
```

## 环境变量

复制 `.env.example` 为 `.env`，填入真实密钥。不要把真实 API Key 写进前端、README 或代码。

```bash
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4.1-mini
SUPABASE_URL=
SUPABASE_ANON_KEY=
```

当前 MVP 的 skill 先使用本地规则兜底，保证没有 API Key 时也能演示完整工作流。下一阶段可在各 skill 内接入 OpenAI Structured Outputs，把同一套 response schema 用于真实模型输出。

## 接口说明

### 1. `POST /api/jd/parse`

用途：把原始 JD 解析成岗位结构化信息。

请求体：

```json
{
  "jd_text": "公司：星河科技\n岗位：AI产品实习生\n职责：参与用户调研、竞品分析、Prompt设计和数据看板搭建。\n要求：熟悉Python、SQL、Excel，每周到岗4天。"
}
```

返回字段：

```text
job_title, company, job_type, core_tasks, hard_requirements,
soft_requirements, bonus_points, ats_keywords, risk_points
```

### 2. `POST /api/resume/match`

用途：根据 JD 结构、简历文本和求职画像输出匹配分、证据、缺口和投递建议。

返回字段：

```text
overall_score, dimension_scores, matched_evidence, missing_evidence,
resume_improvement_suggestions, application_recommendation
```

### 3. `POST /api/material/generate`

用途：基于已提供的真实经历生成投递材料草稿。

返回字段：

```text
email_subject, email_body, boss_message, referral_message,
follow_up_message, attachment_name
```

### 4. `POST /api/agent/run`

用途：一键执行完整 Agent 工作流。

执行顺序：

```text
JD解析 -> 简历匹配 -> 投递优先级判断 -> 材料生成 -> 质量审核
```

返回字段：

```text
jd_analysis, resume_match, priority_decision, generated_materials,
quality_review, recommended_next_action, trace
```

`quality_review` 结构：

```text
has_fabrication_risk, fabrication_items,
has_exaggeration_risk, exaggeration_items,
missing_keywords, tone_issues,
revision_suggestions, final_safety_level
```

## Swagger 测试样例

四个 realistic sample payload 已放在：

```text
sample_payloads/jd_parse.json
sample_payloads/resume_match.json
sample_payloads/material_generate.json
sample_payloads/agent_run.json
```

在 Swagger 中测试：

1. 打开 `http://127.0.0.1:8000/docs`。
2. 展开目标接口。
3. 点击 `Try it out`。
4. 复制对应 `sample_payloads/*.json` 内容到 Request body。
5. 点击 `Execute`。
6. 检查返回是否为 JSON object，而不是自然语言长文。

建议优先测试 `/api/agent/run`，它会一次性返回完整工作流结果和 `trace`。

## 自动化测试

```powershell
cd "C:\Users\86173\Documents\AI求职投递助手\career-copilot-agent-service"
$env:PYTHONPATH='.'
C:\Users\86173\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m unittest discover -s tests -v
```

当前测试覆盖：

- 四个核心接口的 HTTP 调用。
- OpenAPI/Swagger 是否暴露 JSON request/response contract。
- 输入 schema 是否带 realistic examples。
- `/api/agent/run` 的执行顺序。
- `quality_review` 是否检查虚构风险、夸大风险、遗漏关键词和过度营销语气。
- 非 AI 岗位不会因为 AI Demo 证据被过度加分。
- P1 修改后投递场景会返回更具体的 `recommended_next_action`。

## 前端接入方式

当前根目录 `index.html` 已新增「Agent 联调」面板，并优先调用完整工作流接口：

```js
const AGENT_API_BASE = 'http://127.0.0.1:8000';
```

核心按钮「一键运行 Career Copilot Agent」请求：

```js
fetch(`${AGENT_API_BASE}/api/agent/run`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    jd_text: jdText,
    resume_text: resumeText,
    user_profile: profileFormValue,
    task: '判断是否值得投递，并生成投递材料'
  })
});
```

前端渲染：

- `jd_analysis` 渲染成 JD 解析卡片。
- `resume_match` 渲染成匹配分、证据和缺口列表。
- `priority_decision` 渲染成 P0/P1/P2/P3 决策标签。
- `generated_materials` 渲染成可复制的邮件/BOSS/内推话术。
- `quality_review` 渲染成发送前检查清单。
- `recommended_next_action` 渲染成下一步行动建议。
- `trace` 渲染成 Agent 执行链路，方便作品集展示。

本地联调前端：

```powershell
cd "C:\Users\86173\Documents\AI求职投递助手"
python -m http.server 5500 --bind 127.0.0.1
```

浏览器打开：

```text
http://127.0.0.1:5500/index.html
```

进入「Agent 联调」标签，点击「填充样例」和「一键运行 Career Copilot Agent」。结果生成后，可在前端点击「保存本次分析」写入 LocalStorage，或点击「导出分析报告」下载 Markdown 报告。

## 输出评估

项目根目录新增 `docs/agent_evaluation.md`，记录 AI产品实习生、产品运营 / 商业化运营实习生、数据运营 / 数据产品实习生 3 组真实岗位样例的 `/api/agent/run` 输出摘要和质量评估。

## 下一步

- 将当前本地规则 skill 替换为 OpenAI Structured Outputs。
- 前端 API Base 后续可从本地 `http://127.0.0.1:8000` 切换为云端后端地址。
- 用户确认后再接入 Supabase 保存投递看板，不自动外发、不自动投递。


