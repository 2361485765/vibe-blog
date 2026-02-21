"""
AionUi 迁移特性 E2E 验证脚本 v3
使用 Vite dev server 的 ESM dynamic import 验证模块是否可用
"""
import sys
import os
from playwright.sync_api import sync_playwright

FRONTEND = "http://localhost:5173"
SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), "..", "backend", "outputs", "e2e_screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

results = []
console_errors = []


def record(name, passed, detail=""):
    status = "PASS" if passed else "FAIL"
    results.append((name, status, detail))
    print(f"  [{status}] {name}" + (f" — {detail}" if detail else ""))


def shot(page, name):
    path = os.path.join(SCREENSHOT_DIR, f"aionui_{name}.png")
    page.screenshot(path=path, full_page=True)
    return path


def try_import(page, module_path):
    """通过 Vite ESM dynamic import 检查模块是否存在且可导入"""
    result = page.evaluate(f"""async () => {{
        try {{
            const mod = await import('{module_path}');
            return {{ ok: true, exports: Object.keys(mod) }};
        }} catch(e) {{
            return {{ ok: false, error: e.message }};
        }}
    }}""")
    return result


# ─── 115.02 KaTeX 数学公式渲染 ───
def verify_katex(page):
    print("\n=== 115.02 KaTeX 数学公式渲染 ===")
    page.goto(FRONTEND)
    page.wait_for_load_state("networkidle")

    # 1. KaTeX CSS 已加载
    katex_css = page.evaluate("""() => {
        const sheets = Array.from(document.styleSheets);
        for (const s of sheets) {
            try {
                if (s.href && s.href.includes('katex')) return 'link';
                const rules = Array.from(s.cssRules || []);
                if (rules.some(r => r.cssText && r.cssText.includes('.katex'))) return 'inline';
            } catch {}
        }
        return '';
    }""")
    record("KaTeX CSS 已加载", katex_css != "", f"方式={katex_css or 'none'}")

    # 2. useMarkdownRenderer 导出 renderMarkdown
    md = try_import(page, "/src/composables/useMarkdownRenderer.ts")
    record("useMarkdownRenderer 可导入", md["ok"],
           f"exports={md.get('exports', md.get('error', ''))}")

    # 3. 实际渲染 KaTeX 公式
    if md["ok"]:
        rendered = page.evaluate("""async () => {
            const { useMarkdownRenderer } = await import('/src/composables/useMarkdownRenderer.ts');
            const { renderMarkdown } = useMarkdownRenderer();
            const html = renderMarkdown('行内公式 $E=mc^2$ 和块级公式:\\n$$\\\\int_0^1 x^2 dx$$');
            return {
                hasKatex: html.includes('katex'),
                hasInline: html.includes('katex-mathml') || html.includes('katex'),
                snippet: html.substring(0, 200)
            };
        }""")
        record("KaTeX 公式渲染成功", rendered.get("hasKatex", False),
               f"包含katex标记={rendered.get('hasKatex')}")
    shot(page, "01_katex")


# ─── 115.01a 智能自动滚动 ───
def verify_smart_scroll(page):
    print("\n=== 115.01a 智能自动滚动 ===")

    # 1. useSmartAutoScroll composable 可导入
    mod = try_import(page, "/src/composables/useSmartAutoScroll.ts")
    record("useSmartAutoScroll 可导入", mod["ok"],
           f"exports={mod.get('exports', mod.get('error', ''))}")

    # 2. ProgressDrawer 组件可导入
    drawer = try_import(page, "/src/components/home/ProgressDrawer.vue")
    record("ProgressDrawer 组件可导入", drawer["ok"],
           f"exports={drawer.get('exports', drawer.get('error', ''))}")
    shot(page, "02_scroll")


# ─── 115.03 拖拽上传 + 粘贴 ───
def verify_drag_upload(page):
    print("\n=== 115.03 拖拽上传 + 粘贴 ===")
    page.goto(FRONTEND)
    page.wait_for_load_state("networkidle")

    # 1. BlogInputCard 存在
    card = page.locator(".code-input-card")
    record("BlogInputCard 存在", card.count() > 0)

    # 2. useDragUpload composable
    drag = try_import(page, "/src/composables/useDragUpload.ts")
    record("useDragUpload 可导入", drag["ok"],
           f"exports={drag.get('exports', drag.get('error', ''))}")

    # 3. usePasteService composable
    paste = try_import(page, "/src/composables/usePasteService.ts")
    record("usePasteService 可导入", paste["ok"],
           f"exports={paste.get('exports', paste.get('error', ''))}")

    # 4. 模拟拖拽触发 overlay
    page.evaluate("""() => {
        const card = document.querySelector('.code-input-card');
        if (!card) return;
        const dt = new DataTransfer();
        dt.items.add(new File(['test'], 'test.pdf', { type: 'application/pdf' }));
        card.dispatchEvent(new DragEvent('dragenter', { bubbles: true, dataTransfer: dt }));
    }""")
    page.wait_for_timeout(500)
    overlay = page.locator(".drag-overlay")
    record("拖拽 overlay 已触发", overlay.count() > 0)

    if overlay.count() > 0:
        has_parts = (page.locator(".drag-icon").count() > 0 and
                     page.locator(".drag-text").count() > 0)
        record("overlay 包含图标+文字", has_parts)
    shot(page, "03_drag")


# ─── 115.01b Token 可视化圆环 ───
def verify_token_ring(page):
    print("\n=== 115.01b Token 可视化圆环 ===")

    # 1. TokenUsageRing 组件可导入
    ring = try_import(page, "/src/components/home/TokenUsageRing.vue")
    record("TokenUsageRing 组件可导入", ring["ok"],
           f"exports={ring.get('exports', ring.get('error', ''))}")

    # 2. Token 类型定义可导入
    types = try_import(page, "/src/types/token.ts")
    record("Token 类型定义可导入", types["ok"],
           f"exports={types.get('exports', types.get('error', ''))}")
    shot(page, "04_token")


# ─── 115.05 打字动画 + 分割面板 + 字体控制 ───
def verify_typing_split_font(page):
    print("\n=== 115.05 打字动画 + 分割面板 + 字体控制 ===")
    page.goto(FRONTEND)
    page.wait_for_load_state("networkidle")

    # 1. CSS 变量
    font_scale = page.evaluate("""() =>
        getComputedStyle(document.documentElement).getPropertyValue('--font-scale').trim()
    """)
    record("--font-scale CSS 变量", font_scale != "", f"值={font_scale or '(空)'}")

    scaled = page.evaluate("""() =>
        getComputedStyle(document.documentElement).getPropertyValue('--font-size-base-scaled').trim()
    """)
    record("--font-size-base-scaled 变量", scaled != "", f"值={scaled or '(空)'}")

    # 2. useTypingAnimation
    typing = try_import(page, "/src/composables/useTypingAnimation.ts")
    record("useTypingAnimation 可导入", typing["ok"],
           f"exports={typing.get('exports', typing.get('error', ''))}")

    # 3. useResizableSplit
    split = try_import(page, "/src/composables/useResizableSplit.ts")
    record("useResizableSplit 可导入", split["ok"],
           f"exports={split.get('exports', split.get('error', ''))}")

    # 4. useFontScale
    font = try_import(page, "/src/composables/useFontScale.ts")
    record("useFontScale 可导入", font["ok"],
           f"exports={font.get('exports', font.get('error', ''))}")

    # 5. FontSizeControl 组件
    ctrl = try_import(page, "/src/components/ui/FontSizeControl.vue")
    record("FontSizeControl 组件可导入", ctrl["ok"],
           f"exports={ctrl.get('exports', ctrl.get('error', ''))}")
    shot(page, "05_font")


# ─── 115.04 Cron 任务管理 UI ───
def verify_cron_ui(page):
    print("\n=== 115.04 Cron 任务管理 UI ===")
    page.goto(f"{FRONTEND}/cron")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(2000)

    # 1. CronManager 页面容器
    record("CronManager 页面已加载", page.locator(".cron-manager").count() > 0)

    # 2. 统计芯片
    chips = page.locator(".stat-chip")
    record("统计芯片", chips.count() > 0, f"数量={chips.count()}")

    # 3. 页面标题
    title = page.locator(".page-title")
    if title.count() > 0:
        record("页面标题 '$ crontab'", True, f"内容={title.inner_text().strip()}")
    else:
        record("页面标题", False)

    # 4. 新建按钮
    record("新建任务按钮", page.locator(".btn-new").count() > 0)

    # 5. 空状态或任务列表
    empty = page.locator(".empty-state").count() > 0
    jobs = page.locator(".job-list").count() > 0
    record("内容区域", empty or jobs, f"{'空状态' if empty else '有任务' if jobs else '未知'}")

    shot(page, "06_cron_page")

    # 6. 点击新建 → Drawer 弹出
    btn = page.locator(".btn-new").first
    if btn:
        btn.click()
        page.wait_for_timeout(500)
        drawer = page.locator(".cron-drawer-overlay, .drawer-mask, [class*='drawer']")
        record("新建任务 Drawer 弹出", drawer.count() > 0)
        shot(page, "06_cron_drawer")

    # 7. CronManager 组件可导入
    cron = try_import(page, "/src/views/CronManager.vue")
    record("CronManager 组件可导入", cron["ok"])

    # 8. useCronJobs composable
    cron_jobs = try_import(page, "/src/composables/useCronJobs.ts")
    record("useCronJobs 可导入", cron_jobs["ok"],
           f"exports={cron_jobs.get('exports', cron_jobs.get('error', ''))}")


# ─── 主函数 ───
def main():
    print("=" * 60)
    print("AionUi 迁移特性 E2E 验证 v3")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={"width": 1280, "height": 900})
        page = ctx.new_page()
        page.on("console", lambda m: console_errors.append(m.text) if m.type == "error" else None)

        try:
            verify_katex(page)
            verify_smart_scroll(page)
            verify_drag_upload(page)
            verify_token_ring(page)
            verify_typing_split_font(page)
            verify_cron_ui(page)
        except Exception as e:
            print(f"\n!!! 异常: {e}")
            shot(page, "error")
            raise
        finally:
            browser.close()

    # 汇总
    print("\n" + "=" * 60)
    print("验证结果汇总")
    print("=" * 60)
    passed = sum(1 for _, s, _ in results if s == "PASS")
    failed = sum(1 for _, s, _ in results if s == "FAIL")
    for name, status, detail in results:
        icon = "✅" if status == "PASS" else "❌"
        print(f"  {icon} {name}" + (f" — {detail}" if detail else ""))
    print(f"\n总计: {passed} 通过, {failed} 失败, 共 {len(results)} 项")

    if console_errors:
        print(f"\n⚠️  控制台错误 ({len(console_errors)}):")
        for e in console_errors[:5]:
            print(f"  - {e[:200]}")

    print(f"\n截图: {SCREENSHOT_DIR}")
    sys.exit(1 if failed > 0 else 0)


if __name__ == "__main__":
    main()
