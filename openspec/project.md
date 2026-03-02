# Project Context

## Purpose

vibe-blog 是一个 AI 驱动的长文技术博客自动生成系统。通过多智能体协作架构（研究 → 规划 → 写作 → 代码集成 → 图片生成 → 质量审核 → 排版），将复杂技术知识转化为易读的技术文章，降低技术写作门槛。

核心功能：
- 多智能体协作（10+ agents：Researcher、Planner、Writer、Questioner、Coder、Artist、Reviewer 等）
- 深度研究（集成多种搜索引擎）
- 智能图片生成（Mermaid 图表 + AI 生成图片）
- 代码集成与可运行示例
- 质量审核与可读性分析
- 多格式导出（Markdown、图片）
- 书籍聚合（将多篇博客组合成教程书）
- 多平台发布（CSDN 等）
- 对话式写作（Chat-based writing sessions）
- 定时任务调度（Cron job scheduling）
- 小红书内容生成

## Tech Stack

### Backend
- **语言**: Python 3.10+
- **Web 框架**: Flask 3.0+
- **AI/ML**: LangChain 1.0+, LangGraph 1.0+, LangChain OpenAI/Gemini
- **模板引擎**: Jinja2（Prompt 模板）
- **数据校验**: Pydantic 2.0+
- **图片处理**: Pillow
- **文档处理**: python-docx
- **云存储**: oss2（阿里云 OSS）
- **中文 NLP**: jieba（可读性分析）
- **浏览器自动化**: Playwright（多平台发布）
- **LLM 追踪**: Langfuse 3.0+
- **任务队列**: aiosqlite, APScheduler, croniter
- **生产服务器**: Gunicorn

### Frontend
- **框架**: Vue 3.4+（Composition API）
- **构建工具**: Vite 5.0+
- **语言**: TypeScript 5.3+（strict 模式）
- **状态管理**: Pinia 2.1+
- **路由**: Vue Router 4.6+
- **UI 组件**: 自定义组件（基于 reka-ui）
- **样式**: Tailwind CSS 3.4+（自定义主题）
- **Markdown 渲染**: marked.js + marked-highlight + marked-katex-extension
- **代码高亮**: highlight.js
- **图表**: Mermaid.js 10.6+
- **数学公式**: KaTeX
- **富文本编辑器**: TipTap
- **导出**: html2canvas + jsPDF
- **HTTP 客户端**: Axios

### Database
- **SQLite**（多库架构）：
  - `banana_blog.db` — 博客/文档存储
  - `task_queue.db` — 异步任务队列
  - `vibe_reviewer.db` — 教程评审系统
  - `writing_sessions.db` — 对话式写作会话

### DevOps
- **容器化**: Docker + Docker Compose
- **反向代理**: Nginx（生产环境）
- **环境管理**: Python venv

## Project Conventions

### Code Style

**Python：**
- 使用类型注解（Type Hints）
- 类和函数编写 Docstring
- 使用 `logging` 模块记录日志
- try/except 进行错误处理
- 使用上下文管理器管理资源

**TypeScript / Vue：**
- TypeScript strict 模式
- Vue 3 Composition API（`<script setup>`）
- 可复用逻辑封装为 Composables
- Pinia 管理全局状态
- 组件命名：PascalCase（如 `BlogDetail.vue`）
- 文件命名：PascalCase（Vue 组件），kebab-case（工具类）

### Architecture Patterns

- **多智能体架构**：基于 LangGraph 的有向图工作流，10+ 专业化 Agent 协作完成博客生成
- **SSE 流式传输**：生成过程中实时推送进度更新
- **多 LLM 提供商支持**：通过 LLM Factory 支持 OpenAI 兼容 API，可配置多种模型
- **知识融合**：支持上传 PDF/MD/TXT 文档作为知识源
- **并行执行**：代码生成和图片生成支持并行处理
- **前后端分离**：Flask REST API + Vue SPA，通过 Vite 代理开发环境请求
- **Blueprint 模块化**：Flask 路由按功能拆分为独立 Blueprint
- **服务层模式**：业务逻辑封装在 `services/` 层，Routes 只做请求/响应处理

### Testing Strategy

**Backend：**
- 框架：pytest
- 测试目录：`backend/tests/`
- 测试类型：单元测试（`tests/unit/`）、集成测试（`tests/integration/`）、API 测试（`tests/api/`）、端到端测试
- 覆盖范围：100+ 测试文件，覆盖 agents、services、routes

**Frontend：**
- 框架：Vitest 4.0+
- 测试目录：`frontend/__tests__/`
- 测试类型：单元测试（`__tests__/unit/`）、集成测试（`__tests__/integration/`）
- 覆盖率：v8 provider，50% 阈值
- 测试环境：happy-dom
- E2E：Playwright

### Git Workflow

- 主分支：`main`
- 分支策略：feature 分支开发，合并到 main

## Domain Context

- **博客生成流程**：用户输入主题 → Researcher 搜索资料 → Planner 规划大纲 → Writer 撰写内容 → Questioner 提问优化 → Coder 生成代码示例 → Artist 生成配图 → Reviewer 质量审核 → Assembler 最终排版
- **知识融合**：支持上传文档作为写作参考素材，与搜索结果融合
- **风格配置**：支持自定义写作风格（style profiles）和图片生成风格
- **Token 追踪**：跟踪 LLM 调用成本，支持预算管理
- **上下文管理**：上下文压缩和 Guard 机制，防止超过模型上下文窗口
- **教程评审**：独立的教程质量评审模块（vibe_reviewer），评估文章质量和可读性

## Important Constraints

- LLM API 调用有速率限制和成本约束，需要 Token 追踪和预算管理
- 搜索 API（Zhipu、Serper、Sogou）有各自的配额限制
- 图片生成 API 有并发和速率限制
- SQLite 不支持高并发写入，任务队列使用 aiosqlite 进行异步操作
- 中文内容为主，需要 jieba 分词进行可读性分析
- Playwright 发布功能依赖浏览器环境，Docker 部署需要 headless 浏览器支持
- 环境变量配置项 200+，需通过 `.env` 文件管理

## External Dependencies

| 服务 | 用途 | 配置方式 |
|------|------|---------|
| OpenAI 兼容 API（默认阿里云 DashScope Qwen 系列） | LLM 推理 | `LLM_API_KEY`, `LLM_BASE_URL` |
| 智谱 Web Search API | 网络搜索 | `ZHIPU_API_KEY` |
| Serper Google Search | Google 搜索 | `SERPER_API_KEY` |
| 搜狗搜索（腾讯云） | 搜索引擎 | `SOGOU_API_KEY` |
| Nano Banana Pro API | AI 图片生成 | `IMAGE_API_KEY` |
| Veo3 (Google) | 视频生成 | 相关环境变量 |
| MinerU API | PDF 解析 | `MINERU_API_KEY` |
| 阿里云 OSS | 云端文件存储 | `OSS_ACCESS_KEY_ID`, `OSS_ACCESS_KEY_SECRET` |
| Langfuse | LLM 调用追踪 | `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY` |
