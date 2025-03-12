const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  transpileDependencies: true,
  lintOnSave: false, // 可以设置为true启用保存时lint
  devServer: {
    port: 8080,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true
      },
      '/ws': {
        target: 'ws://localhost:5000',
        ws: true,
        changeOrigin: true,
        pathRewrite: {
          '^/ws': '/ws'  // 重写路径
        }
      }
    },
    client: {
      overlay: {
        errors: true,
        warnings: false
      }
    }
  }
}) 