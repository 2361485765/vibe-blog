# Footnote Assembly

Assembler Agent 的脚注收集、编号、去重与替换能力，以及文末脚注列表的生成。

## MODIFIED Requirements

### Requirement: Assembler MUST replace source placeholders with numbered footnote markers

当前 Assembler 的 `replace_source_references` 将 `{source_NNN}` 替换为内联链接 `（[标题](url)）`。变更为：Assembler MUST 全局收集所有 section 中的 `{source_NNN}`，基于 URL 去重并分配全文统一编号，替换为 HTML 上标脚注标记。

#### Scenario: Single source referenced once

- Given: 一篇文章的某个 section 内容包含 `{source_001}`
- And: `search_results[0]` 的 title 为 "Redis 性能优化指南"，url 为 "https://example.com/redis"
- When: Assembler 执行脚注替换
- Then: `{source_001}` 被替换为 `<sup>[[1]](#ref-1)</sup>`
- And: 脚注列表包含条目 `[1] [Redis 性能优化指南](https://example.com/redis)`

#### Scenario: Same source referenced in multiple sections

- Given: Section 1 包含 `{source_003}`，Section 3 也包含 `{source_003}`
- And: `search_results[2]` 的 url 为 "https://example.com/article"
- When: Assembler 执行脚注替换
- Then: 两处 `{source_003}` 都被替换为相同的脚注编号（如 `<sup>[[2]](#ref-2)</sup>`）
- And: 脚注列表中该来源只出现一次

#### Scenario: Different source indices pointing to same URL

- Given: Section 1 包含 `{source_001}`，Section 2 包含 `{source_005}`
- And: `search_results[0]` 和 `search_results[4]` 的 URL 相同（去重场景）
- When: Assembler 执行脚注替换
- Then: 两处占位符替换为相同的脚注编号
- And: 脚注列表中该 URL 只出现一次

#### Scenario: Source index out of range

- Given: 内容包含 `{source_099}` 但 `search_results` 只有 10 项
- When: Assembler 执行脚注替换
- Then: `{source_099}` 保持原样不替换（与当前行为一致）

#### Scenario: No search results available

- Given: `search_results` 为空列表
- When: Assembler 执行脚注替换
- Then: 所有 `{source_NNN}` 占位符保持原样
- And: 不生成脚注列表

### Requirement: Footer MUST render cited footnotes and supplementary references separately

文末参考资料 MUST 区分为两部分：正文中实际引用的编号脚注列表，以及未被引用的补充参考资料。

#### Scenario: Footer with both cited and uncited references

- Given: 正文引用了 source_001 和 source_003（对应脚注 [1] 和 [2]）
- And: `reference_links` 包含 5 个来源，其中 2 个与被引用来源 URL 相同
- When: Assembler 渲染 footer
- Then: "参考文献"区块包含编号 [1] 和 [2]，带锚点 `<a id="ref-1"></a>` 和 `<a id="ref-2"></a>`
- And: "延伸阅读"区块包含剩余 3 个未被引用的 reference_links
- And: 文档来源（document_references）独立展示，不受脚注逻辑影响

#### Scenario: All reference links are cited in text

- Given: `reference_links` 中的所有来源都已被正文引用
- When: Assembler 渲染 footer
- Then: "参考文献"区块包含所有编号脚注
- And: "延伸阅读"区块不渲染（或渲染为空）

#### Scenario: No source placeholders in text

- Given: Writer 未使用任何 `{source_NNN}` 占位符
- And: `reference_links` 有 3 个来源
- When: Assembler 渲染 footer
- Then: "参考文献"区块不渲染
- And: `reference_links` 全部进入"延伸阅读"或保持为"参考资料"（向后兼容）

## ADDED Requirements

### Requirement: Footnote numbering MUST be globally unique and ordered by first appearance

脚注编号 MUST 在全文范围内从 1 开始按首次出现顺序递增，确保编号连续无间隔。

#### Scenario: Sequential footnote numbering across sections

- Given: Section 1 引用 source_003（首次出现），Section 2 引用 source_001（首次出现），Section 3 引用 source_003（再次出现）
- When: Assembler 分配脚注编号
- Then: source_003 获得脚注编号 1（首次在 Section 1 出现）
- And: source_001 获得脚注编号 2（首次在 Section 2 出现）
- And: Section 3 中的 source_003 复用编号 1
- And: 脚注列表按 [1], [2] 顺序排列
