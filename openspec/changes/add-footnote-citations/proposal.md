# Add Footnote Citations

## Status

draft

## Problem

当前博客生成系统已具备基础的来源引用能力：Writer 使用 `{source_NNN}` 占位符标注信息来源，Assembler 将其替换为 `（[标题](url)）` 形式的内联链接。但这种方式存在以下问题：

1. **阅读体验差**：内联的 `（[长标题](长URL)）` 链接打断正文阅读节奏，尤其同一段落引用多个来源时非常冗长
2. **引用与参考列表脱节**：文末"参考资料"来自 Researcher 的 `top_references`，与正文中实际引用的 `{source_NNN}` 不是同一套数据，导致正文引用的来源可能不在参考列表中
3. **无编号脚注机制**：缺乏学术/专业文章常用的编号脚注（如 `[1]`、`[2]`），无法让读者快速定位来源
4. **重复来源未去重**：同一来源在多处引用时，每处都展开为完整链接，而非复用同一编号

## Proposed Solution

引入脚注式引用系统，将 `{source_NNN}` 占位符替换为编号脚注标记（如 `[1]`），并在文末生成与之对应的编号参考文献列表。具体方案：

- **Assembler 层**：新增脚注收集与编号逻辑，将 `{source_NNN}` 替换为带锚点的上标编号 `<sup>[[1]](#ref-1)</sup>`，同时收集所有实际被引用的来源，去重后生成编号脚注列表
- **Footer 模板**：将"参考资料"改为基于实际引用的编号脚注列表，未被正文引用的 `reference_links` 作为"延伸阅读"补充
- **Writer Prompt**：保持 `{source_NNN}` 占位符机制不变，但增强引用指导，鼓励更精确地标注来源
- **前端渲染**：利用已有的 `CitationTooltip` 组件，增强对脚注编号的 hover 交互支持

## Impact

- **Assembler Agent** — 核心变更：引用替换逻辑从内联链接改为编号脚注
- **Footer 模板** (`assembler_footer.j2`) — 参考资料部分重构为编号脚注格式
- **Writer Prompt** (`writer.j2`) — 微调引用指导说明
- **Frontend** — `CitationTooltip` 和 `citationMatcher` 适配脚注编号元素
- **Markdown 渲染** (`useMarkdownRenderer.ts`) — 无需额外 marked 插件（使用 HTML 标记方案）
- **数据库/API** — `citations` 数据结构不变，兼容现有存储

## Alternatives Considered

### 方案 A：Markdown 原生脚注语法 `[^1]`

使用标准 Markdown Extended Syntax 的脚注格式：正文中 `[^1]`，文末 `[^1]: 来源说明`。

- **优点**：标准语法，部分渲染器原生支持
- **缺点**：`marked.js` 不原生支持脚注，需引入 `marked-footnote` 扩展；导出为纯 Markdown 时依赖读者的渲染器也支持该语法；脚注内容格式受限（只能是纯文本或简单 Markdown）
- **结论**：引入额外依赖且兼容性不确定，不采用

### 方案 B：HTML 锚点 + 上标编号（推荐，已选用）

正文中使用 `<sup>[[N]](#ref-N)</sup>`，文末使用 `<a id="ref-N"></a>` 锚点 + 编号列表。

- **优点**：纯 HTML，所有 Markdown 渲染器都支持；支持点击跳转；格式灵活；无需额外依赖
- **缺点**：Markdown 源码中混入少量 HTML 标签
- **结论**：最佳平衡点，兼容性强，采用此方案

### 方案 C：保持内联链接但缩短

将 `（[标题](url)）` 缩短为 `（[来源](url)）` 或仅显示域名。

- **优点**：改动最小
- **缺点**：仍然打断阅读流，根本问题未解决
- **结论**：不够彻底，不采用
