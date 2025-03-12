"""
API路由
定义控制设备的HTTP接口
"""

from flask import Blueprint, jsonify, request, current_app
import asyncio

api = Blueprint('api', __name__)

@api.route('/status', methods=['GET'])
def get_status():
    """获取设备状态"""
    matter_client = current_app.matter_client
    status = matter_client.get_device_status()
    
    # 添加设备基本信息
    device_info = current_app.config.get('DEVICE_INFO', {
        "product_name": "RVC控制器",
        "hardware_version": "1.0.0",
        "software_version": "1.0.0",
        "ip_address": request.host
    })
    
    return jsonify({
        "status": "success",
        "data": {
            "device_info": device_info,
            "device_status": status
        }
    })

@api.route('/control', methods=['POST'])
async def control_device():
    """控制设备"""
    matter_client = current_app.matter_client
    data = request.json
    
    if not data or 'action' not in data:
        return jsonify({
            "status": "error",
            "message": "缺少必要参数"
        }), 400
    
    action = data['action']
    params = data.get('params', {})
    
    # 定义支持的操作
    supported_actions = {
        'start': '开始清洁',
        'stop': '停止清洁',
        'pause': '暂停清洁',
        'resume': '恢复清洁',
        'return_to_base': '返回基站'
    }
    
    if action not in supported_actions:
        return jsonify({
            "status": "error",
            "message": f"不支持的操作: {action}"
        }), 400
    
    # 异步发送命令
    success = await matter_client.send_command(action, params)
    
    if success:
        return jsonify({
            "status": "success",
            "message": f"{supported_actions[action]}命令已发送"
        })
    else:
        return jsonify({
            "status": "error",
            "message": "命令发送失败，请检查设备连接状态"
        }), 500

@api.route('/config', methods=['GET'])
def get_config():
    """获取配置信息"""
    return jsonify({
        "status": "success",
        "data": {
            "matter_server_url": current_app.config['MATTER_SERVER_WS_URL']
        }
    })

@api.route('/config', methods=['POST'])
def update_config():
    """更新配置信息"""
    data = request.json
    
    if not data:
        return jsonify({
            "status": "error",
            "message": "缺少必要参数"
        }), 400
    
    # 更新Matter Server WebSocket URL
    if 'matter_server_url' in data:
        current_app.config['MATTER_SERVER_WS_URL'] = data['matter_server_url']
        
        # 重新连接Matter Server
        asyncio.create_task(current_app.reconnect_matter_server())
        
        return jsonify({
            "status": "success",
            "message": "配置已更新，正在重新连接Matter Server"
        })
    
    return jsonify({
        "status": "error",
        "message": "没有可更新的配置项"
    }), 400 