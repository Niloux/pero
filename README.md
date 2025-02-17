# Pero — QQ机器人框架

Pero 是一款基于 WebSocket 通信和 napcat 对接的 QQ 机器人框架，通过插件管理和消息注册的方式实现自动化功能。它能通过与 **NapCat** 的 WebSocket 通信进行互动，同时支持灵活的插件扩展，轻松实现多种机器人功能，实现自己理想的QQ机器人功能~

## 特性

- **WebSocket 通信**: 实现与 **NapCat** 进行实时消息通信。
- **API 对接**: 与 **NapCat** 相关的 API 无缝连接，支持丰富的消息操作。
- **消息注册系统**: 支持注册自定义消息，处理特定事件。
- **插件管理**: 支持按需加载插件，扩展机器人的功能。
- **灵活扩展**: 插件可以轻松添加和删除，功能扩展超方便！

## 依赖

- Python 3.7+
- [NapCat]

## 安装

首先，安装依赖项~

```bash
pip install -r requirements.txt
```

然后，配置 **config.yaml** 文件，填入相关配置。

## 使用方法

### 1.启动机器人

```bash
python main.py
```

这会启动一个 WebSocket 服务器，并连接到 NapCat 服务。

### 2.注册消息处理器

### 3.插件管理

### 4.消息发送与响应

### 5.定时任务


[napcat]: https://github.com/NapNeko/NapCatQQ



## 计划
- [x] message_adapter: message适配器，用于处理不同类型的message_event(尚不完善)
- [x] message_parser: message解析器，将message_event中的content分离出txt, at, image等，然后转换成统一标准的cmd以及适配插件的类型
- [x] BaseChatPlugin: chat插件基类，完善多轮对话、文件对话等基本功能
- [x] 数据库部署，主要用户多用户使用聊天插件的多轮对话或者文件对话场景
