# Footnote Rendering

前端对脚注标记的渲染、交互和 tooltip 展示能力。

## MODIFIED Requirements

### Requirement: CitationTooltip MUST support footnote anchor links

当前 `citationMatcher.ts` 通过匹配 `<a href="https://...">` 来识别引用链接。CitationTooltip MUST 额外支持 `<a href="#ref-N">` 格式的脚注锚点链接。

#### Scenario: Hover on footnote marker shows citation tooltip

- Given: 文章 HTML 中包含 `<sup><a href="#ref-1">[1]</a></sup>`
- And: `citations` 列表的第 1 项（index 0）为 `{url: "https://example.com", title: "示例文章", domain: "example.com", snippet: "这是一段摘要"}`
- When: 用户将鼠标悬停在 `[1]` 上
- Then: 显示 CitationTooltip，包含标题 "示例文章"、域名 "example.com"、摘要
- And: tooltip 中显示编号 `[1]`

#### Scenario: Click on footnote marker scrolls to reference

- Given: 文章 HTML 中包含 `<sup><a href="#ref-2">[2]</a></sup>`
- And: 文末脚注列表中有 `<a id="ref-2"></a>[2] ...`
- When: 用户点击 `[2]`
- Then: 页面滚动到文末脚注列表中对应的 `ref-2` 锚点位置

#### Scenario: Legacy inline citation links still work

- Given: 一篇旧文章中包含 `（<a href="https://example.com">标题</a>）` 格式的内联引用
- And: `citations` 列表中包含对应 URL
- When: 用户悬停在该链接上
- Then: CitationTooltip 仍正常显示（向后兼容）

### Requirement: scanCitationLinks MUST identify both inline and footnote citations

`scanCitationLinks` 函数 MUST 同时支持旧格式（外部 URL 链接）和新格式（`#ref-N` 锚点链接）的引用识别。

#### Scenario: Mixed old and new citation formats

- Given: 文章 HTML 同时包含旧格式 `<a href="https://example.com">标题</a>` 和新格式 `<sup><a href="#ref-1">[1]</a></sup>`
- And: `citations` 列表包含对应数据
- When: `scanCitationLinks` 扫描容器
- Then: 返回结果包含两种格式的匹配项
- And: 新格式通过编号索引匹配，旧格式通过 URL 匹配
