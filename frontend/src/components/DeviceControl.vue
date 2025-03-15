<template>
  <div class="device-control">
    <el-card class="control-card">
      <template #header>
        <div class="card-header">
          <h2>设备状态与控制</h2>
        </div>
      </template>
      
      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="3" animated />
      </div>
      
      <template v-else>
        <div class="status-section">
          <el-row :gutter="20">
            <el-col :span="6">
              <div class="status-item">
                <h3>运行模式</h3>
                <el-tag size="large">{{ getRunModeText(deviceStatus.current_run_mode) }}</el-tag>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="status-item">
                <h3>清洁模式</h3>
                <el-select 
                  v-model="selectedCleaningMode" 
                  placeholder="选择清洁模式"
                  size="large"
                  style="width: 100%;"
                  @change="handleCleaningModeChange"
                >
                  <el-option
                    v-for="mode in cleaningModeOptions"
                    :key="mode.value"
                    :label="mode.label"
                    :value="mode.value"
                  />
                </el-select>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="status-item">
                <h3>操作状态</h3>
                <el-select 
                  v-model="deviceStatus.operational_state" 
                  placeholder="操作状态"
                  size="large"
                  style="width: 100%;"
                  :popper-append-to-body="false"
                  @change="handleOperationalStateChange"
                >
                  <el-option
                    v-for="item in deviceStatus.operational_state_list"
                    :key="item.id"
                    :label="`${item.name} (${item.id})`"
                    :value="item.id"
                    :disabled="true"
                  />
                  <el-option
                    v-if="!deviceStatus.operational_state_list || deviceStatus.operational_state_list.length === 0 || !deviceStatus.operational_state_list.some(item => item.id === deviceStatus.operational_state)"
                    :label="getOperationStateText(deviceStatus.operational_state)"
                    :value="deviceStatus.operational_state"
                    :disabled="true"
                  />
                </el-select>
              </div>
            </el-col>
            <el-col :span="6">
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
          <el-divider></el-divider>
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
      </template>
    </el-card>
  </div>
</template>

<script>
import { ref, computed, watch, onMounted } from 'vue';
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
    nodeId: {
      type: String,
      default: ''
    }
  },
  setup(props) {
    const deviceStatus = ref({
      current_run_mode: 0,
      current_cleaning_mode: 0,
      operational_state: 0,
      operational_state_list: [],
      battery_level: 0,
      supported_run_modes: [],
      supported_cleaning_modes: []
    });
    
    const selectedCleaningMode = ref(0);
    const loading = ref(false);
    const nodeLoaded = ref(false);
    
    // 计算清洁模式选项
    const cleaningModeOptions = computed(() => {
      if (!deviceStatus.value.supported_cleaning_modes || deviceStatus.value.supported_cleaning_modes.length === 0) {
        // 默认选项
        return [
          { value: 0, label: 'Quick (0)' },
          { value: 1, label: 'Auto (1)' },
          { value: 2, label: 'Deep Clean (2)' },
          { value: 3, label: 'Quiet (3)' },
          { value: 4, label: 'Max Vac (4)' }
        ];
      }
      
      // 从支持的清洁模式列表生成选项
      return deviceStatus.value.supported_cleaning_modes.map(mode => {
        return {
          value: mode["1"],
          label: `${mode["0"]} (${mode["1"]})`
        };
      });
    });
    
    // 监听设备状态变化，更新选中的清洁模式
    watch(() => deviceStatus.value.current_cleaning_mode, (newMode) => {
      selectedCleaningMode.value = newMode;
    });
    
    // 处理清洁模式变更
    const handleCleaningModeChange = (value) => {
      // 发送设置清洁模式命令
      controlDevice('set_mode', { mode: value });
    };
    
    // 计算设备是否正在运行
    const isRunning = computed(() => {
      return deviceStatus.value.operational_state === 1; // 1表示清洁中
    });
    
    // 计算设备是否暂停
    const isPaused = computed(() => {
      return deviceStatus.value.operational_state === 2; // 2表示暂停
    });
    
    // 计算设备是否处于活动状态（运行中或暂停）
    const isActive = computed(() => {
      return isRunning.value || isPaused.value;
    });
    
    // 获取运行模式文本
    const getRunModeText = (mode) => {
      if (mode === undefined || mode === null) return '未知';
      
      // 从支持的运行模式列表中查找
      if (deviceStatus.value.supported_run_modes && deviceStatus.value.supported_run_modes.length > 0) {
        const modeObj = deviceStatus.value.supported_run_modes.find(m => m["1"] === mode);
        if (modeObj && modeObj["0"]) {
          return modeObj["0"];
        }
      }
      
      // 默认映射（备用）
      const modeMap = {
        0: 'Idle',
        1: 'Cleaning',
        2: 'Mapping'
      };
      
      return modeMap[mode] || `模式${mode}`;
    };
    
    // 获取清洁模式文本
    const getCleaningModeText = (mode) => {
      if (mode === undefined || mode === null) return '未知';
      
      // 从支持的清洁模式列表中查找
      if (deviceStatus.value.supported_cleaning_modes && deviceStatus.value.supported_cleaning_modes.length > 0) {
        const modeObj = deviceStatus.value.supported_cleaning_modes.find(m => m["1"] === mode);
        if (modeObj && modeObj["0"]) {
          return modeObj["0"];
        }
      }
      
      // 默认映射（备用）
      const modeMap = {
        0: 'Quick',
        1: 'Auto',
        2: 'Deep Clean',
        3: 'Quiet',
        4: 'Max Vac'
      };
      
      return modeMap[mode] || `模式${mode}`;
    };
    
    // 获取操作状态文本
    const getOperationStateText = (state) => {
      if (state === undefined || state === null) return '未知';
      
      // 默认映射
      const stateMap = {
        0: '待机',
        1: '清洁中',
        2: '暂停',
        3: '故障',
        4: '关机',
        64: '寻找充电座', // 0x40 SeekingCharger
        65: '充电中',     // 0x41 Charging
        66: '已对接'      // 0x42 Docked
      };
      
      return stateMap[state] || `状态${state}`;
    };
    
    // 获取状态标签类型
    const getStatusType = (status) => {
      const statusMap = {
        0: 'info',    // 待机
        1: 'success', // 清洁中
        2: 'warning', // 暂停
        3: 'danger',  // 故障
        4: 'info',    // 关机
        64: 'warning', // 寻找充电座
        65: 'success', // 充电中
        66: 'info'     // 已对接
      };
      return statusMap[status] || 'info';
    };
    
    // 处理操作状态变更（防止用户选择）
    const handleOperationalStateChange = (value) => {
      // 不做任何操作，保持原值不变
      // 由于选项都设置了disabled，这个函数实际上不会被调用
    };
    
    // 获取电池状态
    const getBatteryStatus = (level) => {
      if (level <= 20) return 'exception';
      if (level <= 50) return 'warning';
      return 'success';
    };
    
    // 控制设备
    const controlDevice = async (action, params = {}) => {
      if (!props.nodeId) {
        ElMessage.warning('请先选择一个设备节点');
        return;
      }
      
      loading.value = true;
      try {
        // 添加节点ID到参数中
        const controlParams = {
          ...params,
          node_id: props.nodeId
        };
        
        const response = await api.controlDevice(action, controlParams);
        if (response.status === 'success') {
          ElMessage.success(response.message || '命令已发送');
          
          // 更新设备状态
          if (action === 'start') {
            deviceStatus.value.operational_state = 1; // 清洁中
            deviceStatus.value.current_run_mode = 1; // Cleaning
          } else if (action === 'pause') {
            deviceStatus.value.operational_state = 2; // 暂停
          } else if (action === 'resume') {
            deviceStatus.value.operational_state = 1; // 清洁中
            deviceStatus.value.current_run_mode = 1; // Cleaning
          } else if (action === 'stop') {
            deviceStatus.value.operational_state = 0; // 待机
            deviceStatus.value.current_run_mode = 0; // Idle
          } else if (action === 'set_mode') {
            deviceStatus.value.current_cleaning_mode = params.mode;
          }
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
    
    // 加载节点状态
    const loadNodeStatus = (nodeId) => {
      if (!nodeId) {
        console.log('未提供节点ID，无法加载设备状态');
        return;
      }
      
      loading.value = true;
      api.getNodeStatus(nodeId).then(response => {
        if (response.status === 'success' && response.data) {
          // 更新设备状态
          if (response.data.device_status) {
            deviceStatus.value = response.data.device_status;
            selectedCleaningMode.value = deviceStatus.value.current_cleaning_mode;
            console.log('设备状态:', JSON.stringify(deviceStatus.value, null, 2));
            nodeLoaded.value = true;
          }
          
          // 打印设备基础信息
          if (response.data.device_info) {
            console.log('设备基础信息:', JSON.stringify(response.data.device_info, null, 2));
          }
        }
      }).catch(error => {
        console.error('获取设备状态失败:', error);
      }).finally(() => {
        loading.value = false;
      });
    };
    
    // 监听nodeId变化
    watch(() => props.nodeId, (newNodeId) => {
      if (newNodeId) {
        loadNodeStatus(newNodeId);
      } else {
        // 重置设备状态
        deviceStatus.value = {
          current_run_mode: 0,
          current_cleaning_mode: 0,
          operational_state: 0,
          operational_state_list: [],
          battery_level: 0,
          supported_run_modes: [],
          supported_cleaning_modes: []
        };
        nodeLoaded.value = false;
      }
    }, { immediate: true });
    
    return {
      deviceStatus,
      selectedCleaningMode,
      cleaningModeOptions,
      loading,
      nodeLoaded,
      isRunning,
      isPaused,
      isActive,
      getRunModeText,
      getCleaningModeText,
      getOperationStateText,
      getStatusType,
      getBatteryStatus,
      controlDevice,
      handleCleaningModeChange,
      handleOperationalStateChange,
      loadNodeStatus,
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

.state-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.no-node-selected {
  padding: 40px 0;
  text-align: center;
}

.loading-container {
  padding: 20px;
}
</style> 