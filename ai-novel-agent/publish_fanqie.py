"""番茄小说新建章节 - 自动发布脚本

通过 Playwright + CDP 连接已打开的 Edge 浏览器，
自动完成：新建章节 → 填写标题 → 粘贴正文 → 确认发布 → 验证

使用方式：
1. 先启动 Edge: msedge --remote-debugging-port=9222
2. 登录番茄小说作家后台
3. 运行: python publish_fanqie.py
"""
import sys
import os
import time

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from playwright.sync_api import sync_playwright

NOVEL_DIR = r"path/to/novel/workspace"  # 替换为实际路径
CHAPTER_MANAGE_URL = "https://fanqienovel.com/main/writer/chapter-manage/YOUR_BOOK_ID"

# (标题, md文件名)
CHAPTERS = [
    ("第一百八十二章：树枝的声音", "chapters/182-树枝的声音.md"),
    ("第一百八十三章：旁观者的看法", "chapters/183-旁观者的看法.md"),
    # ... 添加更多章节
]

# True=只跑第1章(测试), False=全部
TEST_MODE = False


def read_chapter(filename):
    """读取章节md文件，去掉标题行"""
    filepath = os.path.join(NOVEL_DIR, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    lines = content.strip().split('\n')
    if lines and lines[0].startswith('#'):
        lines = lines[1:]
    return '\n'.join(lines).strip()


def main():
    chapters = CHAPTERS if not TEST_MODE else CHAPTERS[:1]
    print(f"共 {len(chapters)} 章待发布 ({'测试模式' if TEST_MODE else '正式模式'})")

    print("连接 Edge CDP :9222...")
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://localhost:9222")
        ctx = browser.contexts[0]

        # 清理多余tab
        while len(ctx.pages) > 1:
            ctx.pages[-1].close()
        manage = ctx.pages[0]

        success = 0

        for i, chapter_info in enumerate(chapters):
            title, filename = chapter_info
            print(f"\n{'='*50}")
            print(f"[{i+1}/{len(chapters)}] {title}")
            print(f"{'='*50}")

            content = read_chapter(filename)
            print(f"  字数: {len(content)}")

            # 清理多余tab
            while len(ctx.pages) > 1:
                ctx.pages[-1].close()
            manage = ctx.pages[0]

            # 1. 新建章节
            manage.goto(CHAPTER_MANAGE_URL, wait_until='domcontentloaded', timeout=30000)
            time.sleep(3)
            try:
                with manage.expect_popup(timeout=10000) as pop:
                    manage.locator('button:has-text("新建章节")').first.click()
                editor = pop.value
                print("  [1] 新建 OK")
                time.sleep(4)
            except Exception as e:
                print(f"  [1] 失败: {e}")
                continue

            # 2. 填写标题
            try:
                editor.locator('textarea.serial-textarea').first.wait_for(state='visible', timeout=10000)
                editor.locator('textarea.serial-textarea').first.fill(title)
                print("  [2] 标题 OK")
            except Exception as e:
                print(f"  [2] 失败: {e}")
                continue

            # 3. 正文 - JS直接写入ProseMirror编辑器
            try:
                body = editor.locator('.serial-editor-content .ProseMirror').first
                body.wait_for(state='visible', timeout=10000)
                body.click()
                time.sleep(0.5)
                # 将md内容转为HTML段落，直接注入编辑器
                paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
                html_parts = []
                for p in paragraphs:
                    lines = p.split('\n')
                    html_p = '<p>' + '</p><p>'.join(lines) + '</p>'
                    html_parts.append(html_p)
                full_html = ''.join(html_parts)
                editor.evaluate(f'''(html) => {{
                    const editor = document.querySelector(".ProseMirror");
                    if (!editor) return;
                    editor.innerHTML = html;
                    editor.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    editor.dispatchEvent(new Event('change', {{ bubbles: true }}));
                }}''', full_html)
                result = editor.evaluate('() => { const e = document.querySelector(".ProseMirror"); return e ? e.innerText.length : 0; }')
                print(f"  [3] 正文 OK (JS直接赋值, 字数={result})")
                time.sleep(3)
                # 等待自动保存
                try:
                    editor.locator('text=已保存到云端').wait_for(state='visible', timeout=10000)
                    print("  [3b] 自动保存完成")
                except:
                    print("  [3b] 未检测到保存提示（继续）")
                time.sleep(2)
            except Exception as e:
                print(f"  [3] 失败: {e}")
                continue

            # 4. 下一步
            try:
                editor.locator('button:has-text("下一步")').first.click()
                print("  [4] 下一步")
                time.sleep(5)
            except Exception as e:
                print(f"  [4] 失败: {e}")
                continue

            # 5. 弹窗链处理（确认发布/AI声明/风险检测等）
            published = False
            for step in range(15):
                btns = []
                for btn in editor.locator('button:visible').all():
                    try:
                        t = btn.inner_text(timeout=1000).strip()
                        if t:
                            btns.append(t)
                    except:
                        pass

                if "确认发布" in btns and "取消" in btns:
                    print("      发布设置弹窗已打开")
                    time.sleep(3)
                    # AI声明 - 选"是"
                    try:
                        ai_label = editor.locator('.arco-modal label.arco-radio').first
                        ai_label.wait_for(state='visible', timeout=5000)
                        ai_label.click()
                        print("      AI: 是")
                        time.sleep(2)
                    except Exception as e:
                        print(f"      AI失败: {e}")
                    # 确认发布
                    try:
                        pub = editor.locator('.arco-modal-footer button:has-text("确认发布")').first
                        pub.wait_for(state='visible', timeout=5000)
                        pub.scroll_into_view_if_needed()
                        time.sleep(2)
                        pub.click()
                        print("      确认发布 clicked!")
                        time.sleep(5)
                    except Exception as e:
                        print(f"      确认发布失败: {e}")
                        break
                    # 等待跳转到目录页
                    for w in range(30):
                        time.sleep(1)
                        try:
                            if "chapter-manage" in editor.url:
                                print(f"      跳转目录成功 ({w+1}s)")
                                published = True
                                break
                        except:
                            published = True
                            break
                    break
                elif "提交" in btns:
                    editor.locator('button:has-text("提交")').first.click()
                    time.sleep(5)
                elif "确定" in btns:
                    editor.locator('button:has-text("确定")').first.click()
                    time.sleep(5)
                else:
                    time.sleep(1)

            # 6. 验证
            print("  [6] 验证...")
            try:
                manage.goto(CHAPTER_MANAGE_URL, wait_until='domcontentloaded', timeout=30000)
                time.sleep(3)
                text = manage.inner_text('body')
                if title in text:
                    print(f"  OK! {title} 已发布")
                    success += 1
                else:
                    print(f"  重试验证...")
                    time.sleep(5)
                    manage.reload(wait_until='domcontentloaded', timeout=30000)
                    time.sleep(3)
                    text2 = manage.inner_text('body')
                    if title in text2:
                        print(f"  OK! {title} 已发布（刷新后找到）")
                        success += 1
                    else:
                        print(f"  X {title} 未在目录找到 -> 停止")
                        break
            except Exception as e:
                print(f"  X 验证异常: {e} -> 停止")
                break

        print(f"\n{'='*50}")
        print(f"完成: {success}/{len(chapters)} 章")


if __name__ == "__main__":
    main()
