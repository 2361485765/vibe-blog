# Tasks: Refine Footnote Citations

## Task 1: Parse citations data in useBlogDetail

**File**: `frontend/src/composables/useBlogDetail.ts`

- 在 `Blog` interface 中新增 `citations: Citation[]` 字段
- 在 API 响应映射逻辑中解析 `record.citations`（JSON 字符串 → `Citation[]`），null 时默认空数组
- 导入 `Citation` 类型从 `@/utils/citationMatcher`
- **验证**：打开一篇有 citations 的文章，在 Vue DevTools 中确认 `blog.citations` 有数据

**依赖**：无

## Task 2: Add CitationTooltip to BlogDetail page

**File**: `frontend/src/views/BlogDetail.vue`（或 `BlogDetailContent.vue`）

- 导入 `CitationTooltip` 组件和 `scanCitationLinks` 函数
- 添加 `CitationTooltip` 到模板（与 `Generate.vue` 一致）
- 获取文章内容容器 ref 和 `citations` 数据
- 在文章渲染后（`nextTick`/`watch`）调用 `scanCitationLinks` 绑定 hover 和 click 事件
- hover 显示 tooltip，click 滚动到文末锚点
- **验证**：打开文章，悬停脚注 `[1]` 看到来源卡片；点击 `[1]` 页面滚动到参考列表

**依赖**：Task 1

## Task 3: Merge cited footnotes into reference_links in Assembler

**File**: `backend/services/blog_generator/agents/assembler.py`

- 修改 `assemble()` 方法：将 `cited_footnotes` 列表转换为 `reference_links` 格式的 dict，附带 `ref_id` 字段
- 已引用来源排在前面（按脚注编号），未引用来源追加在后面
- URL 去重：已引用来源优先，去掉 `uncited_references` 中重复的 URL
- 统一传入 footer 模板，不再传 `cited_footnotes` 参数
- **验证**：生成文章后检查 footer 输出，确认只有一个统一的来源列表

**依赖**：无

## Task 4: Restructure footer template to remove "参考文献"

**File**: `backend/infrastructure/prompts/blog/assembler_footer.j2`

- 删除 `## 参考文献` 区块及相关 `cited_footnotes` 循环
- 修改"网络来源"列表：已引用条目前附加 `<a id="ref-N"></a>` 锚点（通过 `ref_id` 字段判断）
- 保留"文档来源"区块不变
- **验证**：生成文章后，文末只有"参考资料 > 网络来源"，正文脚注点击能跳转到对应条目

**依赖**：Task 3

## Task 5: Update prompt manager interface

**File**: `backend/infrastructure/prompts/prompt_manager.py`

- 从 `render_assembler_footer` 方法签名中移除 `cited_footnotes` 参数（不再需要）
- **验证**：无报错，生成文章正常

**依赖**：Task 3, Task 4

## Task 6: Update unit tests

**File**: `backend/tests/test_assembler_footnotes.py`

- 更新 Assembler 测试：验证合并后的 reference_links 顺序和去重
- 新增测试：验证 footer 渲染不包含"参考文献"标题
- **验证**：全部测试通过

**依赖**：Task 3, Task 4

## Parallelizable Work

- Task 1 + Task 2（前端）和 Task 3 + Task 4 + Task 5（后端）可并行开发
- Task 6 在 Task 3/4 完成后进行
