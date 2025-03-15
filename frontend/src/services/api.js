import axios from 'axios';

// 创建axios实例
const api = axios.create({
  baseURL: process.env.VUE_APP_API_URL || '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// 请求拦截器
api.interceptors.request.use(
  config => {
    // 在发送请求之前做些什么
    return config;
  },
  error => {
    // 对请求错误做些什么
    console.error('请求错误:', error);
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  response => {
    // 对响应数据做点什么
    return response.data;
  },
  error => {
    // 对响应错误做点什么
    console.error('响应错误:', error);
    return Promise.reject(error);
  }
);

// API方法
export default {
  // 获取设备状态
  getStatus() {
    return api.get('/status');
  },
  
  // 获取所有节点信息
  getAllNodes() {
    return api.get('/nodes');
  },
  
  // 获取指定节点的设备状态
  getNodeStatus(nodeId) {
    return api.get(`/node/${nodeId}`);
  },
  
  // 控制设备
  controlDevice(action, params = {}) {
    return api.post('/control', {
      action,
      params
    });
  },
  
  // 获取配置
  getConfig() {
    return api.get('/config');
  },
  
  // 更新配置
  updateConfig(config) {
    return api.post('/config', config);
  }
}; 