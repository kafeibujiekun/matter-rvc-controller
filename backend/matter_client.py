"""
Matter Server WebSocket客户端
用于与Matter Server通信，获取设备状态并发送控制命令
"""

import json
import asyncio
import websockets
import logging
from config import MATTER_SERVER_WS_URL

# 配置日志
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
            "current_cleaning_mode": "未知",
            "operational_state": "未知",
            "battery_level": 0,
        }
        self.status_callbacks = []
        
        # 存储节点数据
        self.nodes = {}
        self.message_id_counter = 0
        
        logger.info("Matter客户端初始化完成，WebSocket地址: %s", self.ws_url)
    
    async def connect(self):
        """连接到Matter Server"""
        try:
            logger.info("正在连接到Matter Server: %s", self.ws_url)
            self.websocket = await websockets.connect(self.ws_url)
            self.connected = True
            logger.info("已成功连接到Matter Server: %s", self.ws_url)
            
            # 启动接收消息的任务
            asyncio.create_task(self._receive_messages())
            
            # 发送监听命令
            await self.start_listening()
            
            return True
        except Exception as e:
            logger.error("连接Matter Server失败: %s", str(e), exc_info=True)
            self.connected = False
            return False
    
    async def disconnect(self):
        """断开与Matter Server的连接"""
        if self.websocket and self.connected:
            logger.info("正在断开与Matter Server的连接")
            await self.websocket.close()
            self.connected = False
            logger.info("已断开与Matter Server的连接")
    
    async def _receive_messages(self):
        """接收来自Matter Server的消息"""
        try:
            logger.info("开始接收Matter Server消息")
            while self.connected:
                message = await self.websocket.recv()
                logger.debug("收到Matter Server消息: %s", message)
                await self._process_message(message)
        except websockets.exceptions.ConnectionClosed:
            logger.warning("与Matter Server的连接已关闭")
            self.connected = False
        except Exception as e:
            logger.error("接收消息时出错: %s", str(e), exc_info=True)
            self.connected = False
    
    async def _process_message(self, message):
        """处理接收到的消息
        
        Args:
            message: 接收到的WebSocket消息
        """
        try:
            data = json.loads(message)
            
            # 打印完整的接收消息
            logger.info("处理Matter Server消息: %s", json.dumps(data, indent=2, ensure_ascii=False))
            
            # 处理节点列表响应
            if "message_id" in data and data.get("message_id") == "client" and "result" in data:
                logger.info("收到节点列表响应，共 %d 个节点", len(data["result"]))
                await self._process_nodes_list(data["result"])
                logger.info("已处理节点列表数据")
            
            # 处理设备状态更新
            elif "device_status" in data:
                logger.info("收到设备状态更新: %s", json.dumps(data["device_status"], ensure_ascii=False))
                self.device_status = data["device_status"]
                # 调用所有状态回调函数
                for callback in self.status_callbacks:
                    await callback(self.device_status)
            
            # 处理命令响应
            elif "message_id" in data and data.get("message_id").startswith("cmd_"):
                logger.info("收到命令响应: %s", json.dumps(data, indent=2, ensure_ascii=False))
            
            # 其他类型的消息
            else:
                logger.info("收到其他类型消息: %s", json.dumps(data, indent=2, ensure_ascii=False))
                
        except json.JSONDecodeError:
            logger.error("无效的JSON消息: %s", message)
        except Exception as e:
            logger.error("处理消息时出错: %s", str(e), exc_info=True)
    
    async def _process_nodes_list(self, nodes_data):
        """处理节点列表数据
        
        Args:
            nodes_data: 节点列表数据
        """
        # 清空现有节点数据
        self.nodes = {}
        
        # 处理每个节点
        for node in nodes_data:
            node_id = node.get("node_id")
            if node_id is not None:
                self.nodes[str(node_id)] = node
                logger.info("处理节点 %s: available=%s", node_id, node.get("available", False))
                
                # 如果节点可用，更新设备状态
                if node.get("available", False):
                    # 尝试从节点属性中获取操作状态
                    operational_state = "未知"
                    attributes = node.get("attributes", {})
                    if "1/97/4" in attributes:
                        try:
                            operational_state = attributes["1/97/4"]
                            logger.info("从节点 %s 获取到操作状态: %s", node_id, operational_state)
                        except Exception as e:
                            logger.error("获取操作状态时出错: %s", str(e))
                    
                    # 更新设备状态
                    self.device_status = {
                        "current_cleaning_mode": "未知",
                        "operational_state": operational_state,
                        "battery_level": 0,
                    }
                    logger.info("节点 %s 可用，更新设备状态: %s", node_id, json.dumps(self.device_status, ensure_ascii=False))
        
        # 调用所有状态回调函数
        for callback in self.status_callbacks:
            await callback(self.device_status)
    
    async def start_listening(self):
        """发送开始监听命令到Matter Server"""
        if not self.connected:
            logger.error("未连接到Matter Server，无法发送监听命令")
            return False
        
        try:
            message = {
                "message_id": "client",
                "command": "start_listening"
            }
            message_str = json.dumps(message)
            logger.info("发送监听命令到Matter Server: %s", message_str)
            await self.websocket.send(message_str)
            logger.info("监听命令已发送")
            return True
        except Exception as e:
            logger.error("发送监听命令失败: %s", str(e), exc_info=True)
            return False
    
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
            self.message_id_counter += 1
            message = {
                "message_id": f"cmd_{self.message_id_counter}",
                "command": command,
                "params": params or {}
            }
            message_str = json.dumps(message)
            logger.info("发送命令到Matter Server: %s", message_str)
            await self.websocket.send(message_str)
            logger.info("命令已发送: %s, 参数: %s", command, json.dumps(params or {}, ensure_ascii=False))
            return True
        except Exception as e:
            logger.error("发送命令失败: %s", str(e), exc_info=True)
            return False
    
    def register_status_callback(self, callback):
        """注册设备状态更新回调函数
        
        Args:
            callback: 回调函数，接收设备状态作为参数
        """
        if callback not in self.status_callbacks:
            self.status_callbacks.append(callback)
            logger.debug("已注册状态回调函数，当前回调函数数量: %d", len(self.status_callbacks))
    
    def unregister_status_callback(self, callback):
        """取消注册设备状态更新回调函数
        
        Args:
            callback: 要取消的回调函数
        """
        if callback in self.status_callbacks:
            self.status_callbacks.remove(callback)
            logger.debug("已取消注册状态回调函数，当前回调函数数量: %d", len(self.status_callbacks))
    
    def get_device_status(self):
        """获取当前设备状态
        
        Returns:
            dict: 设备状态信息
        """
        return self.device_status
    
    def get_node_info(self, node_id):
        """获取指定节点的信息
        
        Args:
            node_id: 节点ID
            
        Returns:
            dict: 节点信息，如果节点不存在则返回None
        """
        node_info = self.nodes.get(str(node_id))
        if node_info:
            logger.debug("获取节点 %s 信息成功", node_id)
        else:
            logger.warning("节点 %s 不存在", node_id)
        return node_info
    
    def get_all_nodes(self):
        """获取所有节点信息
        
        Returns:
            dict: 所有节点信息
        """
        logger.debug("获取所有节点信息，共 %d 个节点", len(self.nodes))
        return self.nodes 