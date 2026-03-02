# 08 - API 参考

## 8.1 API 概览

所有 API 端点以 `/api/` 为前缀，通过 Flask Blueprint 组织。

### 路由注册

```python
# backend/routes/__init__.py
def register_all_blueprints(app):
    app.register_blueprint(blog_bp, url_prefix='/api')
    app.register_blueprint(settings_bp, url_prefix='/api')
    app.register_blueprint(queue_bp, url_prefix='/api')
    app.register_blueprint(scheduler_bp, url_prefix='/api')
    app.register_blueprint(chat_bp, url_prefix='/api')
```

## 8.2 博客生成 API

### POST /api/blog/generate

**创建博客生成任务**（异步）

请求体：

```json
{
    "topic": "Python 异步编程入门",
    "article_type": "tutorial",
    "target_length": "medium",
    "target_audience": "intermediate",
    "audience_adaptation": "default",
    "document_ids": [],
    "image_style": "minimalist",
    "generate_cover_video": false,
    "deep_thinking": false,
    "background_investigation": true,
    "interactive": false,
    "custom_config": null
}
```

响应：

```json
{
    "success": true,
    "task_id": "task_20260226_143000_a1b2c3d4",
    "message": "任务已创建"
}
```

### POST /api/blog/generate-sync

**同步博客生成**（阻塞直到完成）

请求参数同上，响应包含完整生成结果：

```json
{
    "success": true,
    "markdown": "# 完整文章内容...",
    "outline": { ... },
    "sections_count": 4,
    "images_count": 5,
    "code_blocks_count": 2,
    "review_score": 85,
    "seo_keywords": ["Python", "异步", "asyncio"],
    "token_summary": {
        "total_input": 50000,
        "total_output": 12000,
        "by_agent": { ... }
    }
}
```

### POST /api/blog/enhance-topic

**AI 优化主题**

```json
// 请求
{ "topic": "python异步" }

// 响应
{
    "success": true,
    "enhanced_topic": "深入解析 Python asyncio：从事件循环到高性能并发实践"
}
```

## 8.3 任务管理 API

### GET /api/tasks/{task_id}/stream

**SSE 进度流**

返回 `text/event-stream` 类型的 SSE 流：

```
data: {"type": "progress", "stage": "researcher", "progress": 10, "message": "正在搜索背景资料..."}

data: {"type": "progress", "stage": "planner", "progress": 25, "message": "正在生成大纲..."}

data: {"type": "outline_confirm", "outline": {"title": "...", "sections": [...]}}

data: {"type": "progress", "stage": "writer", "progress": 40, "message": "正在撰写第1章..."}

data: {"type": "llm_stream", "content": "在现代...", "stage": "writer"}

data: {"type": "progress", "stage": "questioner", "progress": 60, "message": "深度追问检查..."}

data: {"type": "completed", "results": {"markdown": "...", "review_score": 85}}
```

### GET /api/tasks/{task_id}/status

**轮询任务状态**

```json
{
    "task_id": "task_20260226_143000_a1b2c3d4",
    "status": "running",
    "current_stage": "writer",
    "stage_progress": 60,
    "overall_progress": 40,
    "message": "正在撰写第2章..."
}
```

### POST /api/tasks/{task_id}/resume

**恢复中断的任务**（大纲确认后）

```json
// 接受大纲
{ "action": "accept" }

// 编辑大纲后确认
{
    "action": "edit",
    "outline": {
        "title": "修改后的标题",
        "sections": [ ... ]
    }
}
```

## 8.4 文档管理 API

### POST /api/blog/upload

**上传文档**（PDF/MD/TXT）

`multipart/form-data` 请求：

```
file: <binary>
```

响应：

```json
{
    "success": true,
    "document_id": "doc_a1b2c3d4",
    "filename": "paper.pdf",
    "status": "processing"
}
```

### GET /api/documents/{doc_id}/status

**查询文档解析状态**

```json
{
    "document_id": "doc_a1b2c3d4",
    "status": "completed",  // processing / completed / failed
    "chunks_count": 15,
    "filename": "paper.pdf"
}
```

## 8.5 历史记录 API

### GET /api/blog/history

**获取生成历史**

查询参数：
- `page`: 页码（默认 1）
- `page_size`: 每页条数（默认 10）
- `content_type`: 内容类型过滤

```json
{
    "success": true,
    "records": [
        {
            "id": "hist_001",
            "topic": "Python 异步编程",
            "content_type": "blog",
            "created_at": "2026-02-26T14:30:00",
            "cover_image": "/outputs/images/cover_001.png",
            "sections_count": 4,
            "images_count": 5
        }
    ],
    "total": 50,
    "page": 1,
    "page_size": 10,
    "total_pages": 5
}
```

### GET /api/blog/history/{id}

**获取单条历史详情**

```json
{
    "success": true,
    "record": {
        "id": "hist_001",
        "topic": "Python 异步编程",
        "markdown": "# 完整 Markdown 内容...",
        "outline": { ... },
        "review_score": 85,
        "created_at": "2026-02-26T14:30:00"
    }
}
```

### DELETE /api/blog/history/{id}

**删除历史记录**

```json
{ "success": true }
```

## 8.6 任务队列 API

### GET /api/queue/tasks

**获取队列中的任务列表**

```json
{
    "tasks": [
        {
            "id": "task_001",
            "name": "博客: Python 异步编程",
            "status": "running",
            "created_at": "2026-02-26T14:30:00",
            "progress": 45
        }
    ]
}
```

### POST /api/queue/tasks

**向队列提交新任务**

### DELETE /api/queue/tasks/{task_id}

**取消队列中的任务**

## 8.7 定时调度 API

### GET /api/scheduler/jobs

**获取定时任务列表**

### POST /api/scheduler/jobs

**创建定时任务**

```json
{
    "cron_expression": "0 9 * * 1",
    "topic": "每周 AI 技术动态",
    "article_type": "tutorial",
    "target_length": "medium"
}
```

### DELETE /api/scheduler/jobs/{job_id}

**删除定时任务**

## 8.8 设置 API

### GET /api/settings

**获取当前配置**

### PUT /api/settings

**更新配置**

## 8.9 对话式写作 API

### POST /api/chat/sessions

**创建写作会话**

### POST /api/chat/sessions/{session_id}/messages

**发送消息**

### GET /api/chat/sessions/{session_id}/messages

**获取会话历史**

## 8.10 健康检查

### GET /health

```json
{ "status": "ok", "service": "banana-blog" }
```

## 8.11 SSE 事件协议详解

### 事件类型

| type | 触发时机 | 附加字段 |
|------|----------|----------|
| `progress` | 阶段切换 / 进度更新 | stage, progress, message |
| `llm_stream` | LLM 流式输出 | content, stage |
| `outline_confirm` | 大纲待确认 | outline |
| `outline_confirmed` | 大纲已确认 | — |
| `image_generated` | 图片生成完成 | image_url, section_id |
| `token_summary` | Token 用量更新 | summary |
| `completed` | 生成完成 | results |
| `error` | 发生错误 | message |

### 阶段名称

| stage | 人类可读描述 |
|-------|-------------|
| `researcher` | 素材收集 |
| `planner` | 大纲规划 |
| `writer` | 内容撰写 |
| `check_knowledge` | 知识检查 |
| `refine_search` | 补充搜索 |
| `questioner` | 深度追问 |
| `deepen_content` | 内容深化 |
| `section_evaluate` | 段落评估 |
| `coder_and_artist` | 代码+配图 |
| `reviewer` | 质量审核 |
| `revision` | 内容修订 |
| `factcheck` | 事实核查 |
| `humanizer` | 去 AI 味 |
| `assembler` | 文档组装 |
| `summary_generator` | SEO 生成 |
