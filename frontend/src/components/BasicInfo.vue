<template>
  <div class="basic-info">
    <el-card class="info-card">
      <template #header>
        <div class="card-header">
          <h2>基础信息</h2>
          <el-button type="primary" size="small" @click="refreshInfo">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>
      <div class="info-content">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="产品名称">{{ deviceInfo.product_name }}</el-descriptions-item>
          <el-descriptions-item label="硬件版本">{{ deviceInfo.hardware_version }}</el-descriptions-item>
          <el-descriptions-item label="软件版本">{{ deviceInfo.software_version }}</el-descriptions-item>
          <el-descriptions-item label="IP地址">{{ deviceInfo.ip_address }}</el-descriptions-item>
          <el-descriptions-item label="连接状态">
            <el-tag :type="connectionStatus.type">{{ connectionStatus.text }}</el-tag>
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-card>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { Refresh } from '@element-plus/icons-vue';
import api from '../services/api';

export default {
  name: 'BasicInfo',
  components: {
    Refresh
  },
  props: {
    connected: {
      type: Boolean,
      default: false
    }
  },
  emits: ['refresh'],
  setup(props, { emit }) {
    const deviceInfo = ref({
      product_name: '加载中...',
      hardware_version: '加载中...',
      software_version: '加载中...',
      ip_address: '加载中...'
    });
    
    const loading = ref(false);
    
    const connectionStatus = computed(() => {
      return props.connected 
        ? { text: '已连接', type: 'success' } 
        : { text: '未连接', type: 'danger' };
    });
    
    const fetchDeviceInfo = async () => {
      loading.value = true;
      try {
        const response = await api.getStatus();
        if (response.status === 'success' && response.data.device_info) {
          deviceInfo.value = response.data.device_info;
        }
      } catch (error) {
        console.error('获取设备信息失败:', error);
      } finally {
        loading.value = false;
      }
    };
    
    const refreshInfo = () => {
      fetchDeviceInfo();
      emit('refresh');
    };
    
    onMounted(() => {
      fetchDeviceInfo();
    });
    
    return {
      deviceInfo,
      loading,
      connectionStatus,
      refreshInfo
    };
  }
}
</script>

<style scoped>
.basic-info {
  margin-bottom: 20px;
}

.info-card {
  width: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  margin: 0;
  font-size: 18px;
}

.info-content {
  margin-top: 10px;
}
</style> 