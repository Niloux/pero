import asyncio

from pero.core.application import Application
from pero.utils.logger import logger


def main():
    """应用程序入口点"""
    app = Application()
    try:
        asyncio.run(app.run())
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise
    finally:
        logger.info("Application terminated")


if __name__ == "__main__":
    main()
