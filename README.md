# RVC控制端Web应用

一个RVC（机器人吸尘器）控制端web应用，用于通过Matter协议控制RVC设备。

## 技术栈

- **后端**：Python + Flask
- **前端**：Vue.js + Element Plus

## 功能特点

- Web页面显示分两块：
  - 基础信息：产品名，软硬件版本，IP地址等
  - 设备状态和控制按钮：
    - 状态显示当前清洁模式、操作状态和电量
    - 控制按钮：开始，结束，暂停，恢复，返回基站

- 后端通过WebSocket与Matter Server连接，地址可配置
- 前端通过HTTP接口发送控制命令，后端通过WebSocket向前端反馈设备状态

## 项目结构

```
matter-rvc-controller/
├── backend/                # 后端Flask应用
│   ├── api/                # API路由
│   ├── models/             # 数据模型
│   ├── static/             # 静态文件
│   ├── templates/          # 模板文件
│   ├── app.py              # 主应用入口
│   ├── config.py           # 配置文件
│   ├── matter_client.py    # Matter Server WebSocket客户端
│   ├── websocket_server.py # WebSocket服务器
│   └── requirements.txt    # 依赖文件
├── frontend/               # 前端Vue.js应用
│   ├── src/                # 源代码
│   │   ├── components/     # 组件
│   │   ├── services/       # 服务
│   │   ├── views/          # 视图
│   │   ├── App.vue         # 主组件
│   │   ├── main.js         # 入口文件
│   │   └── router/         # 路由
│   └── package.json        # 依赖文件
└── scripts/                # 项目脚本
    ├── setup_dev_env.sh    # 开发环境配置脚本
    ├── start_dev.sh        # 开发环境启动脚本
    └── build.sh            # 生产环境构建脚本
```

## 快速开始

### 使用脚本（推荐）

项目提供了一系列脚本，用于简化开发和部署过程：

1. 设置开发环境（创建Python虚拟环境并安装依赖）：

```bash
./scripts/setup_dev_env.sh
```

2. 启动后端服务：

```bash
./scripts/start_backend.sh
```

3. 启动前端开发服务器：

```bash
cd frontend
npm run serve
```

4. 或者一键启动开发环境（同时启动后端和前端服务）：

```bash
./scripts/start_dev.sh
```

5. 构建生产环境版本：

```bash
./scripts/build.sh
```

### 手动安装与运行

#### 后端

1. 安装依赖：

```bash
cd backend
pip install -r requirements.txt
```

2. 运行应用：

```bash
python app.py
```

#### 前端

1. 安装依赖：

```bash
cd frontend
npm install
```

2. 开发模式运行：

```bash
npm run serve
```

3. 构建生产版本：

```bash
npm run build
```

## 配置

- Matter Server WebSocket地址默认为：`ws://192.168.2.21:5580/ws`
- 可以通过Web界面的设置页面修改连接地址
- 也可以通过修改后端的`.env`文件或配置文件来更改默认设置

## 常见问题

### WebSocket连接问题

如果遇到WebSocket连接问题，可以尝试以下解决方案：

1. 确保后端服务器正在运行：
   ```bash
   ./scripts/start_backend.sh
   ```

2. 检查WebSocket服务器是否正常工作：
   ```bash
   ./scripts/test_websocket.py
   ```

3. 确保前端配置正确：
   - 前端WebSocket客户端应使用相对路径 `/ws`
   - Vue开发服务器应正确配置WebSocket代理

4. 如果使用不同的主机或端口，请相应更新配置

### 其他问题

如果遇到其他问题，请检查控制台日志以获取更多信息。

## API接口

### 获取设备状态

```
GET /api/status
```

### 控制设备

```
POST /api/control
{
  "action": "start|stop|pause|resume|return_to_base",
  "params": {}
}
```

### 获取配置

```
GET /api/config
```

### 更新配置

```
POST /api/config
{
  "matter_server_url": "ws://192.168.2.21:5580/ws"
}
```