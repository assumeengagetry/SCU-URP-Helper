# SCU URP Helper

四川大学本科教务系统选课 GUI 助手，已适配新版教务处登录和选课接口。

## 免责声明

本项目仅供学习交流。使用本项目即表示你已理解并同意自行承担使用行为及其后果。作者不对账号安全、选课结果、教务系统限制、网络异常或其他使用后果负责。

## 功能

- 登录四川大学本科教务系统
- 按课程名关键词查询自由选课列表
- 添加目标课程到抢课列表
- 自动轮询课余量并提交选课
- 查看已选课程并退课
- 使用 `ddddocr` 自动识别选课提交验证码

## 环境

- Python `>=3.8,<3.10`
- `uv`

PySide2 对 Python 版本较敏感，本项目通过 `pyproject.toml` 和 `uv.lock` 锁定到兼容范围。建议直接使用 `uv` 安装和运行。

## 快速开始

```bash
git clone <your-repo-url>
cd SCU-URP-Helper
uv sync
uv run python main.py
```

首次运行前可以复制配置模板：

```bash
cp config.json.example config.json
```

`config.json` 字段说明：

- `username`：学号，可留空并在 GUI 中输入
- `password`：密码，可留空并在 GUI 中输入
- `major_id`：培养方案号，程序会尝试从教务页面自动读取并写入
- `sleep_time`：抢课轮询基础间隔，单位秒
- `sleep_jitter`：轮询间隔随机抖动，单位秒

`config.json` 和 `userinfo.json` 都只用于本地保存账号配置，已被 `.gitignore` 忽略，不要提交到公开仓库。

## 使用说明

1. 启动程序后在登录页输入学号、密码和登录验证码。
2. 进入菜单后选择“添加课程”，用课程名关键词搜索课程。
3. 在查询结果表格中选中目标课程，点击“添加”。
4. 回到菜单进入“开始抢课”，设置轮询间隔后点击“开始抢课”。
5. 可在“查看课表”中查看已选课程并退课。

## 新版接口适配点

- 登录页动态解析 `action`、隐藏字段和 `tokenValue`
- 根据登录页 JS 自动选择密码加密规则
- 保留项目内 JS 兼容 `hex_md5` 实现
- 选课提交使用新版 `kcIds = kch_kxh_zxjxjhh`
- 选课提交前请求 `getYzmPic.jpg` 并传入 `inputCode`
- 提交参数包含新版 `fajhh`、`kkxsh`、`kclbdm2`

## 开发验证

```bash
uv run python -m compileall main.py modules win
uv run python -c "import modules.utils, modules.userLogin, modules.AutoCourseGrabbing; print('imports ok')"
uv run python -c "import ddddocr; ddddocr.DdddOcr(show_ad=False); print('ocr ok')"
```

真实登录、查询、提交选课依赖教务系统在线状态、账号权限和选课阶段，需要在本地 GUI 中验证。
