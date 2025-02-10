import base64
import mimetypes
import os


def trans_file(file_path):
    # 获取文件的 MIME 类型
    mime_type, _ = mimetypes.guess_type(file_path)

    if mime_type is None:
        raise ValueError("Unable to guess MIME type for the file.")

    # 打开文件并读取为二进制数据
    with open(file_path, "rb") as file:
        file_data = file.read()

        # 将二进制数据编码为 Base64
        encoded_data = base64.b64encode(file_data)

        # 将 Base64 编码的数据转换为字符串
        base64_str = encoded_data.decode("utf-8")

        # 构造 data URI
        data_uri = f"data:{mime_type};base64,{base64_str}"

        return data_uri


def read_file(file_path) -> any:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def convert_uploadable_object(i, message_type):
    """将可上传对象转换为标准格式"""
    if i.startswith("http"):
        return {"type": message_type, "data": {"file": i}}
    elif i.startswith("base64://"):
        return {"type": message_type, "data": {"file": i}}
    elif os.path.exists(i):
        return {"type": message_type, "data": {"file": f"{trans_file(i)}"}}
    else:
        return {"type": message_type, "data": {"file": f"file:///{i}"}}
