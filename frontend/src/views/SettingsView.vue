<template>
  <div class="settings">
    <el-card class="settings-card">
      <template #header>
        <div class="card-header">
          <h2>系统设置</h2>
        </div>
      </template>
      
      <el-form :model="form" label-width="180px" :rules="rules" ref="formRef">
        <el-form-item label="Matter Server地址" prop="matter_server_url">
          <el-input 
            v-model="form.matter_server_url" 
            placeholder="例如: ws://192.168.2.21:5580/ws"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="saveSettings" :loading="loading">
            保存设置
          </el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
      
      <el-divider content-position="center">连接状态</el-divider>
      
      <div class="connection-status">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="Matter Server">
            <el-tag :type="connected ? 'success' : 'danger'">
              {{ connected ? '已连接' : '未连接' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="当前地址">
            {{ currentConfig.matter_server_url || '未设置' }}
          </el-descriptions-item>
        </el-descriptions>
        
        <div class="connection-actions">
          <el-button type="primary" @click="testConnection" :loading="testingConnection">
            测试连接
          </el-button>
          <el-button type="warning" @click="reconnect" :loading="reconnecting">
            重新连接
          </el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import api from '@/services/api';
import websocketService from '@/services/websocket';

export default {
  name: 'SettingsView',
  setup() {
    const formRef = ref(null);
    const loading = ref(false);
    const testingConnection = ref(false);
    const reconnecting = ref(false);
    const connected = ref(false);
    
    const currentConfig = ref({
      matter_server_url: ''
    });
    
    const form = reactive({
      matter_server_url: ''
    });
    
    const rules = {
      matter_server_url: [
        { required: true, message: '请输入Matter Server地址', trigger: 'blur' },
        { pattern: /^ws:\/\/.*:\d+\/.*$/, message: '格式应为 ws://主机:端口/路径', trigger: 'blur' }
      ]
    };
    
    // 获取当前配置
    const fetchConfig = async () => {
      try {
        const response = await api.getConfig();
        if (response.status === 'success' && response.data) {
          currentConfig.value = response.data;
          form.matter_server_url = response.data.matter_server_url;
          
          // 检查连接状态
          checkConnectionStatus();
        }
      } catch (error) {
        console.error('获取配置失败:', error);
        ElMessage.error('获取配置失败，请检查网络连接');
      }
    };
    
    // 保存设置
    const saveSettings = async () => {
      if (!formRef.value) return;
      
      await formRef.value.validate(async (valid) => {
        if (valid) {
          loading.value = true;
          try {
            const response = await api.updateConfig({
              matter_server_url: form.matter_server_url
            });
            
            if (response.status === 'success') {
              ElMessage.success('设置已保存');
              await fetchConfig();
              
              // 更新WebSocket URL
              websocketService.setWsUrl(form.matter_server_url);
            } else {
              ElMessage.error(response.message || '保存设置失败');
            }
          } catch (error) {
            console.error('保存设置失败:', error);
            ElMessage.error('保存设置失败，请检查网络连接');
          } finally {
            loading.value = false;
          }
        }
      });
    };
    
    // 重置表单
    const resetForm = () => {
      if (formRef.value) {
        formRef.value.resetFields();
        form.matter_server_url = currentConfig.value.matter_server_url;
      }
    };
    
    // 测试连接
    const testConnection = async () => {
      testingConnection.value = true;
      try {
        const response = await api.getStatus();
        if (response.status === 'success') {
          ElMessage.success('连接成功');
          connected.value = true;
        } else {
          ElMessage.error('连接失败');
          connected.value = false;
        }
      } catch (error) {
        console.error('测试连接失败:', error);
        ElMessage.error('连接失败，请检查网络和服务器状态');
        connected.value = false;
      } finally {
        testingConnection.value = false;
      }
    };
    
    // 重新连接
    const reconnect = async () => {
      reconnecting.value = true;
      try {
        const response = await api.updateConfig({
          matter_server_url: currentConfig.value.matter_server_url
        });
        
        if (response.status === 'success') {
          ElMessage.success('正在重新连接...');
          setTimeout(() => {
            testConnection();
          }, 2000);
        } else {
          ElMessage.error(response.message || '重新连接失败');
        }
      } catch (error) {
        console.error('重新连接失败:', error);
        ElMessage.error('重新连接失败，请检查网络连接');
      } finally {
        reconnecting.value = false;
      }
    };
    
    // 检查连接状态
    const checkConnectionStatus = async () => {
      try {
        const response = await api.getStatus();
        connected.value = response.status === 'success';
      } catch (error) {
        connected.value = false;
      }
    };
    
    onMounted(() => {
      fetchConfig();
    });
    
    return {
      formRef,
      form,
      rules,
      loading,
      testingConnection,
      reconnecting,
      connected,
      currentConfig,
      saveSettings,
      resetForm,
      testConnection,
      reconnect
    };
  }
}
</script>

<style scoped>
.settings {
  max-width: 800px;
  margin: 0 auto;
}

.settings-card {
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

.connection-status {
  margin-top: 20px;
}

.connection-actions {
  margin-top: 20px;
  display: flex;
  justify-content: center;
  gap: 20px;
}
</style> 