"""
API路由
定义控制设备的HTTP接口
"""

from flask import Blueprint, jsonify, request, current_app
import asyncio
import logging

# 配置日志
logger = logging.getLogger(__name__)

api = Blueprint('api', __name__)

@api.route('/status', methods=['GET'])
def get_status():
    """获取设备状态"""
    matter_client = current_app.matter_client
    status = matter_client.get_device_status()
    
    # 添加设备基本信息
    device_info = current_app.config.get('DEVICE_INFO', {
        "product_name": "未知",
        "manufacturer": "未知",
        "hardware_version": "未知",
        "software_version": "未知",
        "serial_number": "未知",
        "matter_version": "未知",
        "ip_address": request.host
    })
    
    return jsonify({
        "status": "success",
        "data": {
            "device_info": device_info,
            "device_status": status
        }
    })

@api.route('/nodes', methods=['GET'])
def get_all_nodes():
    """获取所有节点信息"""
    matter_client = current_app.matter_client
    nodes = matter_client.get_all_nodes()
    
    # 提取节点基本信息
    nodes_info = []
    for node_id, node_data in nodes.items():
        nodes_info.append({
            "node_id": node_data.get("node_id"),
            "available": node_data.get("available", False),
            "date_commissioned": node_data.get("date_commissioned", ""),
            "last_interview": node_data.get("last_interview", "")
        })
    
    return jsonify({
        "status": "success",
        "data": {
            "nodes": nodes_info
        }
    })

@api.route('/node/<node_id>', methods=['GET'])
def get_node_status(node_id):
    """获取指定节点的设备状态
    
    Args:
        node_id: Matter节点ID
    """
    matter_client = current_app.matter_client
    
    # 获取节点信息
    node_info = matter_client.get_node_info(node_id)
    
    if not node_info:
        return jsonify({
            "status": "error",
            "message": f"节点 {node_id} 不存在"
        }), 404
    
    # 从节点属性中提取信息
    attributes = node_info.get("attributes", {})
    
    # 记录完整的属性数据，便于调试
    logger.info("节点 %s 的属性数据: %s", node_id, attributes)
    
    # 使用正确的属性路径提取信息
    # VendorName: 0/40/1
    # ProductName: 0/40/3
    # HardwareVersionString: 0/40/8
    # SoftwareVersionString: 0/40/10
    # SerialNumber: 0/40/15
    # SpecificationVersion: 0/40/21
    manufacturer = extract_attribute(attributes, "0/40/1", "未知厂商")
    product_name = extract_attribute(attributes, "0/40/3", "未知产品")
    hardware_version = extract_attribute(attributes, "0/40/8", "未知")
    software_version = extract_attribute(attributes, "0/40/10", "未知")
    serial_number = extract_attribute(attributes, "0/40/15", "未知")
    matter_version = extract_attribute(attributes, "0/40/21", "未知")
    
    # 添加设备基本信息
    device_info = {
        "product_name": product_name,
        "manufacturer": manufacturer,
        "hardware_version": hardware_version,
        "software_version": software_version,
        "serial_number": serial_number,
        "matter_version": matter_version,
        "ip_address": "未知",
        "node_id": node_id,
        "available": node_info.get("available", False),
        "date_commissioned": node_info.get("date_commissioned", ""),
        "last_interview": node_info.get("last_interview", "")
    }
    
    # 获取设备状态
    # 如果节点可用，使用节点特定状态，否则使用默认状态
    if node_info.get("available", False):
        status = matter_client.get_device_status()
    else:
        status = {
            "cleaning_mode": "未知",
            "operation_status": "离线",
            "battery_level": 0
        }
    
    return jsonify({
        "status": "success",
        "data": {
            "device_info": device_info,
            "device_status": status
        }
    })

def extract_attribute(attributes, path, default_value):
    """从属性中提取指定路径的值
    
    Args:
        attributes: 属性字典
        path: 属性路径，例如 "0/40/1"
        default_value: 默认值，如果属性不存在则返回此值
        
    Returns:
        提取的属性值或默认值
    """
    try:
        if path in attributes:
            value = attributes[path]
            logger.debug("从路径 %s 提取属性值: %s", path, value)
            return value
    except Exception as e:
        logger.error("提取属性 %s 时出错: %s", path, str(e))
    
    return default_value

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