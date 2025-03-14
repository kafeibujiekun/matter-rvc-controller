<template>
  <div class="basic-info">
    <el-card class="info-card">
      <template #header>
        <div class="card-header">
          <h2>基础信息</h2>
          <div class="header-actions">
            <div class="node-input-group">
              <el-select 
                v-model="nodeId" 
                placeholder="选择Node ID" 
                size="small"
                :loading="nodesLoading"
                filterable
                clearable
                style="width: 150px;"
              >
                <el-option
                  v-for="node in availableNodes"
                  :key="node.node_id"
                  :label="`节点 ${node.node_id} ${node.available ? '(在线)' : '(离线)'}`"
                  :value="node.node_id.toString()"
                />
              </el-select>
              <el-button 
                type="primary" 
                size="small" 
                @click="loadNodeInfo" 
                :loading="loading"
              >
                加载
              </el-button>
            </div>
            <el-button type="primary" size="small" @click="refreshInfo" :loading="loading">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </div>
      </template>
      <div class="info-content">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="Node ID">{{ deviceInfo.node_id || '未知' }}</el-descriptions-item>
          <el-descriptions-item label="产品名称">{{ deviceInfo.product_name || '未知' }}</el-descriptions-item>
          <el-descriptions-item label="厂商名称">{{ deviceInfo.manufacturer || '未知' }}</el-descriptions-item>
          <el-descriptions-item label="硬件版本">{{ deviceInfo.hardware_version || '未知' }}</el-descriptions-item>
          <el-descriptions-item label="软件版本">{{ deviceInfo.software_version || '未知' }}</el-descriptions-item>
          <el-descriptions-item label="SN码">{{ deviceInfo.serial_number || '未知' }}</el-descriptions-item>
          <el-descriptions-item label="Matter协议版本">{{ deviceInfo.matter_version || '未知' }}</el-descriptions-item>
          <el-descriptions-item label="IP地址">{{ deviceInfo.ip_address || '未知' }}</el-descriptions-item>
          <el-descriptions-item label="节点状态">
            <el-tag :type="deviceInfo.available ? 'success' : 'danger'">
              {{ deviceInfo.available ? '在线' : '离线' }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-card>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { Refresh } from '@element-plus/icons-vue';
import { ElMessage } from 'element-plus';
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
  emits: ['refresh', 'node-loaded'],
  setup(props, { emit }) {
    const nodeId = ref('');
    const deviceInfo = ref({
      product_name: '',
      manufacturer: '',
      hardware_version: '',
      software_version: '',
      serial_number: '',
      matter_version: '',
      ip_address: '',
      node_id: '',
      available: false
    });
    
    const loading = ref(false);
    const nodesLoading = ref(false);
    const availableNodes = ref([]);
    
    const connectionStatus = computed(() => {
      return props.connected 
        ? { text: '已连接', type: 'success' } 
        : { text: '未连接', type: 'danger' };
    });
    
    const resetDeviceInfo = () => {
      deviceInfo.value = {
        product_name: '',
        manufacturer: '',
        hardware_version: '',
        software_version: '',
        serial_number: '',
        matter_version: '',
        ip_address: '',
        node_id: '',
        available: false
      };
    };
    
    const fetchDeviceInfo = async () => {
      loading.value = true;
      try {
        const response = await api.getStatus();
        if (response.status === 'success' && response.data.device_info) {
          deviceInfo.value = response.data.device_info;
        }
      } catch (error) {
        console.error('获取设备信息失败:', error);
        resetDeviceInfo();
      } finally {
        loading.value = false;
      }
    };
    
    const fetchNodes = async () => {
      nodesLoading.value = true;
      try {
        const response = await api.getAllNodes();
        if (response.status === 'success' && response.data.nodes) {
          availableNodes.value = response.data.nodes;
        }
      } catch (error) {
        console.error('获取节点列表失败:', error);
        ElMessage.error('获取节点列表失败');
      } finally {
        nodesLoading.value = false;
      }
    };
    
    const loadNodeInfo = async () => {
      if (!nodeId.value) {
        ElMessage.warning('请选择Node ID');
        return;
      }
      
      loading.value = true;
      try {
        const response = await api.getNodeStatus(nodeId.value);
        if (response.status === 'success' && response.data) {
          deviceInfo.value = response.data.device_info;
          emit('node-loaded', response.data.device_status);
          ElMessage.success(`成功加载节点 ${nodeId.value} 的信息`);
        }
      } catch (error) {
        console.error('获取节点信息失败:', error);
        ElMessage.error(`获取节点 ${nodeId.value} 信息失败`);
        resetDeviceInfo();
      } finally {
        loading.value = false;
      }
    };
    
    const refreshInfo = () => {
      if (nodeId.value) {
        loadNodeInfo();
      } else {
        resetDeviceInfo();
        fetchDeviceInfo();
      }
      fetchNodes();
      emit('refresh');
    };
    
    onMounted(() => {
      resetDeviceInfo();
      fetchNodes();
    });
    
    return {
      nodeId,
      deviceInfo,
      loading,
      nodesLoading,
      availableNodes,
      connectionStatus,
      refreshInfo,
      loadNodeInfo
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

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.node-input-group {
  display: flex;
  align-items: center;
  gap: 5px;
}

.info-content {
  margin-top: 10px;
}
</style> 