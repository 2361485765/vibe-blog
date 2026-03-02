# Design: Add Footnote Citations

## Architecture Overview

本变更跨越后端 Assembler 组装逻辑、Jinja2 模板、Writer Prompt 和前端渲染四个子系统，但核心变更集中在 Assembler 层。

```
Writer Agent                    Assembler Agent                    Frontend
─────────────                   ────────────────                   ────────
{source_NNN}     ──→   收集 & 去重 & 编号   ──→   <sup>[[1]](#ref-1)</sup>
占位符                  生成脚注列表                  CitationTooltip hover
                        渲染 footer 模板              点击跳转到脚注
```

## Core Design: Footnote Collection & Numbering

### 数据流

1. **Writer** 在每个 section 的正文中插入 `{source_NNN}` 占位符（NNN = search_results 中的 1-based index），**此行为不变**
2. **Assembler** 在处理每个 section 时：
   - 扫描所有 `{source_NNN}` 占位符
   - 对每个引用的 source，查找 `search_results[NNN-1]` 获取来源信息
   - 基于 URL 去重：相同 URL 的不同 `{source_NNN}` 映射到同一个脚注编号
   - 替换为 `<sup>[[footnote_number]](#ref-footnote_number)</sup>`
3. **Assembler** 在生成 footer 时：
   - 将收集到的已引用来源列表（去重、有序）传入 footer 模板
   - Footer 模板渲染编号脚注列表
   - 未被正文引用的 `reference_links` 归入"延伸阅读"

### 编号规则

- 脚注编号从 1 开始，按首次出现顺序递增
- 同一来源（URL 相同）在不同章节多次引用时，复用相同编号
- 脚注编号在全文范围内唯一（非章节内编号）

### 去重策略

```python
# 伪代码
footnote_map = {}  # url -> footnote_number
footnote_list = []  # [(number, title, url), ...]
next_number = 1

for each {source_NNN} in all sections:
    source = search_results[NNN - 1]
    url = normalize(source.url)
    if url not in footnote_map:
        footnote_map[url] = next_number
        footnote_list.append((next_number, source.title, url))
        next_number += 1
    replace {source_NNN} with <sup>[[footnote_map[url]]](#ref-{footnote_map[url]})</sup>
```

## Assembler Changes

### 新方法：`build_footnote_citations`

Assembler 需要拆分当前的 `assemble()` 流程为两阶段：

1. **Phase 1 — 收集阶段**：遍历所有 section 内容，扫描 `{source_NNN}`，构建 `footnote_map` 和 `footnote_list`
2. **Phase 2 — 替换阶段**：用脚注编号替换占位符，渲染 footer

这需要将当前逐 section 调用 `replace_source_references` 的方式改为：
- 先全局扫描 → 构建映射
- 再逐 section 替换

### 输出格式

正文中的脚注标记：
```html
根据实测数据，效率提升了 40%<sup>[[1]](#ref-1)</sup>
```

文末脚注列表：
```markdown
## 参考文献

<a id="ref-1"></a>[1] [文章标题](https://example.com/article)

<a id="ref-2"></a>[2] [另一篇文章](https://example.com/another)
```

## Footer Template Restructuring

当前 `assembler_footer.j2` 的"参考资料"区块分为"文档来源"和"网络来源"两部分，数据分别来自 `document_references` 和 `reference_links`。

变更后的结构：

```
## 参考文献（来自正文引用的脚注列表）
[1] [标题](url)
[2] [标题](url)
...

## 延伸阅读（来自 reference_links 中未被正文引用的来源）
- [标题](url)
- [标题](url)

### 文档来源（如有上传文档，保持不变）
- 文档标题 (文件名)
```

## Writer Prompt Adjustments

Writer prompt (`writer.j2`) 中关于 `{source_NNN}` 的指导微调：

- 保持占位符格式不变
- 增加指导：每个章节至少标注 1-2 个关键数据/论点的来源
- 明确：占位符会被转换为编号脚注，鼓励精准引用而非泛泛标注

## Frontend Adaptation

### CitationTooltip 适配

当前 `citationMatcher.ts` 通过匹配 `<a>` 标签的 `href` 来识别引用。脚注方案产生的 HTML 结构为：

```html
<sup><a href="#ref-1">[1]</a></sup>
```

需要调整 `scanCitationLinks` 逻辑：
- 识别 `href` 为 `#ref-N` 模式的锚点链接
- 从 `citations` 列表中按编号索引匹配（而非 URL 匹配）
- 复用已有的 `CitationTooltip` 组件展示来源详情

### 脚注列表交互

文末脚注列表中的编号项也应支持 hover 展示来源摘要（复用 `CitationTooltip`）。

## Backward Compatibility

- **已生成文章**：已存储在数据库中的文章（`final_markdown` 字段）仍为旧格式（内联链接），不受影响
- **citations API 数据**：`citations` 列表结构不变，前端 tooltip 仍可基于 URL 匹配旧文章
- **导出功能**：HTML 锚点方案在 PDF/图片导出时正常渲染

## Trade-offs

| 决策 | 选择 | 理由 |
|------|------|------|
| 脚注格式 | HTML `<sup>` + 锚点 | 兼容所有渲染器，无需额外 marked 插件 |
| 编号范围 | 全文统一编号 | 符合学术论文惯例，便于引用 |
| 去重粒度 | URL 级别 | 同一页面的不同段落视为同一来源 |
| 旧文章迁移 | 不迁移 | 已生成文章保持原格式，成本效益比低 |
