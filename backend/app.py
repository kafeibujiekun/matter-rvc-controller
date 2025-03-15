"""
RVC控制端Web应用
Flask后端主程序
"""

import os
import logging
import asyncio
import signal
from flask import Flask, render_template, send_from_directory, jsonify
from flask_cors import CORS
import config
from matter_client import MatterClient
from api.routes import api
from ws_service import ws_service
from config import MATTER_SERVER_WS_URL

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)

# 设置Matter客户端日志级别为DEBUG，以显示详细的通信日志
matter_logger = logging.getLogger('matter_client')
matter_logger.setLevel(logging.DEBUG)

# 添加文件处理器，将通信日志保存到文件
if not os.path.exists('logs'):
    os.makedirs('logs')
file_handler = logging.FileHandler('logs/matter_communication.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
matter_logger.addHandler(file_handler)

# 添加控制台处理器，在控制台显示通信日志
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
matter_logger.addHandler(console_handler)

logger = logging.getLogger(__name__)
logger.info("日志系统已配置，Matter通信日志将保存到 logs/matter_communication.log 并显示在控制台")

# 创建Flask应用
app = Flask(__name__, 
            static_folder='../frontend/dist/static', 
            template_folder='../frontend/dist')

# 允许跨域请求
CORS(app)

# 加载配置
app.config.from_object(config)

# 设备基本信息
app.config['DEVICE_INFO'] = {
    "product_name": "未知",
    "manufacturer": "未知",
    "hardware_version": "未知",
    "software_version": "未知",
    "serial_number": "未知",
    "matter_version": "未知",
    "operational_state": "未知",
    "ip_address": "未知"
}

# 注册API蓝图
app.register_blueprint(api, url_prefix='/api')

# Matter客户端
app.matter_client = None

# 将WebSocket服务添加到应用上下文中
app.ws_service = ws_service

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    """提供前端静态文件"""
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return render_template('index.html')

async def init_matter_client():
    """初始化Matter客户端"""
    app.matter_client = MatterClient()
    connected = await app.matter_client.connect()
    if connected:
        logger.info("Matter客户端初始化成功")
    else:
        logger.warning("Matter客户端初始化失败，将在后台重试连接")
        # 启动后台任务尝试重新连接
        asyncio.create_task(reconnect_matter_server())

async def reconnect_matter_server():
    """重新连接Matter Server"""
    # 如果已连接，先断开连接
    if app.matter_client and app.matter_client.connected:
        await app.matter_client.disconnect()
    
    # 尝试重新连接
    retry_count = 0
    max_retries = 5
    retry_interval = 5  # 秒
    
    while retry_count < max_retries:
        logger.info(f"尝试连接Matter Server ({retry_count + 1}/{max_retries})...")
        connected = await app.matter_client.connect()
        
        if connected:
            logger.info("成功连接到Matter Server")
            return True
        
        retry_count += 1
        logger.warning(f"连接失败，{retry_interval}秒后重试...")
        await asyncio.sleep(retry_interval)
    
    logger.error(f"连接Matter Server失败，已达到最大重试次数 ({max_retries})")
    return False

# 将重连函数添加到应用上下文中，以便API可以调用
app.reconnect_matter_server = reconnect_matter_server

async def init_app():
    """初始化应用"""
    # 初始化Matter客户端
    await init_matter_client()
    
    # 启动WebSocket服务
    await app.ws_service.start()
    
    logger.info("应用初始化完成")

def run_app():
    """运行应用"""
    # 创建事件循环
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # 初始化应用
    loop.run_until_complete(init_app())
    
    # 处理信号
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(shutdown(loop)))
    
    # 启动Flask应用
    from hypercorn.asyncio import serve
    from hypercorn.config import Config
    
    config = Config()
    config.bind = ["0.0.0.0:5000"]  # HTTP接口端口为5000
    
    loop.run_until_complete(serve(app, config))

async def shutdown(loop):
    """关闭服务器"""
    logger.info("正在关闭服务...")
    
    # 关闭WebSocket服务器
    await app.ws_service.stop()
    
    # 停止事件循环
    loop.stop()

if __name__ == '__main__':
    run_app() 