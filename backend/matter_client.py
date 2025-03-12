"""
Matter Server WebSocket客户端
用于与Matter Server通信，获取设备状态并发送控制命令
"""

import json
import asyncio
import websockets
import logging
from config import MATTER_SERVER_WS_URL

logger = logging.getLogger(__name__)

class MatterClient:
    """Matter Server WebSocket客户端"""
    
    def __init__(self, ws_url=None):
        """初始化Matter客户端
        
        Args:
            ws_url: WebSocket服务器地址，默认使用配置文件中的地址
        """
        self.ws_url = ws_url or MATTER_SERVER_WS_URL
        self.websocket = None
        self.connected = False
        self.device_status = {
            "cleaning_mode": "未知",
            "operation_status": "离线",
            "battery_level": 0
        }
        self.status_callbacks = []
    
    async def connect(self):
        """连接到Matter Server"""
        try:
            self.websocket = await websockets.connect(self.ws_url)
            self.connected = True
            logger.info(f"已连接到Matter Server: {self.ws_url}")
            
            # 启动接收消息的任务
            asyncio.create_task(self._receive_messages())
            return True
        except Exception as e:
            logger.error(f"连接Matter Server失败: {str(e)}")
            self.connected = False
            return False
    
    async def disconnect(self):
        """断开与Matter Server的连接"""
        if self.websocket and self.connected:
            await self.websocket.close()
            self.connected = False
            logger.info("已断开与Matter Server的连接")
    
    async def _receive_messages(self):
        """接收来自Matter Server的消息"""
        try:
            while self.connected:
                message = await self.websocket.recv()
                await self._process_message(message)
        except websockets.exceptions.ConnectionClosed:
            logger.warning("与Matter Server的连接已关闭")
            self.connected = False
        except Exception as e:
            logger.error(f"接收消息时出错: {str(e)}")
            self.connected = False
    
    async def _process_message(self, message):
        """处理接收到的消息
        
        Args:
            message: 接收到的WebSocket消息
        """
        try:
            data = json.loads(message)
            # 根据消息类型处理不同的消息
            if "device_status" in data:
                self.device_status = data["device_status"]
                # 调用所有状态回调函数
                for callback in self.status_callbacks:
                    await callback(self.device_status)
                logger.debug(f"设备状态更新: {self.device_status}")
        except json.JSONDecodeError:
            logger.error(f"无效的JSON消息: {message}")
        except Exception as e:
            logger.error(f"处理消息时出错: {str(e)}")
    
    async def send_command(self, command, params=None):
        """向Matter Server发送命令
        
        Args:
            command: 命令名称
            params: 命令参数
            
        Returns:
            bool: 命令是否发送成功
        """
        if not self.connected:
            logger.error("未连接到Matter Server，无法发送命令")
            return False
        
        try:
            message = {
                "command": command,
                "params": params or {}
            }
            await self.websocket.send(json.dumps(message))
            logger.info(f"已发送命令: {command}, 参数: {params}")
            return True
        except Exception as e:
            logger.error(f"发送命令失败: {str(e)}")
            return False
    
    def register_status_callback(self, callback):
        """注册设备状态更新回调函数
        
        Args:
            callback: 回调函数，接收设备状态作为参数
        """
        if callback not in self.status_callbacks:
            self.status_callbacks.append(callback)
    
    def unregister_status_callback(self, callback):
        """取消注册设备状态更新回调函数
        
        Args:
            callback: 要取消的回调函数
        """
        if callback in self.status_callbacks:
            self.status_callbacks.remove(callback)
    
    def get_device_status(self):
        """获取当前设备状态
        
        Returns:
            dict: 设备状态信息
        """
        return self.device_status 