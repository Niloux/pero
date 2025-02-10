from openai import OpenAI

from pero.config import Config

config = Config("config.yaml")

DS_API = config.deepseek_api
KM_API = config.kimi_api
deepseek_url = "https://api.deepseek.com"
kimi_url = "https://api.moonshot.cn/v1"

client = OpenAI(api_key=KM_API, base_url=kimi_url)

response = client.chat.completions.create(
    # model="deepseek-chat", # 普通模型
    # model="deepseek-reasoner", # 推理模型
    model="moonshot-v1-8k",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Hello, please introduce yourself"},
    ],
    stream=False,
)

print(response.choices[0].message.content)
