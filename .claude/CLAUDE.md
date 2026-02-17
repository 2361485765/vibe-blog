# CLAUDE.md

## 项目概述

VibeBlog 是一个 AI 长文博客生成 Agent，基于 Flask（后端）+ Vue 3（前端）+ LangGraph（多智能体编排）。

## 本地开发

### 一键启动

```bash
bash docker/start-local.sh
```

该脚本会：
1. 自动检测并释放 5001（后端）和 5173（前端）端口
2. 检查 `backend/.env` 配置
3. 检查并安装前端依赖
4. 启动后端（Flask，端口 5001）和前端（Vite，端口 5173）
5. 日志输出到 `logs/` 目录
6. Ctrl+C 停止所有服务

可选启用 WhatsApp 网关：
```bash
ENABLE_WHATSAPP=true bash docker/start-local.sh
```

### 服务地址

- 前端：http://localhost:5173
- 后端：http://localhost:5001

## 测试

### 单元测试（前端）

```bash
cd frontend
npm test                # Vitest 运行所有测试
npm run test:coverage   # 生成覆盖率报告
```

### 单元测试（后端）

```bash
cd backend
python -m pytest tests/ -v
```

### E2E 测试

E2E 测试使用 Playwright + pytest，需要前后端服务运行中。

**启动服务 + 运行 E2E 测试的完整流程：**

```bash
# 1. 先启动服务（在一个终端中）
bash docker/start-local.sh

# 2. 在另一个终端运行 E2E 测试
RUN_E2E_TESTS=1 python -m pytest tests/e2e/ -v

# 带浏览器界面运行（调试用）
RUN_E2E_TESTS=1 E2E_HEADED=1 python -m pytest tests/e2e/ -v

# 运行单个测试文件
RUN_E2E_TESTS=1 python -m pytest tests/e2e/test_tc14_quality_eval.py -v
```

**环境变量：**
- `RUN_E2E_TESTS=1`：必须设置，否则所有 E2E 测试会被跳过
- `E2E_HEADED=1`：显示浏览器窗口（默认 headless）
- `E2E_SLOW_MO=100`：操作间隔毫秒数（默认 100）

**E2E 测试文件列表：**
- `test_tc01_home_load.py` — 首页加载
- `test_tc02_blog_gen.py` — 博客生成流程
- `test_tc03_advanced.py` — 高级功能
- `test_tc04_file_upload.py` — 文件上传
- `test_tc05_progress.py` — 进度追踪（SSE）
- `test_tc06_cancel.py` — 取消任务
- `test_tc07_navigation.py` — 导航
- `test_tc08_theme.py` — 主题切换
- `test_tc09_history.py` — 历史记录
- `test_tc10_blog_detail.py` — 博客详情页
- `test_tc11_responsive.py` — 响应式布局
- `test_tc12_error.py` — 错误处理
- `test_tc13_dashboard.py` — 仪表盘
- `test_tc14_quality_eval.py` — 质量评估对话框

**截图输出：** `backend/outputs/e2e_screenshots/`

## 可用 Skills（Claude Code 斜杠命令）

以下 skills 与本项目开发相关，在 Claude Code 中通过 `/skill-name` 调用：

### 开发流程
- `/vue-best-practices` — Vue.js 开发规范，强制 Composition API + `<script setup>` + TypeScript
- `/brainstorming` — 创意/功能设计前的头脑风暴，在写代码前探索需求和方案
- `/spec-driven-development` — 需求→设计→任务三阶段规范化开发流程
- `/kiro-skill` — 交互式功能开发，从 idea 到 EARS 格式需求文档到实现

### 计划与执行
- `/writing-plans` — 有 spec 后，编写多步骤实施计划
- `/executing-plans` — 在独立会话中执行实施计划，带 review checkpoint
- `/subagent-driven-development` — 并行执行实施计划中的独立任务
- `/dispatching-parallel-agents` — 2+ 个独立任务并行处理

### 测试与质量
- `/test-driven-development` — TDD，先写测试再写实现
- `/systematic-debugging` — 遇到 bug/测试失败时的系统化调试流程
- `/webapp-testing` — Playwright 交互测试本地 Web 应用，截图、日志、UI 验证
- `/e2e-testing-patterns` — E2E 测试最佳实践（Playwright/Cypress）
- `/verification-before-completion` — 完成前必须跑验证命令，证据先于断言

### 代码审查与发布
- `/requesting-code-review` — 完成功能后请求代码审查
- `/receiving-code-review` — 收到 review 反馈后的处理流程
- `/finishing-a-development-branch` — 实现完成后决定 merge/PR/cleanup
- `/using-git-worktrees` — 创建隔离的 git worktree 做功能开发

### 内容与发布（VibeBlog 特有）
- `/content-research-writer` — 辅助写高质量内容，研究、引用、大纲迭代
- `/baoyu-post-to-wechat` — 发布文章到微信公众号
- `/baoyu-post-to-x` — 发布内容到 X（Twitter）
- `/baoyu-xhs-images` — 生成小红书风格信息图
- `/baoyu-slide-deck` — 从内容生成演示文稿图片
- `/baoyu-cover-image` — 生成文章封面图
- `/baoyu-article-illustrator` — 智能文章配图
- `/baoyu-image-gen` — AI 图片生成（OpenAI/Google API）
- `/baoyu-comic` — 知识漫画创作

### 工具类
- `/topic-collector` — AI 热点采集（Twitter、Product Hunt、Reddit、HN）
- `/scheduler` — 定时任务调度（macOS launchd）
- `/find-skills` — 搜索和发现更多可安装的 skills
- `/python-patterns` — Python 最佳实践和惯用写法
- `/ui-ux-pro-max` — UI/UX 设计智能，50 种风格、调色板、字体搭配

## 前端设计规范

前端 UI 遵循 **终端/开发者美学 (Terminal-Inspired Developer Aesthetic)** 风格，详见 `.claude/STYLE-GUIDE.md`。

核心规则：
1. **卡片组件** 统一使用终端窗口样式：红黄绿圆点 + 文件名标题栏 + `border-radius: 12px`
2. **导航/标题** 使用命令行语法：`$ command --flag`、`$ pwd: ~ / page`
3. **内容装饰** 使用代码语法元素：`export`、`import`、`//`、`$`
4. **字体** UI 镶边用 `var(--font-mono)` (JetBrains Mono)，正文用 `var(--font-sans)`
5. **色彩** 使用 `tokens.css` 中的语法高亮色：关键字紫、函数蓝、字符串绿、变量粉
6. **玻璃态** 浮动面板使用 `backdrop-filter: blur(12px)` + `var(--glass-bg)`
7. **暗色模式** 所有组件必须支持 `.dark-mode` 主题切换

## 项目结构

```
vibe-blog/
├── backend/           # Flask 后端
│   ├── app.py         # 入口
│   ├── routes/        # API 路由
│   ├── services/      # 业务逻辑（blog_generator、database 等）
│   └── tests/         # 后端测试
├── frontend/          # Vue 3 + Vite 前端
│   ├── src/
│   │   ├── components/  # UI 组件
│   │   ├── views/       # 页面
│   │   ├── services/    # API 调用
│   │   └── composables/ # Vue composables
│   └── __tests__/       # 前端测试
├── tests/e2e/         # Playwright E2E 测试
├── docker/            # Docker 配置 + 本地启动脚本
└── docs/              # 文档
```
