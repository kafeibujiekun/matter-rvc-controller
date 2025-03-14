"""
WebSocket服务模块
提供WebSocket服务功能，用于向前端推送设备状态
"""

import os
import json
import asyncio
import logging
import socket
import websockets
import subprocess
import sys

# 配置日志
logger = logging.getLogger(__name__)

class WebSocketService:
    """WebSocket服务类，用于管理WebSocket连接和消息广播"""
    
    def __init__(self):
        """初始化WebSocket服务"""
        self.clients = set()
        self.server = None
        
        # 设备状态（模拟数据）
        self.device_status = {
            "cleaning_mode": "标准",
            "operation_status": "待机",
            "battery_level": 80
        }
        
        # 状态更新任务
        self.update_task = None
    
    async def handle_client(self, websocket):
        """处理WebSocket客户端连接
        
        Args:
            websocket: WebSocket连接
        """
        # 添加到客户端列表
        self.clients.add(websocket)
        logger.info(f"新的WebSocket客户端连接，当前连接数: {len(self.clients)}")
        
        try:
            # 发送当前设备状态
            await self.send_status_to_client(websocket)
            
            # 保持连接直到客户端断开
            async for message in websocket:
                logger.debug(f"收到WebSocket客户端消息: {message}")
                
                # 处理测试消息
                try:
                    data = json.loads(message)
                    if data.get('type') == 'test':
                        # 回复测试消息
                        response = {
                            "type": "test_response",
                            "data": "Hello, WebSocket Client!",
                            "received": data.get('data', '')
                        }
                        await websocket.send(json.dumps(response))
                        logger.info("已回复测试消息")
                except json.JSONDecodeError:
                    logger.warning(f"收到无效的JSON消息: {message}")
                except Exception as e:
                    logger.error(f"处理客户端消息时出错: {str(e)}")
        except websockets.exceptions.ConnectionClosed:
            logger.info("客户端连接已关闭")
        except Exception as e:
            logger.error(f"WebSocket连接出错: {str(e)}")
        finally:
            # 从客户端列表中移除
            self.clients.remove(websocket)
            logger.info(f"WebSocket客户端断开连接，当前连接数: {len(self.clients)}")
    
    async def broadcast_status(self, status):
        """向所有客户端广播设备状态
        
        Args:
            status: 设备状态
        """
        if not self.clients:
            return
            
        message = {
            "type": "status_update",
            "data": status
        }
        
        # 将消息转换为JSON字符串
        message_str = json.dumps(message)
        
        # 创建发送任务列表
        tasks = []
        clients_to_remove = set()
        
        for client in self.clients:
            try:
                tasks.append(client.send(message_str))
            except Exception as e:
                logger.error(f"向WebSocket客户端发送消息失败: {str(e)}")
                clients_to_remove.add(client)
        
        # 移除失败的客户端
        for client in clients_to_remove:
            self.clients.remove(client)
        
        # 等待所有发送任务完成
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def send_status_to_client(self, client):
        """向单个客户端发送当前设备状态
        
        Args:
            client: WebSocket客户端
        """
        message = {
            "type": "status_update",
            "data": self.device_status
        }
        
        try:
            await client.send(json.dumps(message))
        except Exception as e:
            logger.error(f"向WebSocket客户端发送状态失败: {str(e)}")
    
    async def update_status_periodically(self):
        """定期更新设备状态（模拟）"""
        while True:
            # 模拟状态变化
            self.device_status["battery_level"] = max(0, min(100, self.device_status["battery_level"] + (-5 + 10 * (asyncio.get_event_loop().time() % 2 > 1))))
            
            # 广播状态更新
            await self.broadcast_status(self.device_status)
            
            # 等待一段时间
            await asyncio.sleep(10)
    
    def check_port_in_use(self, port):
        """检查端口是否被占用
        
        Args:
            port: 要检查的端口号
            
        Returns:
            tuple: (是否被占用, 占用进程信息)
        """
        # 使用socket检查端口是否被占用
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        
        if result == 0:  # 端口被占用
            # 尝试获取占用端口的进程信息
            process_info = "未知进程"
            try:
                if sys.platform.startswith('linux'):
                    cmd = f"lsof -i :{port} | grep LISTEN"
                    process = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                    if process.stdout:
                        process_info = process.stdout.strip()
                elif sys.platform == 'win32':
                    cmd = f"netstat -ano | findstr :{port}"
                    process = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                    if process.stdout:
                        process_info = process.stdout.strip()
            except Exception as e:
                logger.error(f"获取进程信息失败: {str(e)}")
            
            return True, process_info
        
        return False, None
    
    def print_port_usage_error(self, port, process_info):
        """打印端口占用错误信息
        
        Args:
            port: 被占用的端口
            process_info: 占用进程信息
        """
        error_message = f"""
========================================================================
错误: 端口 {port} 已被占用，无法启动WebSocket服务！

占用信息: {process_info}

请尝试以下解决方案:
1. 终止占用端口的进程:
   - Linux: sudo kill <进程ID>
   - Windows: taskkill /F /PID <进程ID>

2. 修改WebSocket服务端口:
   - 设置环境变量: export WS_PORT=<其他端口>
   - 或修改 .env 文件中的 WS_PORT 值

3. 重启系统，释放所有端口占用
========================================================================
"""
        logger.error(error_message)
        print(error_message, file=sys.stderr)
    
    async def start(self, host='0.0.0.0', port=None):
        """启动WebSocket服务器
        
        Args:
            host: 主机地址，默认为0.0.0.0
            port: 端口号，默认从环境变量获取或使用5005
        """
        # 获取端口
        if port is None:
            port = int(os.environ.get('WS_PORT', 5005))
        
        # 检查端口是否被占用
        port_in_use, process_info = self.check_port_in_use(port)
        if port_in_use:
            self.print_port_usage_error(port, process_info)
            raise OSError(f"端口 {port} 已被占用，无法启动WebSocket服务")
        
        # 启动WebSocket服务器
        try:
            self.server = await websockets.serve(self.handle_client, host, port)
            logger.info(f"WebSocket服务器已启动，监听 {host}:{port}")
            
            # 启动定期更新任务
            self.update_task = asyncio.create_task(self.update_status_periodically())
        except Exception as e:
            logger.error(f"启动WebSocket服务器失败: {str(e)}")
            raise
    
    async def stop(self):
        """停止WebSocket服务器"""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            logger.info("WebSocket服务器已关闭")
        
        # 取消定期更新任务
        if self.update_task:
            self.update_task.cancel()
            try:
                await self.update_task
            except asyncio.CancelledError:
                pass
    
    def update_device_status(self, status):
        """更新设备状态
        
        Args:
            status: 新的设备状态
        """
        self.device_status.update(status)
        
        # 创建异步任务广播状态
        asyncio.create_task(self.broadcast_status(self.device_status))

# 创建全局WebSocket服务实例
ws_service = WebSocketService() 