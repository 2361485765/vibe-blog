"""
Step 1.1 叙事流 Playwright E2E 验证

通过 Playwright 浏览器：
1. 打开前端页面
2. 输入主题，点击生成
3. 监听 SSE 流中的 outline_complete 事件
4. 验证 narrative_mode / narrative_flow / narrative_role 字段

用法：
    cd backend && python tests/test_narrative_e2e.py --headed
    cd backend && python tests/test_narrative_e2e.py  # 无头模式
"""

import sys
import os
import json
import time
import argparse
import logging
import requests

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

BACKEND_URL = "http://localhost:5001"
FRONTEND_URL = "http://localhost:5173"

VALID_MODES = ["what-why-how", "problem-solution", "before-after", "tutorial", "deep-dive", "catalog"]
VALID_ROLES = ["hook", "what", "why", "how", "compare", "deep_dive", "verify", "summary", "catalog_item"]

TEST_CASES = [
    {
        "topic": "什么是 RAG",
        "article_type": "tutorial",
        "expected_modes": ["what-why-how", "tutorial"],
        "target_length": "mini",
    },
    {
        "topic": "手把手搭建 RAG 系统",
        "article_type": "tutorial",
        "expected_modes": ["tutorial"],
        "target_length": "mini",
    },
    {
        "topic": "10 个 RAG 性能优化技巧",
        "article_type": "tutorial",
        "expected_modes": ["catalog"],
        "target_length": "mini",
    },
]


def validate_outline_from_sse(data: dict, expected_modes: list) -> list:
    """验证 SSE outline_complete 事件中的叙事字段"""
    results = []

    # A1: narrative_mode
    mode = data.get("narrative_mode", "")
    if not mode:
        results.append(("FAIL", "缺少 narrative_mode"))
    elif mode not in VALID_MODES:
        results.append(("WARN", f"narrative_mode 值不在预期范围: {mode}"))
    else:
        results.append(("PASS", f"narrative_mode = {mode}"))

    # A2: 模式匹配
    if mode in expected_modes:
        results.append(("PASS", f"模式匹配预期 {expected_modes}"))
    else:
        results.append(("WARN", f"模式不匹配: 实际={mode}, 期望={expected_modes}"))

    # A3: narrative_flow
    flow = data.get("narrative_flow", {})
    if not flow:
        results.append(("FAIL", "缺少 narrative_flow"))
    else:
        if flow.get("reader_start"):
            results.append(("PASS", f"reader_start 有值"))
        else:
            results.append(("FAIL", "缺少 narrative_flow.reader_start"))

        if flow.get("reader_end"):
            results.append(("PASS", f"reader_end 有值"))
        else:
            results.append(("FAIL", "缺少 narrative_flow.reader_end"))

        chain = flow.get("logic_chain", [])
        if len(chain) >= 3:
            results.append(("PASS", f"logic_chain = {len(chain)} 个节点"))
        else:
            results.append(("FAIL", f"logic_chain 不足 3 个节点: {len(chain)}"))

    # A4: sections_narrative_roles
    roles = data.get("sections_narrative_roles", [])
    if not roles:
        results.append(("FAIL", "缺少 sections_narrative_roles"))
    else:
        missing = sum(1 for r in roles if not r)
        if missing == 0:
            results.append(("PASS", f"所有 {len(roles)} 个 section 都有 narrative_role: {roles}"))
        else:
            results.append(("WARN", f"{missing}/{len(roles)} 个 section 缺少 narrative_role"))

    return results


def run_api_e2e(case: dict, case_idx: int) -> bool:
    """通过后端 API + SSE 流进行 E2E 验证"""
    topic = case["topic"]
    logger.info(f"\n{'='*60}")
    logger.info(f"测试 {case_idx}: {topic}")
    logger.info(f"期望模式: {case['expected_modes']}")
    logger.info(f"{'='*60}")

    # 1. 调用异步生成 API
    try:
        resp = requests.post(f"{BACKEND_URL}/api/blog/generate", json={
            "topic": topic,
            "article_type": case["article_type"],
            "target_length": case["target_length"],
            "target_audience": "intermediate",
            "image_style": "",  # 不生成图片
        }, timeout=60)
        resp.raise_for_status()
        result = resp.json()
        task_id = result.get("task_id")
        if not task_id:
            logger.error(f"  ❌ 未获取到 task_id: {result}")
            return False
        logger.info(f"  📡 task_id: {task_id}")
    except Exception as e:
        logger.error(f"  ❌ API 调用失败: {e}")
        return False

    # 2. 监听 SSE 流，等待 outline_complete 事件
    logger.info(f"  ⏳ 监听 SSE 流等待大纲生成...")
    outline_data = None
    try:
        sse_resp = requests.get(
            f"{BACKEND_URL}/api/tasks/{task_id}/stream",
            stream=True, timeout=300
        )
        client = sseclient.SSEClient(sse_resp)

        for event in client.events():
            if event.event == "result":
                data = json.loads(event.data)
                if data.get("type") == "outline_complete":
                    outline_data = data.get("data", {})
                    logger.info(f"  🎉 收到 outline_complete 事件")
                    logger.info(f"     标题: {outline_data.get('title', '')}")
                    logger.info(f"     章节数: {outline_data.get('sections_count', 0)}")
                    break
            elif event.event == "error":
                data = json.loads(event.data)
                logger.error(f"  ❌ SSE 错误: {data.get('message', '')}")
                return False
            elif event.event in ("complete", "cancelled"):
                break

    except Exception as e:
        logger.error(f"  ❌ SSE 监听失败: {e}")
        return False

    if not outline_data:
        logger.error(f"  ❌ 未收到 outline_complete 事件")
        return False

    # 3. 验证字段
    results = validate_outline_from_sse(outline_data, case["expected_modes"])
    all_pass = True
    logger.info(f"\n  --- 验证结果 ---")
    for status, msg in results:
        icon = {"PASS": "✅", "FAIL": "❌", "WARN": "⚠️"}[status]
        logger.info(f"    {icon} {msg}")
        if status == "FAIL":
            all_pass = False

    # 4. 取消任务（不需要等后续写作）
    try:
        requests.post(f"{BACKEND_URL}/api/tasks/{task_id}/cancel", timeout=5)
        logger.info(f"  🛑 已取消任务 {task_id}（只需验证大纲）")
    except Exception:
        pass

    return all_pass


# JS 代码：注入到浏览器中，hook EventSource 拦截 SSE 事件
SSE_HOOK_JS = """
(() => {
    window.__sse_outline_data = null;
    window.__sse_events = [];
    const OrigES = window.EventSource;
    window.EventSource = function(url, opts) {
        const es = new OrigES(url, opts);
        const origAddEventListener = es.addEventListener.bind(es);
        es.addEventListener = function(type, fn, ...rest) {
            const wrapped = function(evt) {
                try {
                    window.__sse_events.push({type: type, data: evt.data});
                    if (type === 'result') {
                        const d = JSON.parse(evt.data);
                        if (d.type === 'outline_complete') {
                            window.__sse_outline_data = d.data;
                        }
                    }
                } catch(e) {}
                return fn.call(this, evt);
            };
            return origAddEventListener(type, wrapped, ...rest);
        };
        // Also hook onmessage
        const origOnMsg = Object.getOwnPropertyDescriptor(OrigES.prototype, 'onmessage');
        return es;
    };
    window.EventSource.CONNECTING = OrigES.CONNECTING;
    window.EventSource.OPEN = OrigES.OPEN;
    window.EventSource.CLOSED = OrigES.CLOSED;
})();
"""


def run_playwright_e2e(case: dict, case_idx: int, headed: bool) -> bool:
    """通过 Playwright 浏览器进行 E2E 验证"""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        logger.warning("Playwright 未安装，回退到 API E2E 模式")
        return run_api_e2e(case, case_idx)

    topic = case["topic"]
    logger.info(f"\n{'='*60}")
    logger.info(f"🌐 Playwright E2E 测试 {case_idx}: {topic}")
    logger.info(f"期望模式: {case['expected_modes']}")
    logger.info(f"{'='*60}")

    outline_data = None
    captured_task_id = None

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not headed, slow_mo=200)
        context = browser.new_context(viewport={'width': 1440, 'height': 900})
        page = context.new_page()
        page.set_default_timeout(300000)

        try:
            # Step 1: 打开首页并注入 SSE Hook
            logger.info("  📌 Step 1: 打开首页")
            # 在页面加载前注入 JS hook
            page.add_init_script(SSE_HOOK_JS)
            page.goto(FRONTEND_URL, wait_until='domcontentloaded')
            page.wait_for_timeout(3000)
            logger.info(f"    ✅ 首页加载成功: {page.title()}")
            page.screenshot(path=f'/tmp/e2e_case{case_idx}_step1.png')

            # Step 2: 输入主题
            logger.info(f"  📌 Step 2: 输入主题: {topic}")
            input_selectors = [
                'textarea[placeholder*="输入"]', 'textarea[placeholder*="主题"]',
                'textarea[placeholder*="想写"]', 'textarea',
            ]
            input_found = False
            for selector in input_selectors:
                try:
                    el = page.locator(selector).first
                    if el.is_visible(timeout=3000):
                        el.click()
                        el.fill(topic)
                        logger.info(f"    ✅ 已输入主题 (selector: {selector})")
                        input_found = True
                        break
                except Exception:
                    continue
            if not input_found:
                logger.error("    ❌ 未找到输入框")
                page.screenshot(path=f'/tmp/e2e_case{case_idx}_step2_fail.png')
                return False

            # Step 3: 点击生成
            logger.info(f"  📌 Step 3: 点击生成")
            gen_selectors = [
                '.code-generate-btn', 'button:has-text("execute")',
                'button:has-text("生成")', 'button:has-text("开始")',
                'button:has-text("Generate")', 'button[type="submit"]',
            ]
            gen_btn = None
            for selector in gen_selectors:
                try:
                    el = page.locator(selector).first
                    if el.is_visible(timeout=3000) and el.is_enabled(timeout=1000):
                        gen_btn = el
                        logger.info(f"    找到生成按钮: {selector}")
                        break
                except Exception:
                    continue
            if not gen_btn:
                logger.error("    ❌ 未找到生成按钮")
                page.screenshot(path=f'/tmp/e2e_case{case_idx}_step3_fail.png')
                return False

            with page.expect_response(
                lambda resp: 'generate' in resp.url and resp.status < 400,
                timeout=60000
            ) as response_info:
                gen_btn.click()
                logger.info(f"    ✅ 已点击生成按钮")

            api_response = response_info.value
            logger.info(f"    🔗 API响应: {api_response.status} {api_response.url}")
            try:
                body = api_response.json()
                captured_task_id = body.get('task_id', '')
            except Exception as e:
                logger.error(f"    ❌ 解析API响应失败: {e}")
                return False

            if not captured_task_id:
                logger.error(f"    ❌ 响应中无 task_id: {body}")
                return False
            logger.info(f"    📡 task_id: {captured_task_id}")
            page.screenshot(path=f'/tmp/e2e_case{case_idx}_step3.png')

            # Step 4: 轮询浏览器中的 SSE hook 数据，等待 outline_complete
            logger.info(f"  📌 Step 4: 等待大纲生成（通过浏览器内 SSE hook）...")
            max_wait = 300  # 最多等 5 分钟
            poll_interval = 3  # 每 3 秒检查一次
            waited = 0
            while waited < max_wait:
                result = page.evaluate('() => window.__sse_outline_data')
                if result:
                    outline_data = result
                    logger.info(f"    🎉 收到 outline_complete")
                    logger.info(f"       标题: {outline_data.get('title', '')}")
                    logger.info(f"       章节数: {outline_data.get('sections_count', 0)}")
                    break
                page.wait_for_timeout(poll_interval * 1000)
                waited += poll_interval
                if waited % 30 == 0:
                    event_count = page.evaluate('() => window.__sse_events.length')
                    logger.info(f"    ⏳ 已等待 {waited}s，收到 {event_count} 个 SSE 事件")

            page.screenshot(path=f'/tmp/e2e_case{case_idx}_step4.png')

            # 取消任务
            if captured_task_id:
                try:
                    requests.post(f"{BACKEND_URL}/api/tasks/{captured_task_id}/cancel", timeout=5)
                    logger.info(f"  🛑 已取消任务（只需验证大纲）")
                except Exception:
                    pass

        except Exception as e:
            logger.error(f"  ❌ Playwright 异常: {e}")
            return False
        finally:
            browser.close()

    if not outline_data:
        logger.error(f"  ❌ 未收到 outline_complete 事件")
        return False

    # 验证
    results = validate_outline_from_sse(outline_data, case["expected_modes"])
    all_pass = True
    logger.info(f"\n  --- 验证结果 ---")
    for status, msg in results:
        icon = {"PASS": "✅", "FAIL": "❌", "WARN": "⚠️"}[status]
        logger.info(f"    {icon} {msg}")
        if status == "FAIL":
            all_pass = False

    return all_pass


def main():
    parser = argparse.ArgumentParser(description="Step 1.1 叙事流 E2E 验证")
    parser.add_argument("--headed", action="store_true", help="Playwright 有头模式")
    parser.add_argument("--api-only", action="store_true", help="仅用 API 模式（不启动浏览器）")
    parser.add_argument("--cases", type=str, default="1,2,3", help="要运行的测试用例编号，逗号分隔")
    args = parser.parse_args()

    case_indices = [int(x) for x in args.cases.split(",")]
    passed = 0
    failed = 0

    for i, idx in enumerate(case_indices):
        if idx < 1 or idx > len(TEST_CASES):
            continue
        case = TEST_CASES[idx - 1]

        # 用例间等待，确保前一个任务完全清理
        if i > 0:
            logger.info(f"\n⏳ 等待 15 秒让后端清理前一个任务...")
            time.sleep(15)

        if args.api_only:
            ok = run_api_e2e(case, idx)
        else:
            ok = run_playwright_e2e(case, idx, args.headed)

        if ok:
            passed += 1
        else:
            failed += 1

    print(f"\n{'='*60}")
    print(f"📊 E2E 验证结果: {passed} 通过, {failed} 失败 (共 {passed+failed})")
    if failed == 0:
        print("🎉 所有测试通过！")
    else:
        print("⚠️ 部分测试未通过")
    print(f"{'='*60}")

    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
