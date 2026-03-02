# Citation Prompt

Writer Prompt 中关于来源引用的指导增强，提升 LLM 引用标注的精准度和覆盖率。

## MODIFIED Requirements

### Requirement: Writer prompt MUST encourage precise source attribution

Writer prompt MUST 包含增强的引用指导，明确脚注的最终呈现效果，鼓励 Writer 更积极地标注来源。

#### Scenario: Writer follows enhanced citation guidance

- Given: Writer prompt 包含增强后的引用指导说明
- And: 当前 section 有 3 个预分配素材
- When: Writer 生成章节内容
- Then: 至少对 `must_use` 素材的关键数据/论点标注了 `{source_NNN}` 占位符
- And: 占位符出现在具体事实、数据、引用语句附近（而非段落末尾泛泛标注）

#### Scenario: Writer prompt explains footnote rendering

- Given: Writer prompt 中说明 `{source_NNN}` 将被渲染为编号脚注（如 `[1]`）
- When: Writer 决定是否标注来源
- Then: Writer 理解脚注不会打断阅读流，因此更倾向于积极标注

### Requirement: Humanizer MUST preserve source placeholders unchanged

Humanizer Agent 在改写时 MUST 保留 `{source_NNN}` 占位符不变。此为已有约束，确认不受本次变更影响。

#### Scenario: Humanizer skips source placeholder in diff

- Given: 原文包含 `根据实测数据，效率提升了 40% {source_002}`
- When: Humanizer 生成替换列表
- Then: 替换列表中的 `old` 字段不包含 `{source_002}`
- And: 替换后的文本仍保留 `{source_002}` 占位符
