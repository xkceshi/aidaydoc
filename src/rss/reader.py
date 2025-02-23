import feedparser
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import List, Dict
import logging
import time
from email.utils import parsedate_to_datetime
import re  # 添加 re 模块导入

logger = logging.getLogger('daydoc')

class RSSReader:
    def __init__(self, sources: List[Dict]):
        self.sources = sources

    def _extract_image_url(self, content: str, source: str) -> str:
        """从文章正文中提取第一张图片URL"""
        if not content:
            return ''
        
        # 通用图片提取（获取第一张图片）
        img_tags = re.findall(r'<img[^>]+>', content)
        for img_tag in img_tags:
            src_match = re.search(r'src="([^"]+)"', img_tag)
            if src_match:
                url = src_match.group(1)
                # 过滤掉无效的图片URL
                if url and not url.startswith(('data:', 'javascript:', '图片URL')):
                    # 针对机器之心的特殊处理
                    if source == "机器之心" and 'image.jiqizhixin.com' not in url:
                        continue
                    return url
        return ''

    async def fetch_feed(self, session: aiohttp.ClientSession, source: Dict) -> List[Dict]:
        try:
            logger.info(f"开始获取 {source['name']} 的 RSS 内容")
            async with session.get(source['url']) as response:
                content = await response.text()
                feed = feedparser.parse(content)
                
                articles = []
                current_time = datetime.now()
                cutoff_time = current_time - timedelta(hours=24)
                
                for entry in feed.entries:
                    try:
                        # 解析发布时间
                        if 'published_parsed' in entry:
                            pub_date = datetime.fromtimestamp(time.mktime(entry.published_parsed))
                        elif 'published' in entry:
                            pub_date = parsedate_to_datetime(entry.published)
                        else:
                            continue
                        
                        # 检查是否在24小时内
                        if pub_date < cutoff_time:
                            continue
                        
                        # 提取文章主图
                        image_url = ''
                        
                        # 按优先级检查内容字段
                        content_fields = []
                        # 1. 优先检查正文内容
                        if hasattr(entry, 'content'):
                            for content in entry.content:
                                if 'value' in content:
                                    content_fields.append(('content', content['value']))
                        # 2. 检查 content_encoded（机器之心等站点使用）
                        if hasattr(entry, 'content_encoded'):
                            content_fields.append(('content_encoded', entry.content_encoded))
                        # 3. 检查 description
                        if hasattr(entry, 'description'):
                            content_fields.append(('description', entry.description))
                        # 4. 最后检查 summary
                        if hasattr(entry, 'summary'):
                            content_fields.append(('summary', entry.summary))
                        
                        # 遍历所有内容字段查找图片
                        for field_name, field_content in content_fields:
                            if field_content:
                                image_url = self._extract_image_url(field_content, source['name'])
                                if image_url:
                                    logger.debug(f"在{field_name}中找到图片: {image_url}")
                                    break
                        
                        # 清理摘要中的HTML标签
                        summary = re.sub(r'<.*?>', '', entry.get('summary', '')) if 'summary' in entry else ''
                        
                        article = {
                            'title': entry.title,
                            'link': entry.link,
                            'source': source['name'],
                            'published': pub_date.isoformat(),
                            'summary': summary,
                            'image_url': image_url,  # 如果没找到图片，这里就是空字符串
                            'importance_score': self._calculate_importance(entry)
                        }
                        
                        articles.append(article)
                        
                        if len(articles) >= 10:
                            break
                            
                    except Exception as e:
                        logger.warning(f"处理文章时出错: {str(e)}")
                        continue
                
                logger.info(f"从 {source['name']} 获取到 {len(articles)} 篇文章")
                return articles
        except Exception as e:
            logger.error(f"从 {source['name']} 获取内容失败: {str(e)}")
            return []

    def _calculate_importance(self, entry) -> float:
        """计算文章重要性分数"""
        score = 0.0
        
        # 根据标题关键词加分
        important_keywords = ['突破', 'breakthrough', '发布', 'release', '重要', 'important',
                            '最新', '最新', '重磅', '革命性', 'revolutionary']
        title_lower = entry.title.lower()
        for keyword in important_keywords:
            if keyword.lower() in title_lower:
                score += 1.0
        
        # 根据内容长度加分
        if 'summary' in entry:
            score += min(len(entry.summary) / 1000, 2.0)  # 最多加2分
        
        # 根据发布时间加分（越新越重要）
        if 'published_parsed' in entry:
            hours_ago = (datetime.now() - datetime.fromtimestamp(time.mktime(entry.published_parsed))).total_seconds() / 3600
            score += max(0, 2.0 * (24 - hours_ago) / 24)  # 最多加2分
        
        return score

    async def fetch_all(self) -> List[Dict]:
        async with aiohttp.ClientSession() as session:
            tasks = [self.fetch_feed(session, source) for source in self.sources]
            results = await asyncio.gather(*tasks)
            
            # 合并所有文章
            all_articles = []
            for articles in results:
                all_articles.extend(articles)
            
            # 去重（基于标题）
            seen_titles = set()
            unique_articles = []
            for article in all_articles:
                if article['title'] not in seen_titles:
                    seen_titles.add(article['title'])
                    unique_articles.append(article)
            
            # 按重要性排序并选择前10-15篇
            sorted_articles = sorted(unique_articles, 
                                  key=lambda x: x['importance_score'], 
                                  reverse=True)
            final_articles = sorted_articles[:15]  # 最多保留15篇
            
            logger.info(f"总共获取 {len(all_articles)} 篇文章，"
                       f"去重后 {len(unique_articles)} 篇，"
                       f"最终选择 {len(final_articles)} 篇重要文章")
            
            return final_articles