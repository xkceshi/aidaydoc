├── src/
│   ├── rss/          # RSS 订阅和解析
│   ├── ai/           # AI 处理模块
│   ├── blog/         # 博客发布接口
│   └── utils/        # 工具函数
├── config/           # 配置文件
├── main.py          # 主程序
└── requirements.txt  # 依赖管理

配置参数（config.yaml）：
1. AI配置，如果使用硅基流动，配置上自己的api_key即可，model也可以做相应的调整
2. blog配置，由于我使用的typecho，所以需要在typecho中开启接收XMLRPC，并支持markdown写法

启动方法：
1. 执行package.sh将项目打包
2. 将压缩包放置到目标位置，比如服务器上
3. 解压后，进入对应目录使用python run.py执行
4. 当然，也可以放到crontab中定时启动
5. 在自己的博客中就可以看到效果啦
