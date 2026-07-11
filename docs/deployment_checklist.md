# V2.3 部署预检查

当前状态：V2.2 本地验收通过，V2.3 已完成线上部署适配准备。Career Copilot Agent MVP Showcase 可在本地运行，下一步可以部署 FastAPI 后端并把前端 API 地址切换到公网后端。

- 本地后端验收端口：`8001`
- 本地前端验收端口：`5500`
- 本次检查目标：只做部署前风险检查，不直接部署，不要新增复杂业务功能，不要改 Agent 工作流。

## 1. 前端 API 地址

检查结果：通过。

前端保留 Agent 联调面板的 API 地址输入框，并新增统一配置入口：

```javascript
window.CAREER_COPILOT_CONFIG = window.CAREER_COPILOT_CONFIG || {
  API_BASE_URL: 'http://127.0.0.1:8001'
};
```

本地默认地址为 `http://127.0.0.1:8001`。线上部署后，可将 `API_BASE_URL` 或页面输入框替换为云端地址，例如 `https://xxx.onrender.com`。

部署要求：避免写死 127.0.0.1，线上展示必须使用公网后端域名。

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

检查结果：通过，待部署平台实际验证。

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
- `CORS_ALLOW_ORIGINS`

真实 `.env` 不应提交；当前服务目录 `.gitignore` 已忽略 `.env`，根目录 `.gitignore` 也避免提交常见生成物。

当前检查结论：没有提交真实 .env。

## 5. CORS

检查结果：通过，待线上域名补充。

FastAPI 当前使用明确白名单：

- `http://127.0.0.1:5500`
- `http://localhost:5500`
- `https://lixuehu123.github.io`

未来线上前端域名可通过 `CORS_ALLOW_ORIGINS` 环境变量补充，多个域名用英文逗号分隔。

## 6. /health 健康检查

检查结果：通过。

`GET /health` 返回结构化 JSON：

```json
{
  "status": "ok",
  "service": "career-copilot-agent-service"
}
```

该接口适合 Render、Railway 等部署平台做健康检查。

## 7. requirements.txt

检查结果：当前 MVP 通过。

`requirements.txt` 已包含：

- `fastapi`
- `uvicorn[standard]`
- `pydantic`
- `python-dotenv`
- `openai`

如果 V3.0 启用 Supabase 数据库存储，再补充 Supabase Python SDK 依赖。

## 8. 部署前结论

当前项目已完成 V2.3 部署适配准备：

1. 前端 API Base URL 已具备配置入口。
2. 后端 CORS 已从通配配置改为本地、GitHub Pages 和环境变量扩展白名单。
3. `/health` 可用于部署平台健康检查。
4. `.env.example` 覆盖必要变量，真实 `.env` 不提交。
5. `docs/deployment_guide.md` 已补充本地运行、后端部署、前端 API 配置、线上验收和常见问题。

本清单只做部署前检查，不直接部署，不新增复杂业务功能，不改 Agent 工作流。
