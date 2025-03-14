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
      }
    },
    client: {
      overlay: {
        errors: true,
        warnings: false
      },
      webSocketURL: {
        hostname: '0.0.0.0',
        pathname: '/sockjs-node',
        port: 8080
      }
    },
    webSocketServer: {
      type: 'sockjs',
      options: {
        prefix: '/sockjs-node'
      }
    }
  }
}) 