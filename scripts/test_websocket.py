#!/usr/bin/env python3
"""
WebSocket测试脚本
用于测试后端WebSocket服务器是否正常工作
"""

import asyncio
import websockets
import json
import sys
import socket

async def test_websocket(url):
    """测试WebSocket连接
    
    Args:
        url: WebSocket服务器URL
    """
    # 确保URL不以/ws结尾
    if url.endswith('/ws'):
        url = url[:-3]
        
    print(f"正在连接WebSocket服务器: {url}")
    
    try:
        # 使用更简单的连接方式，避免loop参数问题
        async with websockets.connect(url, ping_interval=None, close_timeout=2) as websocket:
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

def get_local_ip():
    """获取本机IP地址"""
    try:
        # 创建一个临时socket连接到一个公共IP，获取本机IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception as e:
        print(f"获取本机IP失败: {str(e)}")
        return "127.0.0.1"

async def main():
    """主函数"""
    # 默认WebSocket URL
    url = "ws://localhost:5005"
    
    # 如果提供了命令行参数，使用提供的URL
    if len(sys.argv) > 1:
        url = sys.argv[1]
    
    # 尝试连接
    print("尝试连接到WebSocket服务器...")
    success = await test_websocket(url)
    
    if success:
        print("WebSocket服务器工作正常")
    else:
        print("WebSocket服务器连接失败")
        
        # 尝试不同的路径组合
        alternate_urls = [
            f"ws://localhost:5005/ws",
            f"ws://127.0.0.1:5005",
            f"ws://127.0.0.1:5005/ws"
        ]
        
        for alt_url in alternate_urls:
            if url != alt_url:
                print(f"尝试备用地址: {alt_url}")
                success = await test_websocket(alt_url)
                if success:
                    print(f"备用地址连接成功: {alt_url}")
                    break
        
        # 如果仍然失败，尝试使用本机IP
        if not success:
            # 获取本机IP并尝试连接
            local_ip = get_local_ip()
            local_url = f"ws://{local_ip}:5005"
            
            if url != local_url:
                print(f"尝试使用本机IP地址: {local_url}")
                success = await test_websocket(local_url)
                if success:
                    print(f"使用本机IP地址连接成功: {local_ip}")
                    print("建议在前端配置中使用此IP地址")

if __name__ == "__main__":
    asyncio.run(main()) 