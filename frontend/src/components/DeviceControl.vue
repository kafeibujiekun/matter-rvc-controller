<template>
  <div class="device-control">
    <el-card class="control-card">
      <template #header>
        <div class="card-header">
          <h2>设备状态与控制</h2>
        </div>
      </template>
      
      <div class="status-section">
        <el-row :gutter="20">
          <el-col :span="8">
            <div class="status-item">
              <h3>清洁模式</h3>
              <el-tag size="large">{{ deviceStatus.cleaning_mode }}</el-tag>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="status-item">
              <h3>操作状态</h3>
              <el-tag :type="getStatusType(deviceStatus.operation_status)" size="large">
                {{ deviceStatus.operation_status }}
              </el-tag>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="status-item">
              <h3>电量</h3>
              <el-progress 
                :percentage="deviceStatus.battery_level" 
                :status="getBatteryStatus(deviceStatus.battery_level)"
                :stroke-width="18"
              />
            </div>
          </el-col>
        </el-row>
      </div>
      
      <div class="control-section">
        <el-divider content-position="center">控制按钮</el-divider>
        <el-row :gutter="20" justify="center">
          <el-col :span="4">
            <el-button 
              type="primary" 
              :icon="VideoPlay"
              :disabled="!connected || isRunning"
              @click="controlDevice('start')"
              round
            >
              开始
            </el-button>
          </el-col>
          <el-col :span="4">
            <el-button 
              type="danger" 
              :icon="VideoPause"
              :disabled="!connected || !isRunning"
              @click="controlDevice('pause')"
              round
            >
              暂停
            </el-button>
          </el-col>
          <el-col :span="4">
            <el-button 
              type="success" 
              :icon="VideoPlay"
              :disabled="!connected || !isPaused"
              @click="controlDevice('resume')"
              round
            >
              恢复
            </el-button>
          </el-col>
          <el-col :span="4">
            <el-button 
              type="warning" 
              :icon="CircleClose"
              :disabled="!connected || !isActive"
              @click="controlDevice('stop')"
              round
            >
              结束
            </el-button>
          </el-col>
          <el-col :span="4">
            <el-button 
              type="info" 
              :icon="House"
              :disabled="!connected || !isActive"
              @click="controlDevice('return_to_base')"
              round
            >
              返回基站
            </el-button>
          </el-col>
        </el-row>
      </div>
    </el-card>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue';
import { VideoPlay, VideoPause, CircleClose, House } from '@element-plus/icons-vue';
import { ElMessage } from 'element-plus';
import api from '../services/api';

export default {
  name: 'DeviceControl',
  components: {
    VideoPlay,
    VideoPause,
    CircleClose,
    House
  },
  props: {
    connected: {
      type: Boolean,
      default: false
    },
    status: {
      type: Object,
      default: () => ({
        cleaning_mode: '未知',
        operation_status: '离线',
        battery_level: 0
      })
    }
  },
  setup(props) {
    const deviceStatus = ref({
      cleaning_mode: '未知',
      operation_status: '离线',
      battery_level: 0
    });
    
    const loading = ref(false);
    
    // 监听状态变化
    watch(() => props.status, (newStatus) => {
      if (newStatus) {
        deviceStatus.value = newStatus;
      }
    }, { immediate: true, deep: true });
    
    // 计算设备是否正在运行
    const isRunning = computed(() => {
      return deviceStatus.value.operation_status === '清洁中';
    });
    
    // 计算设备是否暂停
    const isPaused = computed(() => {
      return deviceStatus.value.operation_status === '已暂停';
    });
    
    // 计算设备是否处于活动状态（运行中或暂停）
    const isActive = computed(() => {
      return isRunning.value || isPaused.value;
    });
    
    // 获取状态标签类型
    const getStatusType = (status) => {
      const statusMap = {
        '清洁中': 'success',
        '已暂停': 'warning',
        '已停止': 'info',
        '返回基站中': 'primary',
        '离线': 'danger',
        '错误': 'danger'
      };
      return statusMap[status] || 'info';
    };
    
    // 获取电池状态
    const getBatteryStatus = (level) => {
      if (level <= 20) return 'exception';
      if (level <= 50) return 'warning';
      return 'success';
    };
    
    // 控制设备
    const controlDevice = async (action) => {
      loading.value = true;
      try {
        const response = await api.controlDevice(action);
        if (response.status === 'success') {
          ElMessage.success(response.message || '命令已发送');
        } else {
          ElMessage.error(response.message || '命令发送失败');
        }
      } catch (error) {
        console.error('控制设备失败:', error);
        ElMessage.error('控制设备失败，请检查网络连接');
      } finally {
        loading.value = false;
      }
    };
    
    return {
      deviceStatus,
      loading,
      isRunning,
      isPaused,
      isActive,
      getStatusType,
      getBatteryStatus,
      controlDevice,
      VideoPlay,
      VideoPause,
      CircleClose,
      House
    };
  }
}
</script>

<style scoped>
.device-control {
  margin-bottom: 20px;
}

.control-card {
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

.status-section {
  margin-bottom: 20px;
}

.status-item {
  text-align: center;
  padding: 10px;
}

.status-item h3 {
  margin-top: 0;
  margin-bottom: 10px;
  font-size: 16px;
  color: #606266;
}

.control-section {
  margin-top: 20px;
}

.el-button {
  width: 100%;
  margin-bottom: 10px;
}
</style> 