/**
 * WebSocket服务
 * 用于接收设备状态更新
 */

class WebSocketService {
  constructor() {
    this.socket = null;
    this.isConnected = false;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectInterval = 3000; // 3秒
    this.statusListeners = [];
    
    // 优先使用环境变量中的WebSocket URL，如果没有则使用基于当前主机的URL
    this.wsUrl = process.env.VUE_APP_WS_URL || this.getDefaultWsUrl();
    console.log('初始化WebSocket服务，URL:', this.wsUrl);
  }

  /**
   * 获取默认的WebSocket URL
   * @returns {string} 默认的WebSocket URL
   */
  getDefaultWsUrl() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.hostname;
    return `${protocol}//${host}:5005`;
  }

  /**
   * 连接WebSocket服务器
   */
  connect() {
    if (this.socket && this.isConnected) {
      console.log('WebSocket已连接');
      return;
    }
    
    // 使用完整的WebSocket URL
    const fullUrl = this.wsUrl;
    
    console.log(`正在连接WebSocket: ${fullUrl}`);
    
    try {
      this.socket = new WebSocket(fullUrl);

      this.socket.onopen = () => {
        console.log('WebSocket连接成功');
        this.isConnected = true;
        this.reconnectAttempts = 0;
      };

      this.socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.handleMessage(data);
        } catch (error) {
          console.error('解析WebSocket消息失败:', error);
        }
      };

      this.socket.onclose = () => {
        console.log('WebSocket连接关闭');
        this.isConnected = false;
        this.attemptReconnect();
      };

      this.socket.onerror = (error) => {
        console.error('WebSocket错误:', error);
        this.isConnected = false;
        this.attemptReconnect();
      };
    } catch (error) {
      console.error('创建WebSocket连接失败:', error);
      this.attemptReconnect();
    }
  }

  /**
   * 断开WebSocket连接
   */
  disconnect() {
    if (this.socket) {
      this.socket.close();
      this.isConnected = false;
      console.log('WebSocket连接已断开');
    }
  }

  /**
   * 尝试重新连接
   */
  attemptReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.log('达到最大重连次数，停止重连');
      return;
    }

    this.reconnectAttempts++;
    console.log(`尝试重新连接 (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
    
    setTimeout(() => {
      this.connect();
    }, this.reconnectInterval);
  }

  /**
   * 处理接收到的消息
   * @param {Object} data 消息数据
   */
  handleMessage(data) {
    if (data.type === 'status_update') {
      // 通知所有状态监听器
      this.statusListeners.forEach(listener => {
        listener(data.data);
      });
    }
  }

  /**
   * 添加状态更新监听器
   * @param {Function} listener 监听器函数
   */
  addStatusListener(listener) {
    if (typeof listener === 'function' && !this.statusListeners.includes(listener)) {
      this.statusListeners.push(listener);
    }
  }

  /**
   * 移除状态更新监听器
   * @param {Function} listener 监听器函数
   */
  removeStatusListener(listener) {
    const index = this.statusListeners.indexOf(listener);
    if (index !== -1) {
      this.statusListeners.splice(index, 1);
    }
  }

  /**
   * 设置WebSocket URL
   * @param {string} url WebSocket URL
   */
  setWsUrl(url) {
    if (url && url !== this.wsUrl) {
      this.wsUrl = url;
      // 如果已连接，断开当前连接并重新连接
      if (this.isConnected) {
        this.disconnect();
        this.connect();
      }
    }
  }
}

// 创建单例
const websocketService = new WebSocketService();

export default websocketService; 