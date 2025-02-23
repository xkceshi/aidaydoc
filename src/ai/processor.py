import aiohttp
from typing import List, Dict
import logging
from datetime import datetime
import re  # 添加 re 模块导入

logger = logging.getLogger('daydoc')

class ContentProcessor:
    def __init__(self, config: Dict):
        self.config = config
        self.api_endpoint = config['api_endpoint']
        self.api_key = config['api_key']
        self.model = config['model']
        self.temperature = config['temperature']
        self.max_tokens = config['max_tokens']

    async def process(self, articles: List[Dict]) -> Dict:
        logger.info("开始使用 AI 处理文章内容")
        try:
            prompt = self._prepare_prompt(articles)
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                current_date = datetime.now().strftime("%Y%m%d")
                
                payload = {
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": "你是一个专业的科技新闻编辑，善于总结和归纳新闻要点，擅长写出吸引人的标题。请确保生成完整的文章内容，不要中途截断。"},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": self.temperature,
                    "max_tokens": 4000,  # 增加 token 限制
                    "top_p": 0.95,  # 添加 top_p 参数提高生成质量
                }
                
                logger.info("正在调用 AI 接口...")
                async with session.post(self.api_endpoint, headers=headers, json=payload) as response:
                    result = await response.json()
                    content = result['choices'][0]['message']['content']
                    
                    # 检查内容是否完整
                    if "## 今日趋势" not in content:
                        logger.warning("生成的内容不完整，尝试重新生成...")
                        # 这里可以添加重试逻辑
                    
                    # 如果AI没有添加字数统计，手动添加
                    if "本文字数" not in content[:100]:
                        char_count = len(re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9]', '', content))
                        read_time = max(1, round(char_count / 300))
                        content = f"# {content.split('#', 1)[1].strip()}\n\n> 本文字数：约 {char_count} 字，预计阅读时间：{read_time} 分钟\n\n" + content.split('\n', 1)[1]
                    
                    # 添加文章元信息
                    sources = list(set(article['source'] for article in articles))
                    footer = f"\n\n---\n\n**作者**：{self.model}  \n**文章来源**：{', '.join(sources)}  \n**编辑**：小康"
                    content_with_footer = content + footer
                    
                    return {
                        "title": f"【{current_date}AI日报】{self._extract_highlight_title(articles)}",
                        "content": content_with_footer,
                        "source_articles": articles
                    }
        except Exception as e:
            logger.error(f"AI 处理失败: {str(e)}")
            raise

    def _prepare_prompt(self, articles: List[Dict]) -> str:
        articles_info = []
        for article in articles:
            # 只在有图片时添加图片信息
            article_info = f"""标题：{article['title']}
来源：{article['source']}
链接：{article['link']}
摘要：{article.get('summary', '')}
图片：{article.get('image_url', '')}"""
            articles_info.append(article_info)
        
        articles_text = "\n\n".join(articles_info)
        
        return f"""请基于以下新闻生成一篇详尽的AI科技日报，使用Markdown格式。请注意：
1. 只选取与人工智能、机器学习、大语言模型等AI相关的新闻进行报道
2. 如果新闻内容与AI关系不大，请跳过该新闻
3. 确保每条新闻都突出其在AI领域的意义和影响

文章结构要求：
1. 文章结构：
   - 第一行：> 本文字数：约 xxxx 字，预计阅读时间：xx 分钟
   - 重点新闻（3条）：每条新闻格式如下：
     > ## [新闻标题](原文链接)
     > 
     > ![新闻图片](图片URL)  // 仅在有图片时添加此行
     > 
     > 新闻内容（至少300字的详细介绍）
   - 其他新闻（7-8条）：每条新闻格式如下：
     ## [新闻标题](原文链接)
     ![新闻图片](图片URL)  // 仅在有图片时添加此行
     新闻内容（至少200字的详细介绍）
   - 最后：## 总结（简要总结今日AI领域的主要动向，200字左右）

2. 内容要求：
   - 重点新闻：使用引用格式（>），内容至少300字
   - 其他新闻：内容至少200字
   - 总结部分：控制在200字左右
   - 保持专业性和可读性的平衡
   - 突出AI相关的技术细节和影响

3. 格式要求：
   - 标题必须使用链接格式：[标题文字](原文链接)
   - 重点新闻必须使用引用格式（>）
   - 有图片的新闻必须展示图片
   - 使用分隔线（---）分隔重点新闻和其他新闻
   - 确保文章格式统一且美观

新闻信息如下：
{articles_text}"""

    def _extract_highlight_title(self, articles: List[Dict]) -> str:
        # 这里可以实现一个简单的算法来选择最吸引人的标题
        # 目前简单返回第一篇文章的标题
        if articles:
            return articles[0]['title']
        return "今日AI要闻汇总"