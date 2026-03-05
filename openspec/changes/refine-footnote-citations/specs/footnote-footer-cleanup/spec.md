# Footnote Footer Cleanup

移除冗余的"参考文献"区块，将脚注引用来源合并到"网络来源"列表中。

## REMOVED Requirements

### Requirement: Footer MUST NOT render a separate "参考文献" section

文末 MUST NOT 再单独渲染"参考文献"编号脚注列表。所有引用来源统一归入"网络来源"。

#### Scenario: Article with cited footnotes

- Given: 正文中引用了 source_001 和 source_003（脚注 [1] 和 [2]）
- When: Assembler 渲染文末 footer
- Then: 不出现 `## 参考文献` 标题
- And: 不出现独立的 `[1] [标题](url)` 编号脚注列表

## MODIFIED Requirements

### Requirement: "网络来源" list MUST include all cited and uncited references with anchors

"网络来源"列表 MUST 包含所有来源（正文引用 + 补充参考），已引用来源排在前面并附带锚点。

#### Scenario: Mixed cited and uncited references in unified list

- Given: 正文引用了 2 个来源（脚注 [1] 和 [2]）
- And: 还有 3 个未被引用的补充参考
- When: Assembler 渲染 footer 的"网络来源"列表
- Then: 列表前 2 项为已引用来源，附带 `<a id="ref-1"></a>` 和 `<a id="ref-2"></a>` 锚点
- And: 列表后 3 项为补充参考来源，无锚点
- And: 所有 5 项均以编号列表形式渲染
- And: 同一 URL 不重复出现

#### Scenario: No cited footnotes, only reference links

- Given: 正文中没有使用 `{source_NNN}` 占位符
- And: `reference_links` 有 3 个来源
- When: Assembler 渲染 footer
- Then: "网络来源"列表正常显示 3 个来源，无锚点

#### Scenario: Footnote anchor click lands on correct item

- Given: 正文中脚注 `[2]` 的链接为 `<a href="#ref-2">`
- And: 文末"网络来源"列表第 2 项为 `<a id="ref-2"></a>2. [标题](url)`
- When: 用户点击正文中的 `[2]`
- Then: 页面滚动到"网络来源"列表中的第 2 项
