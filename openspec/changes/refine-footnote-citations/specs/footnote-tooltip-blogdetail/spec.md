# Footnote Tooltip on Blog Detail Page

博客阅读页对脚注标记的悬停 tooltip 支持。

## ADDED Requirements

### Requirement: BlogDetail page MUST show CitationTooltip on footnote hover

博客阅读页（`/blog/:id`）MUST 在用户悬停脚注标记时显示来源信息卡片，与生成页行为一致。

#### Scenario: Hover footnote marker on blog detail page

- Given: 用户打开一篇已生成的博客文章 `/blog/task_xxx`
- And: 文章正文中包含脚注标记 `<sup><a href="#ref-1" data-source-url="https://example.com">[1]</a></sup>`
- And: 该文章的 `citations` 数据包含 `{url: "https://example.com", title: "示例", domain: "example.com", snippet: "摘要"}`
- When: 用户将鼠标悬停在 `[1]` 上
- Then: 显示 CitationTooltip 卡片，包含来源标题、域名、摘要
- And: tooltip 消失后不影响页面滚动

#### Scenario: Click footnote marker scrolls to reference list

- Given: 文章正文中包含脚注标记 `<a href="#ref-1">[1]</a>`
- And: 文末"网络来源"列表中有 `<a id="ref-1"></a>` 锚点
- When: 用户点击 `[1]`
- Then: 页面平滑滚动到文末对应来源条目

#### Scenario: Old article without citations data

- Given: 用户打开一篇旧文章，该文章的 `citations` 字段为 null
- When: 页面渲染完成
- Then: 不显示任何 tooltip，不报错

### Requirement: useBlogDetail MUST parse citations from API response

`useBlogDetail` composable MUST 从历史记录 API 响应中提取并解析 `citations` JSON 字段。

#### Scenario: API returns citations JSON string

- Given: API 响应中 `record.citations` 为 `'[{"url":"...", "title":"...", "domain":"...", "snippet":"..."}]'`
- When: `useBlogDetail` 处理响应数据
- Then: `blog.citations` 为解析后的 `Citation[]` 数组

#### Scenario: API returns null citations

- Given: API 响应中 `record.citations` 为 null 或不存在
- When: `useBlogDetail` 处理响应数据
- Then: `blog.citations` 为空数组 `[]`
