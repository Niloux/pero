import traceback
from typing import Dict, Optional, Tuple
from urllib.parse import quote

import aiohttp

from pero.cmd.commands import BaseCommand
from pero.utils.config import config
from pero.utils.logger import logger

WEATHER_KEY = config.WEATHER_KEY
LOCATION_KEY = config.LOCATION_KEY


class WeatherService:
    def __init__(self):
        self._session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self._session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            await self._session.close()

    async def fetch_json(self, url: str) -> Dict:
        """通用的异步 GET 请求函数，返回 JSON 数据"""
        if not self._session:
            raise RuntimeError(
                "Session not initialized. Use 'async with' context manager."
            )
        async with self._session.get(url) as response:
            return await response.json()

    async def get_location(self, city: str) -> Tuple[Optional[float], Optional[float]]:
        """调用腾讯地图接口，根据城市获取经纬度"""
        city = quote(city)
        url = (
            f"https://apis.map.qq.com/ws/geocoder/v1/?address={city}&key={LOCATION_KEY}"
        )

        data = await self.fetch_json(url)
        if data.get("status") != 0:
            logger.error(f"获取经纬度失败: {data.get('message')}")
            return None, None

        location = data.get("result", {}).get("location", {})
        return location.get("lat"), location.get("lng")

    async def get_weather(self, lat: float, lon: float) -> str:
        """调用天气接口，根据经纬度获取天气信息"""
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_KEY}&lang=zh_cn"

        data = await self.fetch_json(url)
        if not data:
            logger.error("获取天气信息失败")
            return "无法获取天气信息, 可能是网络异常, 请重试"

        location = data.get("name", "未知地点")
        weather = data.get("weather", [{}])[0].get("description", "未知天气")
        main = data.get("main", {})
        temperature_c = main.get("temp", 0) - 273.15
        temperature_feel = main.get("feels_like", 0) - 273.15
        humidity = main.get("humidity", 0)
        wind_speed = data.get("wind", {}).get("speed", 0)
        visibility = data.get("visibility", 0) / 1000

        return (
            f"地点: {location}\n"
            f"天气状况: {weather}\n"
            f"当前温度: {temperature_c:.2f}°C\n"
            f"体感温度: {temperature_feel:.2f}°C\n"
            f"湿度: {humidity}%\n"
            f"风速: {wind_speed} m/s\n"
            f"能见度: {visibility:.1f} km"
        )


class Forecast(BaseCommand):
    command_name = "weather"

    async def execute(self) -> str:
        """处理天气查询命令"""

        location = self.text.strip()
        if not location:
            return "命令无效，请在命令后添加城市名称。"

        try:
            return await self.get_forecast(location)
        except Exception as e:
            error_msg = f"获取天气失败: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            return error_msg

    async def get_forecast(self, city: str) -> str:
        """根据城市名称获取天气信息"""
        async with WeatherService() as service:
            lat, lon = await service.get_location(city)

            if lat is None or lon is None:
                return f"无法获取城市 {city} 的经纬度信息，请检查输入是否正确。"

            return await service.get_weather(lat, lon)


# # 支持并发查询多个城市的示例
# async def get_multiple_forecasts(cities: list[str]) -> list[str]:
#     async with WeatherService() as service:
#         tasks = [Forecast("weather", city).get_forecast(city) for city in cities]
#         return await asyncio.gather(*tasks)
