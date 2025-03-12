#!/usr/bin/env python3
"""
WebSocket测试脚本
用于测试后端WebSocket服务器是否正常工作
"""

import asyncio
import websockets
import json
import sys

async def test_websocket(url):
    """测试WebSocket连接
    
    Args:
        url: WebSocket服务器URL
    """
    print(f"正在连接WebSocket服务器: {url}")
    
    try:
        # 使用更简单的连接方式，避免loop参数问题
        async with websockets.connect(url, ping_interval=None) as websocket:
            print("连接成功！")
            
            # 发送测试消息
            test_message = {
                "type": "test",
                "data": "Hello, WebSocket Server!"
            }
            await websocket.send(json.dumps(test_message))
            print(f"已发送测试消息: {test_message}")
            
            # 等待响应，设置超时
            try:
                print("等待响应...")
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"收到响应: {response}")
            except asyncio.TimeoutError:
                print("等待响应超时，但连接已建立")
            
            # 保持连接一段时间
            print("保持连接5秒...")
            await asyncio.sleep(5)
            
            print("测试完成，连接正常")
            return True
    except Exception as e:
        print(f"连接失败: {str(e)}")
        return False

async def main():
    """主函数"""
    # 默认WebSocket URL
    url = "ws://localhost:5000/ws"
    
    # 如果提供了命令行参数，使用提供的URL
    if len(sys.argv) > 1:
        url = sys.argv[1]
    
    success = await test_websocket(url)
    
    if success:
        print("WebSocket服务器工作正常")
    else:
        print("WebSocket服务器连接失败")
        
        # 尝试备用地址
        backup_url = "ws://127.0.0.1:5000/ws"
        if url != backup_url:
            print(f"尝试备用地址: {backup_url}")
            success = await test_websocket(backup_url)
            if success:
                print("备用地址连接成功，请更新前端配置")

if __name__ == "__main__":
    asyncio.run(main()) 