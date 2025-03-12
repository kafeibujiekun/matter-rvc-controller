"""
WebSocket服务器
用于向前端推送设备状态
"""

import json
import asyncio
import logging
from flask import Flask
from flask_sock import Sock

logger = logging.getLogger(__name__)

class WebSocketServer:
    """WebSocket服务器，用于向前端推送设备状态"""
    
    def __init__(self, app: Flask):
        """初始化WebSocket服务器
        
        Args:
            app: Flask应用实例
        """
        self.app = app
        self.sock = Sock(app)
        self.clients = set()
        
        # 注册WebSocket路由
        self.sock.route('/ws')(self.ws_handler)
        
        # 注册Matter客户端状态回调
        if hasattr(app, 'matter_client') and app.matter_client is not None:
            app.matter_client.register_status_callback(self.on_device_status_update)
        else:
            logger.warning("Matter客户端未初始化，状态更新回调未注册")
    
    async def ws_handler(self, ws):
        """WebSocket连接处理函数
        
        Args:
            ws: WebSocket连接
        """
        # 添加到客户端列表
        self.clients.add(ws)
        logger.info(f"新的WebSocket客户端连接，当前连接数: {len(self.clients)}")
        
        try:
            # 发送当前设备状态
            await self.send_status_to_client(ws)
            
            # 保持连接直到客户端断开
            while True:
                message = await ws.receive()
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
                        await ws.send(json.dumps(response))
                        logger.info("已回复测试消息")
                except json.JSONDecodeError:
                    logger.warning(f"收到无效的JSON消息: {message}")
                except Exception as e:
                    logger.error(f"处理客户端消息时出错: {str(e)}")
        except Exception as e:
            logger.error(f"WebSocket连接出错: {str(e)}")
        finally:
            # 从客户端列表中移除
            self.clients.remove(ws)
            logger.info(f"WebSocket客户端断开连接，当前连接数: {len(self.clients)}")
    
    async def on_device_status_update(self, status):
        """设备状态更新回调函数
        
        Args:
            status: 设备状态
        """
        # 向所有客户端发送状态更新
        await self.broadcast_status(status)
    
    async def broadcast_status(self, status):
        """向所有客户端广播设备状态
        
        Args:
            status: 设备状态
        """
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
        self.clients -= clients_to_remove
        
        # 等待所有发送任务完成
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def send_status_to_client(self, client):
        """向单个客户端发送当前设备状态
        
        Args:
            client: WebSocket客户端
        """
        try:
            if hasattr(self.app, 'matter_client') and self.app.matter_client is not None:
                status = self.app.matter_client.get_device_status()
                message = {
                    "type": "status_update",
                    "data": status
                }
                
                await client.send(json.dumps(message))
            else:
                # 如果Matter客户端未初始化，发送一个空状态
                message = {
                    "type": "status_update",
                    "data": {
                        "cleaning_mode": "未知",
                        "operation_status": "离线",
                        "battery_level": 0
                    },
                    "message": "Matter客户端未连接"
                }
                await client.send(json.dumps(message))
        except Exception as e:
            logger.error(f"向WebSocket客户端发送状态失败: {str(e)}")
            # 如果发送失败，从客户端列表中移除
            if client in self.clients:
                self.clients.remove(client) 