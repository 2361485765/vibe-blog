# 04 - Agent 详解

## 4.1 Agent 总览

vibe-blog 拥有 10+ 个专业化 Agent，每个 Agent 都是一个 Python 类，核心职责明确。

| Agent | 文件 | 职责 | LLM 级别 |
|-------|------|------|----------|
| ResearcherAgent | `agents/researcher.py` | 联网搜索 + 素材提炼 | smart |
| PlannerAgent | `agents/planner.py` | 文章大纲设计 | strategic |
| WriterAgent | `agents/writer.py` | 章节正文撰写 | smart |
| QuestionerAgent | `agents/questioner.py` | 深度追问 + 段落评估 | fast |
| CoderAgent | `agents/coder.py` | 可运行代码示例 | smart |
| ArtistAgent | `agents/artist.py` | Mermaid 图表 + AI 封面图 | fast |
| ReviewerAgent | `agents/reviewer.py` | 质量审核打分 | strategic |
| AssemblerAgent | `agents/assembler.py` | Markdown 组装 | — |
| SearchCoordinator | `agents/search_coordinator.py` | 多轮搜索策略 | fast |
| HumanizerAgent | `agents/humanizer.py` | 去 AI 味润色 | smart |
| FactCheckAgent | `agents/factcheck.py` | 事实核查 | smart |
| ThreadCheckerAgent | `agents/thread_checker.py` | 叙事一致性检查 | fast |
| VoiceCheckerAgent | `agents/voice_checker.py` | 语气一致性检查 | fast |
| SummaryGeneratorAgent | `agents/summary_generator.py` | SEO + 导读生成 | fast |

### LLM 三级模型策略

通过 `TieredLLMProxy` 实现：

- **fast**: 轻量级任务（追问、评估、检查），低延迟低成本
- **smart**: 主力写作和研究任务，质量与速度兼顾
- **strategic**: 关键决策（大纲、审核），追求最高质量

配置方式：`LLM_FAST` / `LLM_SMART` / `LLM_STRATEGIC` 环境变量。不配置则全部退化为 `TEXT_MODEL`。

## 4.2 ResearcherAgent — 素材收集师

**源文件**: `backend/services/blog_generator/agents/researcher.py` (891 行)

### 职责

接收用户主题，通过联网搜索和文档知识融合，收集写作所需的全部背景资料。

### 核心流程

```
1. 生成搜索查询词（LLM 扩展用户主题为多个搜索词）
2. 联网搜索（智谱 / Serper / 搜狗 三引擎路由）
3. 深度抓取（可选，Jina 对 TOP-N 结果全文抓取）
4. 本地素材库匹配（可选）
5. 文档知识融合（用户上传的 PDF/MD/TXT）
6. LLM 摘要与提炼（背景知识 + 核心概念 + 教学设计分析）
7. 缓存结果
```

### 搜索增强功能

- **SmartSearchService**: 自动检测 AI 话题，扩展到权威博客源
- **DeepScraper**: Jina Reader + httpx 抓取搜索结果的全文
- **LocalMaterialStore**: 扫描本地 `materials/` 目录的 Markdown 文件

### 输出到 State

```python
{
    'search_results': [...],        # 搜索结果列表
    'background_knowledge': "...",   # 背景知识摘要
    'key_concepts': [...],           # 核心概念列表
    'reference_links': [...],        # 参考链接
    'instructional_analysis': {...}, # 教学设计分析
    'verbatim_data': [...],          # 需要原样保留的数据
    'distilled_sources': [...],      # 提炼后的结构化素材
    'content_gaps': [...],           # 内容缺口
}
```

## 4.3 PlannerAgent — 大纲规划师

**源文件**: `backend/services/blog_generator/agents/planner.py` (311 行)

### 职责

根据素材收集结果设计文章大纲，包括标题、章节结构、每章节的配图规划等。

### 输入

- `topic`: 主题
- `article_type`: 文章类型
- `background_knowledge`: 背景知识
- `key_concepts`: 核心概念
- `instructional_analysis`: 教学设计分析
- `target_sections_count`, `target_word_count` 等量化目标

### 输出格式 (BlogOutline)

```json
{
    "title": "深度解析 Python 异步编程",
    "subtitle": "从 asyncio 到生产实践",
    "reading_time": 15,
    "article_type": "tutorial",
    "introduction": "...",
    "core_value": "...",
    "table_of_contents": ["第1章: ...", "第2章: ..."],
    "sections": [
        {
            "id": "section_1",
            "title": "异步编程基础概念",
            "key_concept": "事件循环与协程",
            "content_outline": ["什么是异步", "为什么需要异步"],
            "image_type": "flowchart",
            "image_description": "事件循环工作流程图",
            "code_blocks": 1,
            "key_quote": ""
        }
    ],
    "conclusion_summary_points": ["..."],
    "reference_links": ["..."]
}
```

### 交互式确认

生成大纲后可暂停等待用户确认（基于 LangGraph interrupt）：
- 用户可以接受大纲
- 用户可以编辑章节标题、顺序、内容要点
- mini 模式自动确认

## 4.4 WriterAgent — 内容撰写师

**源文件**: `backend/services/blog_generator/agents/writer.py` (612 行)

### 职责

根据大纲逐章撰写 Markdown 格式的正文内容。是整个系统中调用 LLM 最频繁的 Agent。

### 核心方法

| 方法 | 用途 |
|------|------|
| `run(state)` | 根据大纲逐章撰写（并行） |
| `enhance_section(...)` | 根据追问结果深化章节 |
| `correct_section(...)` | 修正审核发现的问题 |
| `improve_section(...)` | 根据段落评估改进章节 |

### 并行写作

Writer 对多个章节使用 `ThreadPoolExecutor` 并行撰写（默认 3 个 worker）：

```python
MAX_WORKERS = int(os.environ.get('BLOG_GENERATOR_MAX_WORKERS', '3'))

with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    futures = {
        executor.submit(self._write_single_section, section, ...): section
        for section in outline['sections']
    }
```

mini 模式强制并行以加速生成；`TRACE_ENABLED=true` 时关闭并行以保证 Langfuse 追踪链路完整。

### 写作模板体系

通过 `PromptComposer` 支持写作模板和风格注入：
- 模板（tutorial, problem_solution, narrative, comparison 等）
- 风格（professional, casual, academic, storytelling 等）

## 4.5 QuestionerAgent — 深度追问官

**源文件**: `backend/services/blog_generator/agents/questioner.py` (351 行)

### 职责

评估章节内容的深度是否足够，识别模糊点并生成追问问题。

### 核心方法

| 方法 | 用途 |
|------|------|
| `run(state)` | 对所有章节进行深度检查 |
| `evaluate_section(...)` | 段落多维度评估（69.04 Generator-Critic Loop） |

### 输出格式 (QuestionResult)

```json
{
    "section_id": "section_1",
    "is_detailed_enough": false,
    "depth_score": 45,
    "vague_points": [
        {
            "location": "第三段",
            "issue": "缺乏具体的性能数据",
            "question": "async 比 sync 快多少？有 benchmark 吗？",
            "suggestion": "补充性能对比数据或实验结果"
        }
    ]
}
```

### 段落多维评估

`evaluate_section()` 方法从多个维度打分：
- 内容完整性
- 逻辑连贯性
- 上下文衔接
- overall_quality（综合分，< 7.0 需改进）

## 4.6 CoderAgent — 代码生成师

**源文件**: `backend/services/blog_generator/agents/coder.py` (296 行)

### 职责

为文章生成可运行的代码示例、运行输出和代码解释。

### 输出格式 (CodeBlock)

```json
{
    "id": "code_1",
    "code": "import asyncio\n\nasync def main():\n    ...",
    "output": "Hello, async world!",
    "explanation": "这段代码展示了基本的 asyncio 用法...",
    "language": "python"
}
```

## 4.7 ArtistAgent — 配图师

**源文件**: `backend/services/blog_generator/agents/artist.py` (1228 行，最大文件之一)

### 职责

- 为每个章节生成 **Mermaid 图表**
- 生成 **AI 封面图**（通过 Nano Banana Pro API）
- 为章节生成 **AI 配图**（支持多种图片风格）

### 图片风格

系统支持多种 AI 图片风格：
- academic（学术）
- cartoon（卡通）
- chiikawa（可爱风）
- dark_tech（暗黑科技）
- ink_wash（水墨）
- minimalist（极简）
- whiteboard（白板）
- biesty（立体）

风格通过 `infrastructure/prompts/image_styles/` 目录下的 Jinja2 模板配置。

### 异步生成

ArtistAgent 通过 `ThreadPoolExecutor` 在后台异步执行，不阻塞后续文本处理节点。

## 4.8 ReviewerAgent — 质量审核员

**源文件**: `backend/services/blog_generator/agents/reviewer.py` (175 行)

### 职责

从多个维度审核文章质量，标记问题并决定是否通过。

### 审核维度

- **completeness**: 内容完整性
- **logic**: 逻辑连贯性
- **verbatim_violation**: 是否篡改了需要原样保留的数据
- **learning_objective_gap**: 学习目标覆盖度

### 输出

```json
{
    "review_score": 85,
    "review_approved": true,
    "review_issues": [
        {
            "section_id": "section_2",
            "issue_type": "completeness",
            "severity": "medium",
            "description": "缺少错误处理的讨论",
            "suggestion": "增加 try/except 异常处理示例"
        }
    ]
}
```

## 4.9 AssemblerAgent — 文档组装师

**源文件**: `backend/services/blog_generator/agents/assembler.py` (272 行)

### 职责

将所有生成内容组装成最终的 Markdown 文档。不调用 LLM，纯模板拼接。

### 组装结构

```markdown
# [文章标题]

![封面图](cover_image_path)

**摘要**: [AI 生成的摘要]

---

## 目录
- 第1章: ...
- 第2章: ...

---

## 第1章: [标题]
[正文内容，含 Mermaid 图表、代码块]

## 第2章: [标题]
...

---

## 代码示例
[完整可运行代码]

---

## 参考资料
1. [来源1](url1)
2. [来源2](url2)
```

### Markdown 修复

`_fix_markdown_separators()` 处理常见的格式问题：
- 确保 `---` 前后有空行（避免被解析为 Setext 标题）
- 跳过代码块内的 `---`

## 4.10 SearchCoordinator — 搜索协调器

**源文件**: `backend/services/blog_generator/agents/search_coordinator.py` (296 行)

### 职责

在 Writer 完成初稿后，检测知识空白并协调多轮搜索。

### 核心方法

| 方法 | 用途 |
|------|------|
| `run(state)` | 检测知识空白 |
| `refine_search(gaps, state)` | 根据空白点执行针对性搜索 |

### 知识空白类型

```python
class KnowledgeGap:
    gap_type: "missing_data" | "vague_concept" | "no_example"
    description: str
    suggested_query: str
    section_id: Optional[str]
```

## 4.11 HumanizerAgent — 去 AI 味

**源文件**: `backend/services/blog_generator/agents/humanizer.py` (350 行)

### 职责

消除 AI 生成文本的典型特征，使文章读起来更自然。处理方式包括：
- 替换 AI 常用的过渡词（"总的来说"、"综上所述"等）
- 增加口语化表达
- 调整句式结构

## 4.12 FactCheckAgent — 事实核查

**源文件**: `backend/services/blog_generator/agents/factcheck.py` (195 行)

### 职责

对文章中的事实性声明进行核查，确保数据和结论的准确性。

### 输出

```json
{
    "overall_score": 90,
    "claims": [
        {
            "claim": "Python 3.10 引入了结构化模式匹配",
            "verdict": "verified",
            "source": "Python 官方文档"
        }
    ],
    "fix_instructions": "..."
}
```

## 4.13 Prompt 模板体系

所有 Agent 的 Prompt 都通过 Jinja2 模板管理，位于 `backend/infrastructure/prompts/` 目录：

```
infrastructure/prompts/
├── blog/
│   ├── writer.j2           # Writer 写作 Prompt
│   ├── search_router.j2    # 搜索路由 Prompt
│   ├── search_query.j2     # 搜索查询生成
│   ├── questioner.j2       # 追问 Prompt
│   └── humanizer.j2        # 去 AI 味 Prompt
├── reviewer/
│   ├── quality_review.j2   # 质量审核
│   ├── depth_check.j2      # 深度检查
│   └── readability_check.j2 # 可读性检查
├── image_styles/
│   ├── academic.j2          # 学术风格
│   ├── cartoon.j2           # 卡通风格
│   └── ...                  # 更多风格
└── shared/
    └── ...                  # 共享模板
```

通过 `PromptManager` 统一加载和渲染，支持变量注入：

```python
pm = get_prompt_manager()
prompt = pm.render_writer(
    topic=topic,
    section_title=section['title'],
    background_knowledge=background,
    ...
)
```
