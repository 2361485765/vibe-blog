# Design: Refine Footnote Citations

## 优化 1：BlogDetail 页接入 CitationTooltip

### 数据流

```
DB (history_records.citations)
  → API GET /api/history/:id  (返回 citations JSON 字符串)
  → useBlogDetail.ts          (解析 JSON → Citation[])
  → BlogDetail.vue            (传递 citations + 文章 HTML 容器 ref)
  → scanCitationLinks()       (扫描 <a data-source-url="..."> 元素)
  → CitationTooltip           (hover 显示来源卡片)
```

### 复用策略

`Generate.vue` 中已有完整的 citation hover 逻辑（`setupCitationHover` 函数）。
`BlogDetail.vue` 可以将此逻辑抽取为共享 composable `useCitationTooltip`，
或直接在 `BlogDetail.vue` 中复制同样的 setup 逻辑（更简单，因为逻辑量很小）。

推荐直接在 `BlogDetail.vue` 中实现，避免重构 `Generate.vue` 引入风险。

### 兼容性

- 旧文章（未存储 `citations`）：`citations` 为 null/空，tooltip 逻辑自动跳过
- 旧格式脚注（内联链接 `（[标题](url)）`）：`scanCitationLinks` 已支持外部 URL 匹配

## 优化 2：移除"参考文献"，统一"网络来源"

### 当前 footer 结构

```
## 参考文献                    ← 来自 cited_footnotes（正文引用的来源）
[1] [标题](url)
[2] [标题](url)

## 参考资料
### 🌐 网络来源               ← 来自 reference_links（未被引用的补充来源）
1. [标题](url)
2. [标题](url)
```

### 目标 footer 结构

```
## 参考资料
### 📄 文档来源               ← 保持不变（如有上传文档）
### 🌐 网络来源               ← 合并全部来源（cited + uncited），去重
<a id="ref-1"></a>1. [标题](url)
<a id="ref-2"></a>2. [标题](url)
3. [标题](url)                ← 未被正文引用的补充来源
```

### 合并逻辑

在 `assembler.py` 的 `assemble()` 方法中：
1. 将 `cited_footnotes` 列表中的来源按编号顺序排在前面
2. 将 `uncited_references` 中未重复的来源追加在后面
3. 统一传入 footer 模板的 `reference_links` 列表
4. 每个已引用条目附带 `ref_id` 字段（如 `ref-1`），用于锚点渲染

### 锚点保留

正文中 `<a href="#ref-1">` 仍需跳转到对应来源。
在合并后的"网络来源"列表中，已引用条目前添加 `<a id="ref-N"></a>` 锚点。
