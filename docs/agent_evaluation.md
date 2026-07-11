# Agent 输出质量评估

当前阶段：V2.1 Agent 输出评估与报告导出版。

评估目标：验证 Career Copilot Agent 在真实求职场景中是否能稳定完成 JD 解析、简历匹配、投递优先级判断、材料生成、质量审核和下一步建议。测试通过 FastAPI 路由 `POST /api/agent/run` 执行，保持现有 API schema 不变。

## 评估维度

- JD解析是否准确
- 简历匹配评分是否合理
- matched_evidence 是否真实
- missing_evidence 是否具体
- 投递材料是否可用
- quality_review 是否发现风险
- recommended_next_action 是否具体

## 总览

| 测试岗位 | overall_score | priority_level | application_recommendation | quality_review | 是否通过 |
| --- | ---: | --- | --- | --- | --- |
| AI产品实习生 | 88 | P0 | strong_apply | needs_review | 通过 |
| 产品运营 / 商业化运营实习生 | 84 | P1 | apply_after_revision | safe | 基本通过 |
| 数据运营 / 数据产品实习生 | 84 | P1 | apply_after_revision | safe | 基本通过 |

## 本轮优化记录

- 发现问题：产品运营 / 商业化运营实习生样例中，旧逻辑只凭 SQL、Excel 和 AI Demo 证据给出过高评分。
- 优化动作：保持 `ResumeMatch` schema 不变，收紧 `match_resume` 评分逻辑；非 AI 岗不再因为 AI Demo 自动加分，并新增运营、数据、AI 三类岗位场景证据检查。
- 验收结果：商业化运营样例从虚高优先级收敛为需要补强证据后再投递，`missing_evidence` 能指出商业化、用户分层、漏斗、商家/增长等缺口。

## AI产品实习生

### realistic sample payload

```json
{
  "jd_text": "公司：灵犀智能\n岗位：AI产品实习生\n岗位类型：实习\n职责：参与大模型应用的用户调研、竞品分析、Prompt方案设计、PRD撰写、数据看板搭建和效果复盘；协助产品经理跟进模型能力评测、用户反馈整理和版本迭代。\n要求：熟悉AI产品或大模型应用，具备结构化表达和需求分析能力；熟悉Python、SQL、Excel或数据分析工具；每周到岗4天，实习3个月以上。\n加分：有AI产品作品集、Agent Demo、Prompt迭代经验或完整产品文档。\n风险提示：岗位节奏快，需要主动沟通和跨团队协作。",
  "resume_text": "我是信息管理与信息系统专业应届生，目标方向是AI产品、产品运营和数据产品实习。做过AI求职投递助手Demo，包含JD解析、简历匹配、材料生成、质量审核和投递看板；使用Python整理岗位文本和测试样例，用SQL做基础查询分析，用Excel制作指标表和对比表；曾完成用户访谈、竞品分析、Prompt迭代和PRD草稿整理。课程项目中做过校园二手交易小程序需求分析，负责用户调研、功能优先级梳理和原型说明；也参与过社团活动数据复盘，用Excel统计报名、到场和转化情况。每周可到岗4天，可实习3个月以上。作品集：https://lixuehu123.github.io/AI-/index.html",
  "user_profile": {
    "identity": "应届生",
    "target_roles": [
      "AI产品",
      "产品经理"
    ],
    "target_cities": [
      "上海",
      "杭州"
    ],
    "availability": "每周4天，可实习3个月以上",
    "skills_summary": "Python, SQL, Excel, Prompt, 用户调研, 竞品分析, PRD",
    "portfolio_url": "https://lixuehu123.github.io/AI-/index.html"
  },
  "task": "判断是否值得投递，并生成投递材料"
}
```

### 输出摘要

```json
{
  "company": "灵犀智能",
  "job_title": "AI产品实习生",
  "overall_score": 88,
  "application_recommendation": "strong_apply",
  "priority_level": "P0",
  "quality_review": {
    "has_fabrication_risk": false,
    "fabrication_items": [],
    "has_exaggeration_risk": false,
    "exaggeration_items": [],
    "missing_keywords": [
      "用户调研",
      "竞品分析",
      "数据看板",
      "需求分析",
      "PRD",
      "大模型"
    ],
    "tone_issues": [],
    "revision_suggestions": [
      "发送前检查是否需要补充 JD 关键词的真实证据"
    ],
    "final_safety_level": "needs_review"
  },
  "recommended_next_action": "请人工确认材料内容，确认后可投递并写入投递看板",
  "matched_evidence": [
    "简历中出现 JD 关键词：AI产品",
    "简历中出现 JD 关键词：Prompt",
    "简历中出现 JD 关键词：Python",
    "简历中出现 JD 关键词：SQL",
    "简历中出现 JD 关键词：Excel"
  ],
  "missing_evidence": [
    "缺少 JD 关键词或证据：数据看板",
    "缺少 JD 关键词或证据：大模型",
    "缺少岗位场景证据：数据分析"
  ]
}
```

### 质量评估

- JD解析是否准确：通过：公司、岗位、实习类型、AI/Prompt/PRD/数据看板等关键词可识别。
- 简历匹配评分是否合理：通过：AI项目、Prompt、Python、SQL、用户调研等证据充分，P0/strong_apply合理。
- matched_evidence 是否真实：通过：证据均来自简历中的AI求职助手、Prompt、Python、SQL和用户调研。
- missing_evidence 是否具体：通过：指出数据看板、大模型等仍需补充更具体项目证据。
- 投递材料是否可用：基本通过：可作为初稿，但发送前应补充更具体的项目产出。
- quality_review 是否发现风险：通过：发现部分JD关键词未覆盖到材料中，要求人工复核。
- recommended_next_action 是否具体：通过：P0 结果会提示人工确认材料后投递并写入看板。

## 产品运营 / 商业化运营实习生

### realistic sample payload

```json
{
  "jd_text": "公司：光合增长\n岗位：商业化产品运营实习生\n岗位类型：实习\n职责：支持商业化活动配置、商家运营、用户分层和转化漏斗分析；跟踪活动曝光、点击、报名、转化等指标，输出周报；协助整理竞品活动玩法和运营策略，推进跨部门需求沟通。\n要求：熟悉Excel，具备基础SQL或数据分析能力；对商业化、增长、用户运营感兴趣；沟通执行力强，能细致处理配置和复盘工作。\n加分：有电商、活动运营、校园增长或数据复盘项目经验。\n风险提示：需要处理重复运营配置，对细节和响应速度要求高。",
  "resume_text": "我是信息管理与信息系统专业应届生，目标方向是AI产品、产品运营和数据产品实习。做过AI求职投递助手Demo，包含JD解析、简历匹配、材料生成、质量审核和投递看板；使用Python整理岗位文本和测试样例，用SQL做基础查询分析，用Excel制作指标表和对比表；曾完成用户访谈、竞品分析、Prompt迭代和PRD草稿整理。课程项目中做过校园二手交易小程序需求分析，负责用户调研、功能优先级梳理和原型说明；也参与过社团活动数据复盘，用Excel统计报名、到场和转化情况。每周可到岗4天，可实习3个月以上。作品集：https://lixuehu123.github.io/AI-/index.html",
  "user_profile": {
    "identity": "应届生",
    "target_roles": [
      "产品运营",
      "商业化运营"
    ],
    "target_cities": [
      "上海",
      "杭州"
    ],
    "availability": "每周4天，可实习3个月以上",
    "skills_summary": "Excel, SQL, 用户调研, 竞品分析, 活动复盘, 文档整理",
    "portfolio_url": "https://lixuehu123.github.io/AI-/index.html"
  },
  "task": "判断是否值得投递，并生成投递材料"
}
```

### 输出摘要

```json
{
  "company": "光合增长",
  "job_title": "商业化产品运营实习生",
  "overall_score": 84,
  "application_recommendation": "apply_after_revision",
  "priority_level": "P1",
  "quality_review": {
    "has_fabrication_risk": false,
    "fabrication_items": [],
    "has_exaggeration_risk": false,
    "exaggeration_items": [],
    "missing_keywords": [],
    "tone_issues": [],
    "revision_suggestions": [],
    "final_safety_level": "safe"
  },
  "recommended_next_action": "补强简历关键词后投递",
  "matched_evidence": [
    "简历中出现 JD 关键词：SQL",
    "简历中出现 JD 关键词：Excel",
    "简历中出现岗位场景证据：转化",
    "简历中出现岗位场景证据：复盘",
    "简历中包含项目/作品集证据，可用于支撑产品能力"
  ],
  "missing_evidence": [
    "缺少岗位场景证据：商业化",
    "缺少岗位场景证据：用户分层",
    "缺少岗位场景证据：漏斗",
    "缺少岗位场景证据：增长",
    "缺少岗位场景证据：电商",
    "缺少岗位场景证据：数据分析"
  ]
}
```

### 质量评估

- JD解析是否准确：基本通过：能识别商业化运营、Excel/SQL和运营配置风险，但运营场景关键词仍依赖规则抽取。
- 简历匹配评分是否合理：通过：已从原先虚高P0收紧为修改后投递，更符合简历只有活动复盘/Excel/SQL但缺商业化深证据的情况。
- matched_evidence 是否真实：通过：引用SQL、Excel、活动/复盘等真实经历。
- missing_evidence 是否具体：通过：指出商业化、用户分层、漏斗、商家/增长等岗位场景证据缺口。
- 投递材料是否可用：基本通过：能生成初稿，但建议先补充运营配置或增长复盘案例。
- quality_review 是否发现风险：基本通过：未发现虚构和夸大；岗位场景缺口主要由 missing_evidence 暴露，后续可让 quality_review 联动匹配缺口。
- recommended_next_action 是否具体：通过：P1 结果会提示先补强简历关键词后再投递。

## 数据运营 / 数据产品实习生

### realistic sample payload

```json
{
  "jd_text": "公司：数湾科技\n岗位：数据产品实习生\n岗位类型：实习\n职责：协助梳理业务指标口径、撰写数据产品需求文档，跟进BI看板搭建和数据异常排查；使用SQL提取数据，结合Excel或可视化工具完成经营分析，并沉淀指标字典。\n要求：熟悉SQL、Excel和基础Python，理解指标体系、数据看板和需求分析；逻辑清晰，能和业务、研发沟通数据需求。\n加分：有BI看板、数据分析、指标体系、数据产品或运营分析项目经验。\n风险提示：需要较强数据细节意识，不能只停留在概念层。",
  "resume_text": "我是信息管理与信息系统专业应届生，目标方向是AI产品、产品运营和数据产品实习。做过AI求职投递助手Demo，包含JD解析、简历匹配、材料生成、质量审核和投递看板；使用Python整理岗位文本和测试样例，用SQL做基础查询分析，用Excel制作指标表和对比表；曾完成用户访谈、竞品分析、Prompt迭代和PRD草稿整理。课程项目中做过校园二手交易小程序需求分析，负责用户调研、功能优先级梳理和原型说明；也参与过社团活动数据复盘，用Excel统计报名、到场和转化情况。每周可到岗4天，可实习3个月以上。作品集：https://lixuehu123.github.io/AI-/index.html",
  "user_profile": {
    "identity": "应届生",
    "target_roles": [
      "数据产品",
      "数据运营"
    ],
    "target_cities": [
      "上海",
      "杭州"
    ],
    "availability": "每周4天，可实习3个月以上",
    "skills_summary": "SQL, Python, Excel, 指标表, 数据分析, 需求文档",
    "portfolio_url": "https://lixuehu123.github.io/AI-/index.html"
  },
  "task": "判断是否值得投递，并生成投递材料"
}
```

### 输出摘要

```json
{
  "company": "数湾科技",
  "job_title": "数据产品实习生",
  "overall_score": 84,
  "application_recommendation": "apply_after_revision",
  "priority_level": "P1",
  "quality_review": {
    "has_fabrication_risk": false,
    "fabrication_items": [],
    "has_exaggeration_risk": false,
    "exaggeration_items": [],
    "missing_keywords": [
      "需求分析"
    ],
    "tone_issues": [],
    "revision_suggestions": [
      "发送前检查是否需要补充 JD 关键词的真实证据"
    ],
    "final_safety_level": "safe"
  },
  "recommended_next_action": "补强简历关键词后投递",
  "matched_evidence": [
    "简历中出现 JD 关键词：数据产品",
    "简历中出现 JD 关键词：Python",
    "简历中出现 JD 关键词：SQL",
    "简历中出现 JD 关键词：Excel",
    "简历中出现 JD 关键词：需求分析"
  ],
  "missing_evidence": [
    "缺少 JD 关键词或证据：数据看板",
    "缺少岗位场景证据：BI",
    "缺少岗位场景证据：数据分析",
    "缺少岗位场景证据：可视化",
    "缺少岗位场景证据：异常"
  ]
}
```

### 质量评估

- JD解析是否准确：通过：岗位、SQL/Python/Excel、数据产品、看板和指标类要求可识别。
- 简历匹配评分是否合理：基本通过：工具证据充分，但BI、异常排查、指标字典证据不足，因此不应只看总分。
- matched_evidence 是否真实：通过：引用SQL、Python、Excel、指标表和项目/作品集。
- missing_evidence 是否具体：通过：指出BI/看板/指标/异常等数据产品深度证据缺口。
- 投递材料是否可用：基本通过：可作为初稿，建议补充一条指标口径或看板案例。
- quality_review 是否发现风险：基本通过：未发现虚构和夸大；数据深度缺口主要由 missing_evidence 暴露，后续可让 quality_review 联动匹配缺口。
- recommended_next_action 是否具体：通过：P1 结果会提示先补强简历关键词后再投递。

## 后续观察点

- 对真实公司 JD，可继续扩充 `ats_keywords` 和岗位场景词表，降低漏抽取。
- 投递材料仍应由用户发送前人工确认，避免把“可补充”或泛化证据直接外发。
- 下一轮可加入人工评分表，记录每次输出是否被用户采纳。


