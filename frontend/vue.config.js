const { defineConfig } = require('@vue/cli-service')
const webpack = require('webpack')

module.exports = defineConfig({
  transpileDependencies: true,
  lintOnSave: false, // 可以设置为true启用保存时lint
  configureWebpack: {
    plugins: [
      // 定义Vue特性标志
      new webpack.DefinePlugin({
        __VUE_PROD_DEVTOOLS__: false,
        __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: false
      })
    ]
  },
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