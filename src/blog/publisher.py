import xmlrpc.client
from typing import Dict
import logging

logger = logging.getLogger('daydoc')

class BlogPublisher:
    def __init__(self, config: Dict):
        self.config = config
        self.server = xmlrpc.client.ServerProxy(f"{config['api_endpoint']}/xmlrpc.php")

    async def publish(self, content: Dict) -> Dict:
        try:
            logger.info("开始发布文章到博客")
            post = {
                'title': content['title'],
                'description': content['content'],
                'categories': [self.config['category']],
                'dateCreated': xmlrpc.client.DateTime()
            }
            
            try:
                post_id = self.server.metaWeblog.newPost(
                    '',
                    self.config['username'],
                    self.config['password'],
                    post,
                    True
                )
                # 如果能获取到 post_id，说明发布成功
                if post_id:
                    url = f"{self.config['api_endpoint']}/archives/{post_id}"
                    logger.info(f"文章发布成功，文章ID: {post_id}，访问地址: {url}")
                    return {
                        'success': True,
                        'post_id': post_id,
                        'url': url
                    }
            except xmlrpc.client.Fault as fault:
                # XML-RPC 调用失败
                logger.error(f"XML-RPC 调用失败: {fault.faultString}")
                return {'success': False, 'error': fault.faultString}
            except xmlrpc.client.ProtocolError as protocol_error:
                # 协议错误
                logger.error(f"协议错误: {protocol_error}")
                return {'success': False, 'error': str(protocol_error)}
            except Exception as xml_error:
                # 其他 XML 解析错误，但如果有 post_id 说明文章已发布成功
                if 'post_id' in locals():
                    logger.warning(f"文章已发布成功，但响应解析有误: {str(xml_error)}")
                    return {
                        'success': True,
                        'post_id': post_id,
                        'url': f"{self.config['api_endpoint']}/archives/{post_id}"
                    }
                raise
                
        except Exception as e:
            logger.error(f"文章发布失败: {str(e)}")
            return {'success': False, 'error': str(e)}