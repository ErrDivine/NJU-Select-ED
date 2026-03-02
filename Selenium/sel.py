

from io import BytesIO
from PIL import Image, ImageTk
import tkinter as tk
import json, time, os
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#load json


def wait_for_manual_login_and_ctrl_g():
    """
    弹出一个提示窗口。请先在浏览器里手动登录（完成图片验证码等），
    登录完成后在此窗口按 Ctrl+G 继续；Esc 取消。
    """
    import tkinter as tk

    root = tk.Tk()
    root.title("登录完成后按 Ctrl+G 继续")
    root.geometry("+200+150")  # 可选：把窗口摆放到屏幕较不妨碍的位置

    msg = (
        "请在浏览器中手动完成登录（包括图片点选验证码）。\n\n"
        "完成后：请回到这个小窗口，按  Ctrl+G  继续选课。\n"
        "（Esc 取消）"
    )
    label = tk.Label(root, text=msg, justify="left", padx=12, pady=12)
    label.pack()

    def on_ctrl_g(event=None):
        print("[manual] 收到 Ctrl+G，准备继续选课流程 ...")
        root.quit()
        root.destroy()

    def on_esc(event=None):
        print("[manual] 取消继续（Esc）")
        root.quit()
        root.destroy()

    root.bind("<Control-g>", on_ctrl_g)  # ★ 必须在这个窗口里按 Ctrl+G
    root.bind("<Escape>", on_esc)
    root.mainloop()


def _collect_click_points(image_bytes: bytes,
                          save_json_path: str = "captcha_points.json",
                          max_points: int | None = None):
    """
    显示验证码截图，人工点击目标：
      - 左键：添加点（会在控制台打印坐标）
      - Backspace：撤销最后一个点
      - Ctrl+P：保存坐标到 save_json_path 并退出（MAC/Windows 通用）
      - Esc：取消并退出（不保存）
    返回：[(x,y), ...]  基于【图片像素坐标】(0,0) 为左上
    """
    img = Image.open(BytesIO(image_bytes))
    w, h = img.size

    root = tk.Tk()
    root.title("按提示点选验证码：左键添加点，Backspace撤销，Ctrl+P保存提交，Esc取消")
    canvas = tk.Canvas(root, width=w, height=h)
    canvas.pack()
    tk_img = ImageTk.PhotoImage(img)
    canvas.create_image(0, 0, anchor="nw", image=tk_img)

    points: list[tuple[int, int]] = []
    dots = []

    def on_click(event):
        nonlocal points
        if max_points is not None and len(points) >= max_points:
            return
        x, y = int(event.x), int(event.y)
        r = 4
        dot = canvas.create_oval(x-r, y-r, x+r, y+r, width=2)
        dots.append(dot)
        points.append((x, y))
        print(f"[captcha] click#{len(points)} at image px: ({x}, {y})")

    def on_key(event):
        # Backspace 撤销
        nonlocal points
        if event.keysym == "BackSpace" and points:
            points.pop()
            dot = dots.pop()
            canvas.delete(dot)
            print("[captcha] undo last point")
        elif event.keysym == "Escape":
            print("[captcha] canceled by Esc (no save)")
            root.quit()
            root.destroy()
        # 禁用回车提交（改为 Ctrl+P）
        elif event.keysym in ("Return", "KP_Enter"):
            pass

    def on_ctrl_p(event=None):
        # 保存坐标到 JSON 并退出
        payload = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "image_width": w,
            "image_height": h,
            "points": points,
        }
        try:
            with open(save_json_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
            print(f"[captcha] saved {len(points)} point(s) -> {os.path.abspath(save_json_path)}")
            print(f"[captcha] points: {points}")
        except Exception as e:
            print(f"[captcha] save failed: {e}")
        finally:
            root.quit()
            root.destroy()

    canvas.bind("<Button-1>", on_click)
    root.bind("<Key>", on_key)
    root.bind("<Control-g>", on_ctrl_p)
    # 如需 Command+P，把上一行改为： root.bind("<Command-p>", on_ctrl_p)

    root.mainloop()
    return points

def solve_captcha_with_human_click(driver,
                                   img_xpath: str,
                                   login_button_xpath: str,
                                   save_json_path: str = "captcha_points.json",
                                   max_points: int | None = None):
    """
    1) 截图验证码 <img> 元素
    2) 弹窗收集点击点（打印坐标，Ctrl+P 保存退出）
    3) 按等比缩放将图片像素坐标映射为 CSS 坐标，在页面回放点击
    4) 点击登录按钮
    """

    wait = WebDriverWait(driver, 20)
    img_el = wait.until(EC.visibility_of_element_located((By.XPATH, img_xpath)))

    # 元素 CSS 尺寸（页面中的显示尺寸）
    css_w = float(img_el.size["width"])
    css_h = float(img_el.size["height"])

    # 取元素截图（物理像素尺寸，可能是 Retina 倍数）
    png_bytes = img_el.screenshot_as_png
    from PIL import Image
    _tmp_img = Image.open(BytesIO(png_bytes))
    img_w, img_h = _tmp_img.size  # 图片像素尺寸

    # 计算缩放：图片像素 -> CSS 像素
    sx = css_w / img_w if img_w else 1.0
    sy = css_h / img_h if img_h else 1.0
    print(f"[captcha] element css size=({css_w:.1f}, {css_h:.1f}), screenshot px=({img_w}, {img_h}), scale=({sx:.3f}, {sy:.3f})")

    # 收集点击点（基于图片像素坐标）
    points = _collect_click_points(png_bytes, save_json_path=save_json_path, max_points=max_points)

    # 回放点击（把图片像素坐标按比例映射为 CSS 偏移）
    actions = ActionChains(driver)
    for i, (x, y) in enumerate(points, 1):
        dx = int(round(x * sx))
        dy = int(round(y * sy))
        print(f"[captcha] replay click#{i}: image ({x},{y}) -> css offset ({dx},{dy})")
        actions.move_to_element_with_offset(img_el, dx, dy).click()
    actions.perform()

    # 点击登录
    login_btn = wait.until(EC.element_to_be_clickable((By.XPATH, login_button_xpath)))
    login_btn.click()
    print("[captcha] login button clicked")










def run_course_selection()->bool:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.common.exceptions import WebDriverException
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from time import sleep

    def get_rows_first_link_texts(driver, rows_xpath, timeout=15):
        """
        Grab every <tr> matched by rows_xpath and return [{"idx", "text", "href"}].
        rows_xpath should end with .../tbody/tr (or ...//tr).
        """
        rows = WebDriverWait(driver, timeout).until(
            EC.presence_of_all_elements_located((By.XPATH, rows_xpath))
        )
        out = []
        for i, tr in enumerate(rows, start=1):
            try:
                a = tr.find_element(By.XPATH, "./td[1]/a")
                text = (a.text or "").strip()
                href = a.get_attribute("href") or ""
            except Exception:
                text, href = "", ""
            out.append(text)
        return out

    try:
        config = json.load(open("./config.json"))
        account = config["account"]
        password = config["password"]
        excluded = config["excluded"]
        chrome_options = Options()
        # 人工操作需要有头模式
        # chrome_options.add_argument("--headless")
        chrome_options = Options() # ★ 需要人工窗口，别用 headless # chrome_options.add_argument("--headless")#
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_experimental_option("detach", True)
        service = Service()
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get("https://xk.nju.edu.cn")
        wait = WebDriverWait(driver, 20)
        input_xpath = "/html/body/div[1]/article/section/div[3]/div[1]/div[1]/input"
        input_xpath2 = "/html/body/div[1]/article/section/div[3]/div[1]/div[2]/input"
        #img_xpath = "/html/body/div[1]/article/section/div[3]/div[1]/div[3]/img"
        login_btn = "/html/body/div[1]/article/section/div[3]/div[1]/button"
        wait.until(EC.visibility_of_element_located((By.XPATH, input_xpath))).send_keys(account)
        wait.until(EC.visibility_of_element_located((By.XPATH, input_xpath2))).send_keys(password)
        wait = WebDriverWait(driver, 30)
        # 提示：完全人工登录（包含图片验证码）。如需自动填账号/密码，可自行取消注释下方两行。
        # wait.until(EC.visibility_of_element_located((By.XPATH, "/html/body/div[1]/article/section/div[3]/div[1]/div[1]/input"))).send_keys(account)
        # wait.until(EC.visibility_of_element_located((By.XPATH, "/html/body/div[1]/article/section/div[3]/div[1]/div[2]/input"))).send_keys(password)

        print("请在浏览器中手动完成登录/验证码。完成后到弹出的小窗口按 Ctrl+G 继续。")
        wait_for_manual_login_and_ctrl_g()  # ★ 等你按 Ctrl+G

        # 按下 Ctrl+G 后，确认已出现“开始选课”按钮（判定已登录）
        course_button_xpath = "/html/body/div[1]/article/section/div[3]/div[2]/button"
        wait.until(EC.element_to_be_clickable((By.XPATH, course_button_xpath))).click()
        print("已点击 '开始选课' 按钮")
        #

        sleep(0.5)
        public_tab_xpath = "/html/body/div[1]/header/div[2]/ul/li[8]/a"
        wait.until(EC.element_to_be_clickable((By.XPATH, public_tab_xpath))).click()
        print("已点击 '收藏' 标签")

        def get_text_by_xpath_selenium(url, xpath_expr):
            opts = Options()
            opts.add_argument("--headless=new")
            with webdriver.Chrome(options=opts) as driver:
                driver.get(url)
                el = driver.find_element(By.XPATH, xpath_expr)
                return el.text.strip()

        table_tbody_xpath = "/html/body/div[1]/article/div[2]/div[2]/table/tbody"
        WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.XPATH, table_tbody_xpath))
        )

        # Build the rows XPath (all TRs)
        rows_xpath = table_tbody_xpath + "/tr"

        # Get texts/links from the first <td> <a> in each row
        saved = get_rows_first_link_texts(driver, rows_xpath)

        # sleep(0.5)
        # public_tab_xpath = "/html/body/div[1]/header/div[2]/ul/li[2]/a"
        # wait.until(EC.element_to_be_clickable((By.XPATH, public_tab_xpath))).click()
        # print("已点击 'public' 标签")


        #/html/body/div[1]/article/div[2]/div[2]/table/tbody/tr[1]
        # 你的原 JS 逻辑（保持不变）
        print(saved)

        js_code = f"""const excludedCourseNumbers = {excluded};"""+"""
        
        const campus = "鼓楼校区";  // 校区名称
        const xpath = "/html/body/div[3]/div[2]/div[2]/div[1]";  // Assure button
        const buttonXPath = "/html/body/div[1]/article/div[1]/div[3]/button[2]";  // 按钮的XPath路径
        

        function getElementByXPath(xpath) {
            const result = document.evaluate(
                xpath,
                document,
                null,
                XPathResult.FIRST_ORDERED_NODE_TYPE,
                null
            );
            return result.singleNodeValue;
        }

        function waitForElement(xpath) {
            return new Promise((resolve) => {
                const interval = setInterval(() => {
                    const targetElement = getElementByXPath(xpath);
                    if (targetElement) {
                        clearInterval(interval);
                        resolve(targetElement);
                    }
                }, 100);
            });
        }

        async function selectCourse() {
            const courseRows = document.querySelectorAll("tr.course-tr");
            let found = false;
            courseRows.forEach(row => {
                const numberCell = row.querySelector("td.kch a.cv-jxb-detail");
                const number = numberCell ? numberCell.getAttribute("data-number") : null;
                const campusCell = row.querySelector("td.xq");
                const campusText = campusCell ? campusCell.textContent.trim() : null;
                console.log(campusText);
                
                if (true) {
                    console.log(number);
                    const choiceButton = row.querySelector("td.cz a.cv-choice");
                    if (choiceButton) {
                        console.log(`找到校区为${campus}的课程，课程号is in saved list，正在点击“选择”按钮...`);
                       
                        choiceButton.click();
                        
                    } else {
                        console.log(`找到校区为${campus}的课程，课程号is in saved list，但未找到“选择”按钮。`);
                    }
                    found = true;
                }
            });

            if (!found) {
                console.log(`未找到校区为${campus}且课程号在saved列表中的课程。`);
            }
            try {
                const targetElement = await waitForElement(xpath);
                console.log("找到Assure，正在点击...");//Clicking assuring button
                targetElement.click();
                hold(100)
                targetElement.click();
            } catch (error) {
                console.error("出现错误：", error);
            }
        }

        setInterval(selectCourse, 2000);

        async function clickButtonPeriodically() {
            try {
                const button = await waitForElement(buttonXPath);
                console.log("找到按钮，正在点击...");
                

                button.click();
            } catch (error) {
                console.error("按钮未找到或点击失败：", error);
            }
        }
        setInterval(clickButtonPeriodically,2000);
        """

        driver.execute_script(js_code)
        print("已注入并执行 JavaScript 课程选择逻辑代码")
        return True

    except WebDriverException as e:
        print("浏览器操作异常:", str(e))
        return False



import time

def schedule_run():
    while True:
        try:
            result = run_course_selection()
            if result is True:
                print("run_course_selection 执行成功，等待10分钟后再执行")
                time.sleep(12000000*60)  # 15分钟
            else:
                print("run_course_selection 未正确返回，立即重试")
        except Exception as e:
            print("运行过程中出现异常:", e)
            print("立即重新执行...")


if __name__ == "__main__":
    schedule_run()