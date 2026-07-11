# V2.3 线上部署适配指南

当前目标：在不改动 Agent 核心工作流、不新增复杂业务功能的前提下，把本地可运行的 Career Copilot Agent MVP 适配为可部署版本。

## 本地运行

后端默认建议使用 8001 端口，避免部分 Windows 环境中 8000 端口出现 WinError 10013 权限问题。

```powershell
cd "C:\Users\86173\Documents\AI求职投递助手\career-copilot-agent-service"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001
```

前端本地静态服务：

```powershell
cd "C:\Users\86173\Documents\AI求职投递助手"
python -m http.server 5500 --bind 127.0.0.1
```

本地访问地址：

```text
后端 Swagger：http://127.0.0.1:8001/docs
后端健康检查：http://127.0.0.1:8001/health
前端页面：http://127.0.0.1:5500/index.html
前端 Agent API 地址：http://127.0.0.1:8001
```

如需使用 8000，也可以启动：

```powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

但前端 Agent 联调面板中的 API 地址必须与后端实际端口一致。

## 后端部署

线上部署时，FastAPI 需要监听平台分配的公网端口。通用启动命令：

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

如果目标平台使用 Windows PowerShell 语法，端口变量可能需要写成：

```powershell
python -m uvicorn app.main:app --host 0.0.0.0 --port $env:PORT
```

推荐环境变量：

```text
OPENAI_API_KEY=你的真实 Key，仅配置在部署平台环境变量中
OPENAI_MODEL=gpt-4.1-mini
CORS_ALLOW_ORIGINS=https://lixuehu123.github.io,https://你的前端域名
```

部署完成后，后端会得到一个公网地址，例如：

```text
https://xxx.onrender.com
```

验收后端时优先打开：

```text
https://xxx.onrender.com/health
https://xxx.onrender.com/docs
```

`/health` 当前返回结构化 JSON，适合部署平台健康检查：

```json
{
  "status": "ok",
  "service": "career-copilot-agent-service"
}
```

## 前端配置 API 地址

前端默认使用本地后端：

```javascript
window.CAREER_COPILOT_CONFIG = window.CAREER_COPILOT_CONFIG || {
  API_BASE_URL: 'http://127.0.0.1:8001'
};
```

本地开发时保持：

```text
http://127.0.0.1:8001
```

后端上线后，将 `API_BASE_URL` 或页面「API 地址」输入框替换为线上后端地址：

```text
https://xxx.onrender.com
```

注意不要把 `OPENAI_API_KEY` 写入前端 HTML、JS 或浏览器 LocalStorage。OpenAI Key 只应该存在于后端 `.env` 或部署平台环境变量中。

## 线上验收步骤

1. 打开线上后端 `/health`，确认返回 `status: ok`。
2. 打开线上后端 `/docs`，确认 Swagger 可访问。
3. 打开 GitHub Pages 或线上前端页面。
4. 进入「工作台 - Agent 联调」。
5. 将 API 地址填写为线上后端地址，例如 `https://xxx.onrender.com`。
6. 点击「填充联调样例」。
7. 点击「一键运行 Career Copilot Agent」。
8. 检查页面是否渲染 JD 解析、简历匹配、投递优先级、投递材料、质量审核和下一步建议。
9. 点击「保存本次分析」，刷新页面后确认历史结果仍可复盘。
10. 点击「导出分析报告」，确认 Markdown 内容完整。

## 常见问题

### 8000 端口无法启动

如果 Windows 报 WinError 10013，改用 8001：

```powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001
```

前端 API 地址同步填写：

```text
http://127.0.0.1:8001
```

### 线上前端提示 CORS

检查后端环境变量 `CORS_ALLOW_ORIGINS` 是否包含当前前端域名。多个域名用英文逗号分隔：

```text
CORS_ALLOW_ORIGINS=https://lixuehu123.github.io,https://xxx.vercel.app
```

### 线上 Agent 返回 500

优先检查部署平台环境变量是否配置了 `OPENAI_API_KEY`，并查看平台日志。不要把真实 `.env` 提交到 Git。

### 前端请求仍然打到本地

检查 `API_BASE_URL` 是否仍为 `http://127.0.0.1:8001`。线上展示时应替换为部署后的后端公网地址，例如 `https://xxx.onrender.com`。

### requirements.txt 不完整

当前 MVP 后端依赖应包含 FastAPI、Uvicorn、Pydantic、python-dotenv 和 OpenAI SDK。若后续 V3.0 接入 Supabase，再补充对应 SDK。
