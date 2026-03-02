# 抢课脚本 by ErrDivine


## 准备步骤

- 安装python。对于Windows可以在cmd中运行
```cmd
winget search Python
winget install Python.Python.3.12 --accept-package-agreements --accept-source-agreements
```
对于Mac，在terminal（终端）中运行
```bash
brew install python
```
- 安装Chrome浏览器。
```bat
winget install --id Google.Chrome -e
```
然后运行
```bat
winget list Google.Chrome
winget upgrade --id Google.Chrome -e
```
对于Mac
```bash
brew install --cask google-chrome
```
- 右键selenium文件夹选择在终端打开，然后在终端或命令行中运行以下代码

Windows:
```bat
py -m pip install -r requirements.txt
```
Mac:
```bash
python3 -m pip install -r requirements.txt
```
- 把自己想蹲的课收藏到自己的账号里（在选课网站上点击收藏）
- 在**config.json**中编辑自己的学号和密码。
### 注意！！！！
***不要把不想选的课放进收藏里***，如果放出名额脚本会直接抢。尤其对于点击选择后会自动退选之前选过的同类课程的。




## 使用方式
这是针对2025大一补选课程的脚本。使用方式如下：


- 运行 sel.py，具体来说
```bash
python sel.py
```
- 运行后会弹出一个Chrome内的选课登录界面，和一个脚本弹窗。脚本弹窗中有使用说明。在此再说明一次：手动点击人机验证，点击登录，再点击确认，在“开始选课”页面停止。回到弹出的脚本对话框，按ctrl+g继续。
- 之后你会看到浏览器自动点击选择按钮和刷新按钮，当然，以一定的频率。
- 由于南京大学选课网站会定时清理长时间在线用户，所以每15分钟程序会自动停止并重新运行，此时需要你重复“登录”步骤。

### 一键运行脚本（更简单）(from GPT-5，没有测试过，ErrDivine不推荐)
- Windows：双击 `Selenium\run.cmd`（会自动安装依赖并启动脚本）。
- Mac：在“访达”中双击 `Selenium/run.command`，或在终端执行：`bash Selenium/run.sh`。
  - 如果提示“来自不受信任的开发者”，请在“系统设置-隐私与安全性”里允许运行，或改用终端命令运行。

---

## 一看就会（给不太熟电脑的同学）(From GPT-5)

### 准备好这些（只需一次）：
- 电脑上装好 Chrome 浏览器；
- 安装 Python（上面“准备步骤”里有教程）。

#### 把文件放好：
- 把整个项目文件夹下载到本地；找到里面的 `Selenium` 文件夹（里面有 `sel.py`、`config.json`、`requirements.txt`）。

#### 安装依赖（只需一次）：
- Windows：在“命令提示符/PowerShell”中先进入 `Selenium` 文件夹，然后输入：
  - `py -m pip install -r requirements.txt`
- Mac：在“终端”先进入 `Selenium` 文件夹，然后输入：
  - `python3 -m pip install -r requirements.txt`
如果提示找不到 `requirements.txt`，就改为：`pip install -r Selenium/requirements.txt`（先进入项目根目录再执行）。

#### 填写账号：
- 打开 `Selenium/config.json`，把“account”“password”改成你的学号和密码；`excluded` 可以留空数组 `[]`。

#### 开始运行：
- Windows：在 `Selenium` 文件夹里输入：`py sel.py`
- Mac：在 `Selenium` 文件夹里输入：`python3 sel.py`
接着会弹出浏览器登录页和一个小提示窗口：先在浏览器里完成登录/验证码，然后回到小窗口按下 `Ctrl+G` 继续。

#### 常见问题（简单排查）：
- 运行没反应：等 10～20 秒；看命令行是否有文字输出；确认已安装 Chrome。
- 说找不到 pip：用 `py -m pip ...`（Windows）或 `python3 -m pip ...`（Mac）。
- 说 Tk/tkinter 有问题：换用官方/应用商店安装的 Python 再试。
- 想退出程序：在命令行按 `Ctrl+C`，或关掉浏览器和小窗口。

