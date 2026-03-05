# Refine Footnote Citations

## Status

draft

## Problem

脚注引用功能已上线，但存在两个体验问题：

1. **脚注悬停 tooltip 未生效**：在博客阅读页（`BlogDetail.vue` / `/blog/:id`）悬停脚注标记 `[1]` 时，不会弹出来源信息卡片。原因是 `CitationTooltip` 和 `scanCitationLinks` 仅在生成页（`Generate.vue`）中接入，博客阅读页没有该逻辑，且 `useBlogDetail.ts` 未从 API 响应中提取 `citations` 数据。

2. **"参考文献"区块冗余**：文末同时存在"参考文献"（编号脚注列表）和"参考资料 > 网络来源"（引用链接列表），内容高度重叠。既然正文中的脚注标记 hover 即可查看来源详情，单独的"参考文献"编号列表就不再必要，应当移除，将所有引用来源统一归入"网络来源"列表。

## Proposed Solution

### 优化 1：博客阅读页接入 CitationTooltip

- `useBlogDetail.ts`：从 API 响应中解析 `citations` JSON 字段
- `BlogDetail.vue` 或 `BlogDetailContent.vue`：引入 `CitationTooltip` 组件和 `scanCitationLinks` 函数，在文章渲染后扫描脚注链接并绑定 hover/click 事件（复用 `Generate.vue` 中的逻辑）

### 优化 2：移除"参考文献"区块，统一为"网络来源"

- `assembler_footer.j2`：移除 `## 参考文献` 区块，将 `cited_footnotes` 合并到 `reference_links` 中一起渲染到"网络来源"列表
- `assembler.py`：将已引用来源合并到 `reference_links`（去重）传入 footer 模板，不再单独传 `cited_footnotes`
- 正文中脚注标记的 `#ref-N` 锚点仍保留，指向"网络来源"列表中对应条目的锚点

## Impact

- **`frontend/src/views/BlogDetail.vue`** — 新增 CitationTooltip 集成
- **`frontend/src/components/blog-detail/BlogDetailContent.vue`** — 可能需要配合调整
- **`frontend/src/composables/useBlogDetail.ts`** — 新增 citations 数据映射
- **`backend/infrastructure/prompts/blog/assembler_footer.j2`** — 移除"参考文献"区块，改造"网络来源"
- **`backend/services/blog_generator/agents/assembler.py`** — 合并 cited_footnotes 到 reference_links
