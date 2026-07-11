# V2.3 部署预检查

当前状态：V2.2 本地验收通过，Career Copilot Agent MVP Showcase 可在本地运行。

- 本地后端验收端口：`8001`
- 本地前端验收端口：`5500`
- 本次检查目标：只做部署前风险检查，不直接部署，不要新增复杂业务功能，不要改 Agent 工作流。

## 1. 前端 API 地址

检查结果：部分通过。

前端 Agent 联调面板提供了 API 地址输入框，用户可以在页面中把地址从 `http://127.0.0.1:8000` 改为 `http://127.0.0.1:8001`，本地联调已跑通。

部署风险：`index.html` 中仍有默认本地地址 `AGENT_API_BASE = 'http://127.0.0.1:8000'`，线上部署时需要避免写死 127.0.0.1。上线前建议改成可配置项，例如：

- 根据当前域名选择后端地址。
- 使用单独的 `config.js` 或构建时变量注入线上 API Base URL。
- 前端页面保留手动 API 地址输入框，便于调试。

## 2. README 本地启动方式

检查结果：通过。

README 已说明默认后端端口 `8000`，并补充 8000 遇到 WinError 10013 权限问题时可改用 `8001`：

```powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001
```

前端 Agent 联调面板中的 API 地址同步填写：

```text
http://127.0.0.1:8001
```

## 3. 后端线上启动命令

检查结果：待部署平台确认。

线上环境通常需要监听 `0.0.0.0`，并使用平台注入的端口：

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

如果部署平台使用 PowerShell 或 Windows 环境，端口变量写法可能需要调整为 `$env:PORT`。部署前应按目标平台文档确认。

## 4. 环境变量与密钥

检查结果：通过。

`.env.example` 已包含当前后端需要的占位字段：

- `OPENAI_API_KEY`
- `OPENAI_MODEL`
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`

真实 `.env` 不应提交；当前服务目录 `.gitignore` 已忽略 `.env`，根目录 `.gitignore` 也避免提交常见生成物。

当前检查结论：没有提交真实 .env。

## 5. CORS

检查结果：本地通过，线上需收紧。

当前 FastAPI CORS 使用 `allow_origins=["*"]`，适合本地 Demo 和作品集验收。线上部署后建议改为明确允许的前端域名，例如 GitHub Pages 域名或未来部署域名。

## 6. requirements.txt

检查结果：当前 MVP 通过。

`requirements.txt` 已包含：

- `fastapi`
- `uvicorn[standard]`
- `pydantic`
- `python-dotenv`
- `openai`

如果 V3.0 启用 Supabase 数据库存储，再补充 Supabase Python SDK 依赖。

## 7. 部署前结论

当前项目已具备 V2.3 部署预检查基础，但正式部署前建议先完成两件事：

1. 把前端默认 API Base URL 从本地地址改为可配置方案。
2. 将后端 CORS 从 `*` 收紧为线上前端域名。

本清单只做部署前检查，不直接部署，不新增复杂业务功能，不改 Agent 工作流。
