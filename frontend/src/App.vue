<template>
  <div class="app-container">
    <el-container>
      <el-header>
        <div class="header-content">
          <h1>RVC控制端</h1>
          <el-menu mode="horizontal" :router="true" :default-active="activeRoute">
            <el-menu-item index="/">控制面板</el-menu-item>
            <el-menu-item index="/settings">设置</el-menu-item>
          </el-menu>
        </div>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
      <el-footer>
        <p>© 2023 RVC控制端 - 版本 1.0.0</p>
      </el-footer>
    </el-container>
  </div>
</template>

<script>
export default {
  name: 'App',
  computed: {
    activeRoute() {
      return this.$route.path;
    }
  }
}
</script>

<style>
body {
  margin: 0;
  padding: 0;
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', Arial, sans-serif;
}

.app-container {
  min-height: 100vh;
}

.el-container {
  min-height: 100vh;
}

.el-header {
  background-color: #409EFF;
  color: white;
  padding: 0;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
  padding: 0 20px;
}

.header-content h1 {
  margin: 0;
}

.el-menu.el-menu--horizontal {
  border-bottom: none;
  background-color: transparent;
}

.el-menu--horizontal > .el-menu-item {
  color: white;
  border-bottom: 2px solid transparent;
}

.el-menu--horizontal > .el-menu-item.is-active {
  color: white;
  border-bottom-color: white;
  background-color: rgba(255, 255, 255, 0.1);
}

.el-menu--horizontal > .el-menu-item:hover {
  background-color: rgba(255, 255, 255, 0.2);
}

.el-main {
  padding: 20px;
}

.el-footer {
  text-align: center;
  color: #909399;
  padding: 20px;
  border-top: 1px solid #EBEEF5;
}
</style> 