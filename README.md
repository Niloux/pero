# Pero — QQ机器人

Pero 是一款基于 WebSocket 通信和 napcat 对接的 QQ 机器人，通过插件管理和消息注册的方式实现自动化功能。它能通过与 **NapCat** 的 WebSocket 通信进行互动，同时支持灵活的插件扩展，轻松实现多种机器人功能~

## 特性

- **WebSocket 通信**: 实现与 **NapCat** 进行实时消息通信。
- **API 对接**: 与 **NapCat** 相关的 API 无缝连接，支持丰富的消息操作。
- **消息注册系统**: 支持注册自定义消息，处理特定事件。
- **插件管理**: 支持按需加载插件，扩展机器人的功能。
- **灵活扩展**: 插件可以轻松添加和删除，功能扩展超方便！

## 依赖

- Python 3.7+
- **WebSocket-client**: 用于 WebSocket 通信。
- **Requests**: 用于 HTTP 请求。
- **apscheduler**: 用于定时任务调度。
- **pluginbase**: 用于插件管理。
- **以上由chatgpt自动生成......**

## 安装

首先，安装依赖项喵~

```bash
pip install -r requirements.txt
