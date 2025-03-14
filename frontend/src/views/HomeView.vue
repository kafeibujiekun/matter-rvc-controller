<template>
  <div class="home">
    <BasicInfo :connected="connected" @refresh="refreshData" @node-loaded="handleNodeLoaded" />
    <DeviceControl :connected="connected" :status="deviceStatus" />
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue';
import BasicInfo from '@/components/BasicInfo.vue';
import DeviceControl from '@/components/DeviceControl.vue';
import api from '@/services/api';
import websocketService from '@/services/websocket';

export default {
  name: 'HomeView',
  components: {
    BasicInfo,
    DeviceControl
  },
  setup() {
    const connected = ref(false);
    const deviceStatus = ref({
      cleaning_mode: '未知',
      operation_status: '离线',
      battery_level: 0
    });
    
    // 处理设备状态更新
    const handleStatusUpdate = (status) => {
      deviceStatus.value = status;
      connected.value = true;
    };
    
    // 处理节点加载事件
    const handleNodeLoaded = (status) => {
      if (status) {
        deviceStatus.value = status;
        connected.value = true;
      }
    };
    
    // 刷新数据
    const refreshData = async () => {
      try {
        const response = await api.getStatus();
        if (response.status === 'success' && response.data.device_status) {
          deviceStatus.value = response.data.device_status;
          connected.value = true;
        }
      } catch (error) {
        console.error('获取设备状态失败:', error);
        connected.value = false;
      }
    };
    
    onMounted(() => {
      // 注册WebSocket状态监听器
      websocketService.addStatusListener(handleStatusUpdate);
      
      // 连接WebSocket
      websocketService.connect();
      
      // 初始获取设备状态
      refreshData();
    });
    
    onUnmounted(() => {
      // 移除WebSocket状态监听器
      websocketService.removeStatusListener(handleStatusUpdate);
    });
    
    return {
      connected,
      deviceStatus,
      refreshData,
      handleNodeLoaded
    };
  }
}
</script>

<style scoped>
.home {
  max-width: 1200px;
  margin: 0 auto;
}
</style> 