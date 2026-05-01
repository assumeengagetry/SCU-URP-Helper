# SCU URP Helper

四川大学本科教务系统选课 GUI 助手。项目基于 PySide2 编写，已适配新版教务处登录与自由选课接口，并使用 `uv` 管理运行环境。

## 声明

本项目仅供学习和技术交流。使用本项目即表示你已理解并接受以下事项：

- 账号、密码、验证码等信息由用户自行输入，程序不会上传到第三方服务器。
- 如选择保存登录信息，账号配置只会写入本地 `config.json` 或 `userinfo.json`。
- 自动查询和提交选课可能受到教务系统规则、网络状态、选课阶段和账号权限影响。
- 使用本项目造成的任何后果由使用者自行承担。

## 功能

- 登录四川大学本科教务系统
- 查询自由选课课程列表
- 添加目标课程到抢课列表
- 自动轮询课余量并提交选课请求
- 自动识别选课提交验证码
- 查看已选课程
- 支持退课操作

## 项目结构

```text
SCU-URP-Helper/
├── main.py                  # 程序入口
├── modules/                 # 登录、接口、抢课核心逻辑
├── win/                     # PySide2 窗口逻辑
├── ui/                      # Qt Designer UI 文件
├── config.json.example      # 本地配置模板
├── pyproject.toml           # uv/Python 项目配置
├── uv.lock                  # uv 锁文件
└── README.md
```

## 环境要求

- Python `>=3.8,<3.10`
- `uv`

PySide2 对 Python 版本兼容性要求较严格，推荐使用 `uv` 自动创建兼容环境，不建议直接用系统 Python 运行。

## 安装运行

```bash
git clone <your-repo-url>
cd SCU-URP-Helper
uv sync
uv run python main.py
```

如果还没有安装 `uv`，可以参考官方文档：<https://docs.astral.sh/uv/>

## 配置

首次使用可以复制配置模板：

```bash
cp config.json.example config.json
```

配置示例：

```json
{
  "username": "",
  "password": "",
  "major_id": "",
  "sleep_time": 2,
  "sleep_jitter": 0.5
}
```

字段说明：

- `username`：学号，可留空，在 GUI 登录页输入
- `password`：密码，可留空，在 GUI 登录页输入
- `major_id`：培养方案号，程序会尝试从教务页面自动获取
- `sleep_time`：抢课轮询基础间隔，单位为秒
- `sleep_jitter`：轮询间隔随机抖动，单位为秒

`config.json`、`userinfo.json`、验证码图片和运行缓存都已写入 `.gitignore`，不要提交这些本地文件。

## 使用流程

1. 启动程序：`uv run python main.py`。
2. 在登录页输入学号、密码和登录验证码。
3. 登录成功后进入菜单。
4. 点击“添加课程”，输入课程名关键词并查询。
5. 在表格中选中目标课程，点击“添加”。
6. 回到菜单点击“开始抢课”，设置轮询间隔后启动。
7. 如需查看或退课，进入“查看课表”。

## 新版接口适配

本版本参考新版接口实现，主要处理了以下变化：

- 动态解析登录页表单 `action`
- 动态携带登录页隐藏字段
- 动态解析 `tokenValue`
- 根据登录页 JS 选择密码加密规则
- 使用项目内 JS 兼容 `hex_md5` 实现
- 选课提交前获取 `getYzmPic.jpg` 验证码
- 使用 `ddddocr` 自动识别选课验证码
- 选课提交使用新版 `kcIds = kch_kxh_zxjxjhh`
- 提交新版 `fajhh`、`kkxsh`、`kclbdm2` 等字段

## 开发验证

```bash
uv sync --frozen
uv run python -m compileall main.py modules win
uv run python -c "import modules.utils, modules.userLogin, modules.AutoCourseGrabbing; print('imports ok')"
uv run python -c "import ddddocr; ddddocr.DdddOcr(show_ad=False); print('ocr ok')"
```

真实登录、课程查询和选课提交依赖教务系统在线状态、账号权限和选课阶段，需要在本地 GUI 中验证。

项目也包含 GitHub Actions 工作流，会在 push 和 pull request 时执行依赖同步、语法编译和核心模块导入检查。

## 常见问题

### uv sync 后为什么使用 Python 3.9？

PySide2 的兼容范围有限，本项目在 `pyproject.toml` 中限制了 Python 版本。`uv` 会自动选择或下载兼容解释器。

### 登录成功但无法查询课程？

通常是当前不在自由选课阶段、教务系统响应异常、账号无对应权限，或网络访问失败。

### 为什么不提交 config.json？

`config.json` 可能包含学号、密码和本地运行参数，属于个人本地配置，不应进入公开仓库。

## 许可证

本项目使用 MIT License，详见 `LICENSE`。
