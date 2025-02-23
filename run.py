#!/usr/bin/env python3
import asyncio
from src.utils.logger import setup_logger
from main import main

if __name__ == "__main__":
    logger = setup_logger()
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"程序执行失败: {str(e)}")