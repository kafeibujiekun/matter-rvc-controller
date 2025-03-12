#!/usr/bin/env python3
"""
独立WebSocket服务器测试脚本
用于测试WebSocket连接，不依赖于Flask应用
"""

import asyncio
import websockets
import json
import logging
import sys

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 客户端连接集合
clients = set()

async def handle_client(websocket):
    """处理WebSocket客户端连接
    
    Args:
        websocket: WebSocket连接
    """
    # 添加到客户端列表
    clients.add(websocket)
    logger.info(f"新的WebSocket客户端连接，当前连接数: {len(clients)}")
    
    try:
        # 发送欢迎消息
        welcome_message = {
            "type": "welcome",
            "data": "欢迎连接到WebSocket服务器"
        }
        await websocket.send(json.dumps(welcome_message))
        
        # 保持连接直到客户端断开
        async for message in websocket:
            logger.info(f"收到消息: {message}")
            
            try:
                data = json.loads(message)
                # 回复消息
                response = {
                    "type": "response",
                    "data": f"已收到消息: {data.get('data', '')}"
                }
                await websocket.send(json.dumps(response))
            except json.JSONDecodeError:
                logger.warning(f"收到无效的JSON消息: {message}")
                # 回复错误消息
                error_message = {
                    "type": "error",
                    "data": "无效的JSON消息"
                }
                await websocket.send(json.dumps(error_message))
    except websockets.exceptions.ConnectionClosed:
        logger.info("客户端连接已关闭")
    except Exception as e:
        logger.error(f"处理客户端连接时出错: {str(e)}")
    finally:
        # 从客户端列表中移除
        clients.remove(websocket)
        logger.info(f"客户端断开连接，当前连接数: {len(clients)}")

async def main():
    """主函数"""
    # 默认主机和端口
    host = "0.0.0.0"
    port = 5000
    
    # 如果提供了命令行参数，使用提供的主机和端口
    if len(sys.argv) > 1:
        host = sys.argv[1]
    if len(sys.argv) > 2:
        port = int(sys.argv[2])
    
    # 启动WebSocket服务器
    async with websockets.serve(handle_client, host, port):
        logger.info(f"WebSocket服务器已启动，监听 {host}:{port}/ws")
        logger.info("按Ctrl+C停止服务器")
        
        # 保持服务器运行
        await asyncio.Future()  # 运行直到被取消

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("服务器已停止") 