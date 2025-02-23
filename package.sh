#!/bin/bash

# 确保脚本抛出遇到的错误
set -e

# 创建临时目录
TEMP_DIR="daydoc_deploy"
mkdir -p $TEMP_DIR

# 复制必要文件
cp -r src $TEMP_DIR/
cp -r config $TEMP_DIR/
cp main.py $TEMP_DIR/
cp run.py $TEMP_DIR/
cp requirements.txt $TEMP_DIR/

# 创建必要的目录
mkdir -p $TEMP_DIR/logs

# 创建服务器安装脚本
cat > $TEMP_DIR/install.sh << 'EOF'
#!/bin/bash
set -e

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 设置执行权限
chmod +x run.py

# 设置 cron 任务
(crontab -l 2>/dev/null || true; echo "0 6 * * * cd $(pwd) && source venv/bin/activate && ./run.py >> $(pwd)/logs/cron.log 2>&1") | crontab -

echo "安装完成！"
EOF

# 设置执行权限
chmod +x $TEMP_DIR/install.sh

# 打包
tar -czf daydoc_deploy.tar.gz $TEMP_DIR

# 清理临时目录
rm -rf $TEMP_DIR

echo "打包完成！生成文件：daydoc_deploy.tar.gz"