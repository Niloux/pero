import json
import os
import mimetypes
import base64
from typing import Union


def trans_file(file_path):
    if not os.path.isfile(file_path):
        raise ValueError(f"The file {file_path} does not exist.")

    # 获取文件的 MIME 类型
    mime_type, _ = mimetypes.guess_type(file_path)

    if mime_type is None:
        raise ValueError("Unable to guess MIME type for the file.")

    with open(file_path, "rb") as file:
        file_data = file.read()
        encoded_data = base64.b64encode(file_data).decode("utf-8")

        return f"data:{mime_type};base64,{encoded_data}"


def convert(file_path: str, message_type: str) -> dict:
    """
    本地文件转换为base64编码的二进制内容,网络文件直接返回URL
    """
    if file_path.startswith("http") or file_path.startswith("base64://"):
        return {"type": message_type, "data": {"file": file_path}}
    elif os.path.exists(file_path):
        return {"type": message_type, "data": {"file": trans_file(file_path)}}
    raise ValueError("Invalid file path or URL.")


class MessageChain:
    def __init__(self, chain=None):
        self.chain = []
        if chain is None:
            return

        if isinstance(chain, str):
            try:
                # 尝试解析JSON字符串，保持列表顺序
                parsed_chain = json.loads(chain)
                if isinstance(parsed_chain, list):
                    self.chain = parsed_chain
                else:
                    self.chain = [Text(chain)]
            except json.JSONDecodeError:
                self.chain = [Text(chain)]
        elif isinstance(chain, list):
            # 直接使用传入的列表，保持原有顺序
            self.chain = list(chain)  # 创建新列表以避免引用问题

    def __str__(self):
        """确保字符串表示时保持顺序"""
        return json.dumps(self.chain, ensure_ascii=False)

    @property
    def elements(self) -> list:
        """将消息链转换为可序列化的字典列表"""
        return self.chain

    def __add__(self, other):
        """支持使用 + 连接两个消息链"""
        if isinstance(other, MessageChain):
            return MessageChain(self.chain + other.chain)
        return MessageChain(self.chain + [other])

    def display(self) -> str:
        """获取消息链的字符串表示"""
        result = []
        for elem in self.chain:
            if elem["type"] == "text":
                result.append(elem["data"]["text"])
            elif elem["type"] == "image":
                result.append("[图片]")
            elif elem["type"] == "at":
                result.append(f"@{elem['data']['qq']}")
            elif elem["type"] == "face":
                result.append("[表情]")
            elif elem["type"] == "music":
                result.append("[音乐]")
            elif elem["type"] == "video":
                result.append("[视频]")
            elif elem["type"] == "dice":
                result.append("[骰子]")
            elif elem["type"] == "rps":
                result.append("[猜拳]")
            elif elem["type"] == "json":
                result.append("[JSON]")
        return "".join(result)


class Element:
    """消息元素基类"""

    type: str = "element"
    type_map = {}

    def __new__(cls, *args, **kwargs):
        """直接返回字典而不是类实例"""
        instance = super().__new__(cls)
        instance.__init__(*args, **kwargs)
        return instance.to_dict()

    @classmethod
    def from_type(cls, type_value, *args, **kwargs):
        """根据type动态创建子类实例"""
        subclass = cls.type_map.get(type_value)
        if subclass:
            return subclass(*args, **kwargs)
        else:
            raise ValueError(f"Unknown type: {type_value}")

    @classmethod
    def register_subclass(cls, subclass):
        """注册子类"""
        cls.type_map[subclass.type] = subclass

    def to_dict(self) -> dict:
        """通用的转换方法，可以被子类继承并覆盖"""
        data = {key: getattr(self, key) for key in vars(self)}
        return {"type": self.type, "data": data}


class Text(Element):
    """文本消息元素"""

    type = "text"

    def __init__(self, text: str):
        self.text = text


class At(Element):
    type = "at"

    def __init__(self, qq: Union[int, str]):
        self.qq = qq


class AtAll(Element):
    type = "at"

    def to_dict(self):
        return {"type": "at", "data": {"qq": "all"}}


class Image(Element):
    type = "image"

    def __init__(self, path: str):
        self.path = path

    def to_dict(self) -> dict:
        return convert(self.path, "image")


class Face(Element):
    type = "face"

    def __init__(self, face_id: int):
        self.id = face_id


# TODO: 戳一戳
# class PokeMethods(str, Enum):
#     ChuoYiChuo = "ChuoYiChuo"
#     BiXin = "BiXin"
#     DianDian = "DianDian"


# class Poke(Element):
#     type = "poke"

#     def __init__(self, method: Union[PokeMethods, str]):
#         self.method = method

#     def to_dict(self) -> dict:
#         return {"type": "poke", "data": {"type": self.method}}


class Reply(Element):
    """回复消息元素"""

    type = "reply"

    def __init__(self, message_id: Union[int, str]):
        self.message_id = str(message_id)

    def to_dict(self) -> dict:
        return {"type": "reply", "data": {"id": self.message_id}}


class Json(Element):
    """JSON消息元素"""

    type = "json"

    def __init__(self, data: str):
        self.data = data

    def to_dict(self) -> dict:
        return {"type": "json", "data": {"data": self.data}}


class Record(Element):
    """语音消息元素"""

    type = "record"

    def __init__(self, file: str):
        self.file = file

    def to_dict(self) -> dict:
        return {"type": "record", "data": {"file": self.file}}


class Video(Element):
    """视频消息元素"""

    type = "video"

    def __init__(self, file: str):
        self.file = file

    def to_dict(self) -> dict:
        return {"type": "video", "data": {"file": self.file}}


class Dice(Element):
    """骰子消息元素"""

    type = "dice"

    def to_dict(self) -> dict:
        return {"type": "dice"}


class Rps(Element):
    """猜拳消息元素"""

    type = "rps"

    def to_dict(self) -> dict:
        return {"type": "rps"}


class Music(Element):
    """音乐分享消息元素"""

    type = "music"

    def __init__(self, type: str, id: str):
        self.music_type = type
        self.music_id = id

    def to_dict(self) -> dict:
        return {"type": "music", "data": {"type": self.music_type, "id": self.music_id}}


class CustomMusic(Element):
    """自定义音乐分享消息元素"""

    type = "music"

    def __init__(
        self, url: str, audio: str, title: str, image: str = "", singer: str = ""
    ):
        self.url = url
        self.audio = audio
        self.title = title
        self.image = image
        self.singer = singer

    def to_dict(self) -> dict:
        return {
            "type": "music",
            "data": {
                "type": "custom",
                "url": self.url,
                "audio": self.audio,
                "title": self.title,
                "image": self.image,
                "singer": self.singer,
            },
        }


# TODO: Markdown 图片
# class Markdown(Element):
#     type = "image"

#     def __init__(self, markdown: str):
#         self.markdown = markdown

#     async def to_dict(self) -> dict:
#         return convert(await md_maker(self.markdown), "image")


class File(Element):
    type = "file"

    def __init__(self, file: str):
        self.file = file

    def to_dict(self) -> dict:
        return convert(self.file, "file")
