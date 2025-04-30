# WebRequest ProMax

> ⚠️ 免责声明：本工具仅供安全研究和技术交流，严禁用于非法用途，否则产生的一切后果自行承担。

## 项目简介

WebBatchRequest Pro Max是一款基于python开发的轻量级Web请求工具，主要用于:

- 批量网站存活性探测
- 网站标题(Title)获取
- Banner识别(来源响应中头部 server)
- HTTP代理支持
- 批量未授权漏洞验证

本项目基于

https://github.com/ScriptKid-Beta/WebBatchRequest

https://github.com/XF-FS/WebBatchRequestpro

进行了重构和增强，修复了多个问题并新增了实用功能。

## ✨ 核心特性

### 基础功能

-  多种请求方式(GET/POST/HEAD/OPTION)
-  HTTP/socks5代理支持
-  自定义请求头(支持Host碰撞)
-  Cookie自定义
-  User-Agent自定义
- 自定义路径(路径框)
-  重定向(301/302/303/307/308)处理
-  多线程并发请求
-  数据导入导出(csv)

-  现代化UI界面重构
-  自定义浏览器打开链接
-  智能结果排序
-  基于EHole的指纹识别(可以自定义路径配置)
-  灵活的响应时间设置
-  请求重试机制
-  访问记录标记
-  空节点智能清理

- 修复响应长度排序bug
-  添加超时时间框
-  修改targets默认响应时间，来修复卡死问题
-  修改路径框，可以实现域名/ip地址+路径多对多拼接访问。
-  添加导入路径文件按钮用来导入路径。
- 修复内容长度排序异常
-  优化响应时间计算
-  解决线程阻塞问题
- Content-Type 批量请求可以选择( application/octet-stream application/x-www-form-urlencoded application/json)

## 项目结构

```
WebBatchRequestProMax/
├── main.py               # 应用入口：启动 PyQt5 应用
├── gui.py                # PyQt5 GUI 界面及逻辑
├── worker.py             # 后台请求工作线程类
├── tools/                # 工具模块
│   ├── config.py         # 配置文件读取与管理
│   ├── utils.py          # 通用工具函数（导入导出、解析等）
│   └── resources/        # 资源文件夹
│       ├── user_agents.txt   # 常用 User-Agent 列表
│       └── paths.txt         # 默认路径列表（用于域名+路径拼接）
├── config.properties     # 配置文件（浏览器路径、EHole 工具路径等）
├── requirements.txt      # 依赖包（PyQt5、requests[socks] 等）
└── README.md            # 项目说明文档（可选）



main.py：程序入口，创建并运行 PyQt5 应用；
gui.py：主窗口类（继承自 QMainWindow），负责搭建界面布局、事件绑定、启动/停止扫描等逻辑；
worker.py：自定义工作线程类（继承自 QThread 或 QRunnable），负责执行具体的 HTTP 请求，解析结果并通过信号传递给主线程更新界面；
tools/config.py：读取和管理 config.properties 配置（例如自定义浏览器路径、EHole 工具路径等）；
tools/utils.py：包含导入 CSV、导入路径文件、解析 HTML Title、格式化 URL、生成 HTTP headers、调用 EHole 等通用函数；
tools/resources/：存放辅助资源文件，如常用的 User-Agent 列表 user_agents.txt，以及默认路径列表 paths.txt（可用于域名+路径多对多拼接）等；
config.properties：配置文件示例（内容包括 browserPath 和 eholePath 两项​
github.com
，分别用于设置外部浏览器路径和 EHole 指纹识别工具路径）；
requirements.txt：列出所需 Python 包，如 PyQt5、requests[socks]（用于支持 SOCKS5 代理）等；
项目支持跨平台（Windows/Linux），GUI 默认使用中文界面，应用可通过 PyInstaller 等工具打包为独立可执行文件。
```