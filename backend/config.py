"""
RVC控制端配置文件
"""

# Matter Server WebSocket配置
MATTER_SERVER_WS_URL = "ws://192.168.2.21:5580/ws"

# Flask应用配置
DEBUG = True
SECRET_KEY = "dev-secret-key"  # 在生产环境中应更改为随机值

# WebSocket配置
WS_PING_INTERVAL = 30  # WebSocket心跳间隔（秒）

# 设备状态更新间隔（秒）
STATUS_UPDATE_INTERVAL = 1 