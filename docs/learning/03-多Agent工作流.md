# 03 - 多 Agent 工作流

## 3.1 LangGraph 基础概念

vibe-blog 的 Agent 编排基于 [LangGraph](https://langchain-ai.github.io/langgraph/)，核心概念：

- **StateGraph**: 有状态的有向图，节点之间通过共享状态传递数据
- **Node**: 图中的处理节点，每个节点是一个 Python 函数，接收 state 返回更新后的 state
- **Edge**: 节点之间的连接，可以是固定边或条件边
- **Conditional Edge**: 根据 state 中的值动态决定下一步走向哪个节点
- **SharedState**: 所有节点共享的 TypedDict，是数据在 Agent 间流转的载体
- **Checkpointer**: 支持中断恢复的检查点机制

## 3.2 工作流全貌

工作流定义在 `backend/services/blog_generator/generator.py` 的 `BlogGenerator._build_workflow()` 方法中。

### 节点列表

| 节点名 | 对应方法 | Agent | 说明 |
|--------|----------|-------|------|
| `researcher` | `_researcher_node` | ResearcherAgent | 素材收集 |
| `planner` | `_planner_node` | PlannerAgent | 大纲规划 |
| `writer` | `_writer_node` | WriterAgent | 内容撰写 |
| `check_knowledge` | `_check_knowledge_node` | SearchCoordinator | 知识空白检查 |
| `refine_search` | `_refine_search_node` | SearchCoordinator | 细化搜索 |
| `enhance_with_knowledge` | `_enhance_with_knowledge_node` | WriterAgent | 知识增强 |
| `questioner` | `_questioner_node` | QuestionerAgent | 深度追问 |
| `deepen_content` | `_deepen_content_node` | WriterAgent | 内容深化 |
| `section_evaluate` | `_section_evaluate_node` | QuestionerAgent | 段落多维评估 |
| `section_improve` | `_section_improve_node` | WriterAgent | 段落精准改进 |
| `coder_and_artist` | `_coder_and_artist_node` | Coder + Artist | 代码+配图（异步） |
| `cross_section_dedup` | `_cross_section_dedup_node` | — | 跨章节去重 |
| `consistency_check` | `_consistency_check_node` | ThreadChecker + VoiceChecker | 一致性检查 |
| `reviewer` | `_reviewer_node` | ReviewerAgent | 质量审核 |
| `revision` | `_revision_node` | WriterAgent | 修订 |
| `factcheck` | `_factcheck_node` | FactCheckAgent | 事实核查 |
| `text_cleanup` | `_text_cleanup_node` | — | 文本清理（纯正则）|
| `humanizer` | `_humanizer_node` | HumanizerAgent | 去 AI 味 |
| `wait_for_images` | `_wait_for_images_node` | — | 等待异步配图 |
| `assembler` | `_assembler_node` | AssemblerAgent | 文档组装 |
| `summary_generator` | `_summary_generator_node` | SummaryGeneratorAgent | 导读+SEO |

### 流程图

```
START
  │
  ▼
researcher ──────────────────────────────────────────────────┐
  │                                                           │
  ▼                                                           │
planner                                                       │
  │                                                           │
  ▼                                                           │
writer                                                        │
  │                                                           │
  ├──[mini模式]──→ questioner                                  │
  │                                                           │
  └──[其他模式]──→ check_knowledge ◄─── enhance_with_knowledge │
                      │                       ▲               │
                      ├──[有知识空白]──→ refine_search ──┘     │
                      │                                       │
                      └──[无空白]──→ questioner                │
                                      │                       │
                      ┌──[需要深化]──→ deepen_content          │
                      │               │                       │
                      │   ┌──[达上限]─┤                       │
                      │   │           │                       │
                      │   │   [未达上限]→ questioner (回循环)   │
                      │   │                                   │
                      │   └──→ section_evaluate               │
                      │           │                           │
                      └──[够深]──→│                           │
                                  │                           │
                      ┌──[需改进]─┤                           │
                      │           │                           │
                      │   section_improve → section_evaluate  │
                      │                    (回循环评估)        │
                      │                                       │
                      └──[合格]──→ coder_and_artist           │
                                      │                       │
                                      ▼                       │
                              cross_section_dedup             │
                                      │                       │
                                      ▼                       │
                              consistency_check               │
                                      │                       │
                                      ▼                       │
                                  reviewer ◄── revision       │
                                      │          ▲            │
                                      ├──[不合格]─┘           │
                                      │                       │
                                      └──[合格]──→ factcheck  │
                                                     │        │
                                                     ▼        │
                                                text_cleanup  │
                                                     │        │
                                                     ▼        │
                                                 humanizer    │
                                                     │        │
                                                     ▼        │
                                              wait_for_images │
                                                     │        │
                                                     ▼        │
                                                 assembler    │
                                                     │        │
                                                     ▼        │
                                            summary_generator  │
                                                     │        │
                                                     ▼        │
                                                    END       │
```

## 3.3 条件路由详解

工作流中有多个条件边（`add_conditional_edges`），控制着质量反馈循环：

### 3.3.1 知识空白检查路由

```python
def _should_check_knowledge(state) -> "check" | "skip":
    # mini 模式跳过知识空白检查
    if state['target_length'] == 'mini':
        return "skip"  # 直接进入 questioner
    return "check"     # 进入 check_knowledge
```

### 3.3.2 细化搜索路由

```python
def _should_refine_search(state) -> "search" | "continue":
    # 需要同时满足：StyleProfile 允许 + 有知识空白 + 未超搜索次数上限
    gaps = state['knowledge_gaps']
    search_count = state['search_count']
    max_count = state['max_search_count']
    
    if gaps and search_count < max_count:
        important_gaps = [g for g in gaps if g['gap_type'] in ['missing_data', 'vague_concept']]
        if important_gaps:
            return "search"
    return "continue"
```

### 3.3.3 深化路由

```python
def _should_deepen(state) -> "deepen" | "continue":
    count = state['questioning_count']
    max_rounds = style.max_questioning_rounds  # 来自 StyleProfile
    
    if count >= max_rounds:
        return "continue"
    if not state['all_sections_detailed']:
        return "deepen"
    return "continue"
```

### 3.3.4 段落改进路由

```python
def _should_improve_sections(state) -> "improve" | "continue":
    if not state['needs_section_improvement']:
        return "continue"
    if state['section_improve_count'] >= 2:
        return "continue"  # 最多改进 2 轮
    # 收敛检测：改进幅度 < 0.3 则停止
    if prev_avg > 0 and (curr_avg - prev_avg) < 0.3:
        return "continue"
    return "improve"
```

### 3.3.5 修订路由

```python
def _should_revise(state) -> "revision" | "assemble":
    if revision_count >= style.max_revision_rounds:
        return "assemble"
    
    # high_only 模式：只处理严重问题
    if style.revision_severity_filter == "high_only":
        high_issues = [i for i in review_issues if i['severity'] == 'high']
        return "revision" if high_issues else "assemble"
    
    if not state['review_approved']:
        return "revision"
    return "assemble"
```

## 3.4 三大质量控制循环

### 循环 1：知识空白补充

```
Writer → check_knowledge → refine_search → enhance_with_knowledge → check_knowledge
```

当 Writer 完成初稿后，SearchCoordinator 检测知识空白，触发额外搜索，用新知识增强内容。

**退出条件**：无空白 OR 搜索次数达上限（mini=1, short=3, medium=5, long=8）

### 循环 2：深度追问

```
Questioner → deepen_content → Questioner
```

Questioner 评估每个章节的深度，标记不够深入的模糊点。Writer 根据这些追问结果深化内容。

**退出条件**：所有章节足够深入 OR 追问次数达上限（mini=1, medium=2, long=3）

### 循环 3：质量审核

```
Reviewer → revision → Reviewer
```

Reviewer 对完整性、逻辑性、原创性等维度打分，不合格时触发修订。

**退出条件**：审核通过 OR 修订次数达上限（mini=1, medium=3, long=5）

## 3.5 递归限制与预算管理

LangGraph 有递归限制保护机制。`_build_config()` 动态计算：

```python
def _build_config(self, state):
    base_nodes = 20  # 实际节点数
    max_loops = (
        style.max_questioning_rounds * 2
        + style.max_revision_rounds * 2
        + 2  # section_evaluate <-> improve
    )
    recursion_limit = base_nodes + max_loops + 5
```

不同模式的递归限制：

| 模式 | 追问轮数 | 修订轮数 | 递归限制 |
|------|----------|----------|----------|
| mini | 1 | 1 | ~29 |
| short | 1 | 1 | ~29 |
| medium | 2 | 3 | ~35 |
| long | 3 | 5 | ~41 |

## 3.6 中间件管道

每个节点都通过 `MiddlewarePipeline.wrap_node()` 包装，提供横切关注点：

```python
workflow.add_node("researcher", self.pipeline.wrap_node("researcher", self._researcher_node))
```

中间件执行顺序：

```
before_node (正序)
    TracingMiddleware     → 设置追踪上下文
    TaskLogMiddleware     → 记录节点开始时间
    ReducerMiddleware     → 状态归约
    ErrorTrackingMiddleware → 错误追踪
    ContextManagementMiddleware → 上下文长度管理
    TokenBudgetMiddleware → Token 预算检查
    ContextPrefetchMiddleware → 知识库预取
    
─── 节点执行 ───

after_node (逆序)
    ContextPrefetchMiddleware
    TokenBudgetMiddleware
    ...
    TracingMiddleware     → 记录执行耗时
```

## 3.7 并行执行引擎

内容深化、修订、一致性检查等操作涉及多个章节的独立处理，系统使用 `ParallelTaskExecutor` 并行加速：

```python
results = self.executor.run_parallel(tasks, config=TaskConfig(
    name="content_deepen", timeout_seconds=120,
))
```

并行行为由 `StyleProfile.enable_parallel` 控制。当 `TRACE_ENABLED=true` 时自动关闭并行以确保 Langfuse 追踪链路完整。

## 3.8 交互式大纲确认

基于 LangGraph 原生 `interrupt` 机制，Planner 生成大纲后可以暂停等待用户确认：

```python
if outline and self._interactive and not auto_confirm:
    user_decision = interrupt({
        "type": "confirm_outline",
        "title": outline["title"],
        "sections": outline["sections"],
    })
```

前端通过 `POST /api/tasks/{task_id}/resume` 发送用户决策（接受或编辑），工作流继续执行。

mini 模式或 `OUTLINE_AUTO_CONFIRM=true` 时跳过交互直接继续。

## 3.9 异步配图策略

配图生成（Artist Agent）耗时约 400 秒，但后续的去重、审核、去 AI 味等节点不依赖图片。因此采用异步策略：

```
coder_and_artist 节点:
    1. 同步执行 Coder（很快）
    2. ThreadPoolExecutor 启动 Artist 后台线程
    3. 将 future 存入 state['_image_future']
    4. 立即返回，不等待

... 后续节点正常执行 ...

wait_for_images 节点:
    1. 取出 future
    2. future.result(timeout=600) 等待完成
    3. 合并图片结果到 state
```

这样在文字处理期间图片就在并行生成，大幅缩短总耗时。
