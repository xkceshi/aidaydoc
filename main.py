import asyncio
from src.rss.reader import RSSReader
from src.ai.processor import ContentProcessor
from src.blog.publisher import BlogPublisher
from src.utils.config import load_config
from src.utils.logger import setup_logger

async def main():
    # 设置日志
    logger = setup_logger()
    logger.info("开始运行每日文章生成任务")

    try:
        # 加载配置
        config = load_config()
        logger.info("配置加载成功")
        
        # 初始化组件
        rss_reader = RSSReader(config['rss_sources'])
        content_processor = ContentProcessor(config['ai_config'])
        blog_publisher = BlogPublisher(config['blog_config'])
        
        # 获取 RSS 内容
        articles = await rss_reader.fetch_all()
        
        if not articles:
            logger.error("没有获取到任何文章，任务终止")
            return
            
        # 打印调试信息
        for article in articles:
            logger.debug(f"\n文章标题: {article['title']}")
            logger.debug(f"来源: {article['source']}")
            logger.debug(f"图片URL: {article.get('image_url', '无')}")
            logger.debug(f"摘要前100字符: {article.get('summary', '无')[:100]}")
            logger.debug("-" * 80)
        
        # AI 处理内容
        processed_content = await content_processor.process(articles)
        
        # 发布到博客
        result = await blog_publisher.publish(processed_content)
        
        if result['success']:
            logger.info(f"任务完成，文章已发布: {result['url']}")
        else:
            logger.error("文章发布失败")
            
    except Exception as e:
        logger.error(f"任务执行过程中发生错误: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())