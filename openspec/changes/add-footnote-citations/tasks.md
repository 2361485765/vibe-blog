# Tasks: Add Footnote Citations

## Task 1: Implement footnote collection and numbering in Assembler

**File**: `backend/services/blog_generator/agents/assembler.py`

- 新增 `build_footnote_map(sections, search_results)` 方法：遍历所有 section 内容，扫描 `{source_NNN}` 占位符，基于 URL 去重，按首次出现顺序分配全文统一编号，返回 `footnote_map` (url→number) 和 `footnote_list` (有序脚注条目)
- 修改 `replace_source_references` 方法：接受 `footnote_map` 参数，将 `{source_NNN}` 替换为 `<sup>[[N]](#ref-N)</sup>` 而非内联链接
- 修改 `assemble` 方法：先调用 `build_footnote_map` 全局收集，再在每个 section 中替换，最后将 `footnote_list` 传入 footer 渲染
- **验证**：单元测试覆盖单次引用、重复引用、URL 去重、索引越界、空搜索结果等场景

**依赖**：无（可最先开始）

## Task 2: Restructure footer template for footnote list

**File**: `backend/infrastructure/prompts/blog/assembler_footer.j2`

- 新增"参考文献"区块：渲染编号脚注列表，每项带 `<a id="ref-N"></a>` 锚点
- 将原"网络来源"改为"延伸阅读"：仅展示未被正文引用的 `reference_links`
- 保留"文档来源"区块不变
- 更新 `render_assembler_footer` 调用签名，增加 `cited_footnotes` 和 `uncited_references` 参数
- **验证**：渲染产物包含正确的锚点 ID 和编号，延伸阅读不含已引用来源

**依赖**：Task 1（需要 footnote_list 数据）

## Task 3: Update Writer prompt citation guidance

**File**: `backend/infrastructure/prompts/blog/writer.j2`

- 修改 `{source_NNN}` 使用说明：解释占位符将被渲染为编号脚注 `[N]`，不会打断阅读流
- 增加指导：鼓励在具体事实、数据、引用语句处精准标注，而非段落末尾泛泛标注
- 增加示例：展示脚注最终渲染效果
- **验证**：人工审查 prompt 内容，确认指导清晰无歧义

**依赖**：无（可与 Task 1 并行）

## Task 4: Adapt frontend citationMatcher for footnote anchors

**File**: `frontend/src/utils/citationMatcher.ts`

- 扩展 `scanCitationLinks`：除了匹配 `href` 为外部 URL 的 `<a>` 标签，额外识别 `href="#ref-N"` 模式的脚注锚点链接
- 对脚注链接，通过编号 N 从 `citations` 列表按索引（N-1）匹配，而非 URL 匹配
- 保持旧格式（外部 URL 链接）的匹配逻辑不变，实现向后兼容
- **验证**：单元测试覆盖新旧两种格式的混合场景

**依赖**：无（可与 Task 1 并行）

## Task 5: Update Generate.vue footnote interaction

**File**: `frontend/src/views/Generate.vue`

- 确保 `showTooltip` 对脚注标记（`<sup>` 内的 `<a>`）正确定位 tooltip
- 确保点击脚注标记触发页面滚动到文末对应锚点
- 测试移动端降级（当前 CitationTooltip 在移动端已隐藏）
- **验证**：端到端测试，生成一篇新文章并验证脚注 hover 和点击行为

**依赖**：Task 1, Task 2, Task 4

## Task 6: Update Assembler prompt manager interface

**File**: `backend/services/blog_generator/prompts/` (prompt manager)

- 更新 `render_assembler_footer` 方法签名，传入 `cited_footnotes` 列表和 `uncited_references` 列表
- 确保模板上下文变量正确传递
- **验证**：单元测试验证模板渲染输出

**依赖**：Task 1, Task 2

## Task 7: Update existing tests

**Files**: `backend/tests/test_57_skeleton_design.py` 及其他相关测试

- 更新 `test_57_skeleton_design.py` 中检查 `{source_NNN}` 未替换的断言（新格式为 `<sup>` 标记）
- 新增 Assembler 脚注替换的单元测试
- 新增 footer 模板渲染的单元测试
- **验证**：全部测试通过

**依赖**：Task 1, Task 2

## Parallelizable Work

- Task 1, Task 3, Task 4 可并行开发（无依赖关系）
- Task 2 和 Task 6 在 Task 1 完成后可并行
- Task 5 和 Task 7 需等核心逻辑完成后进行集成测试
