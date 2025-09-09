1. **触发条件（Triggers）**
    - 常用的有：
        - `push`：代码推送触发
        - `pull_request`：PR 时触发
        - `workflow_dispatch`：手动触发
        - `schedule`：定时任务（cron 表达式）
        
2. **工作流文件（Workflow）**
    - 存放在仓库 `.github/workflows/*.yml`
    - 一个仓库可以有多个 workflow 文件
    - 每个 workflow 可以包含多个 **job**
    
3. **Job 与 Runner**
    - 每个 **job** 在一个 **runner**（虚拟机或容器）里执行
    - 可以选择：
        - `ubuntu-latest`
        - `macos-latest`
        - `windows-latest`
    - 或者用 **self-hosted runner**（你自己的服务器/机器）

 ## **🔹 常用功能**
1. **构建与测试**
    - 运行 `docker build` 构建镜像
    - 运行 `cargo build、npm install && npm run build` 等编译步骤
    - 单元测试 `cargo test、npm test`
    
2. **缓存（Cache）**
    - 使用 `actions/cache` 缓存依赖，加快 CI 速度
    - 例如：
```yaml
- uses: actions/cache@v3
  with:
    path: ~/.cargo/registry
    key: ${{ runner.os }}-cargo-${{ hashFiles('**/Cargo.lock') }}
```

3. **Secrets 与环境变量**
    - 使用 `secrets` 存储敏感信息（如 DOCKER_PASSWORD、SSH_KEY）
    - 在 `workflow` 中通过 ${{ secrets.MY_SECRET }} 取用
    
4. **Docker 相关**

- 登录：
```yaml
- name: Docker login
  run: echo ${{ secrets.DOCKER_PASSWORD }} | docker login registry.cn-hangzhou.aliyuncs.com -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
```
-  构建 & 推送：
```bash
- name: Build and Push Docker image
  run: |
    docker build -t registry.cn-hangzhou.aliyuncs.com/tongts/my-service:v1 .
    docker push registry.cn-hangzhou.aliyuncs.com/tongts/my-service:v1
```

5. **部署到服务器**
    - 通过 ssh 连接服务器：
```yaml
- name: Deploy to server
  run: ssh -o StrictHostKeyChecking=no user@server "cd ~/project && docker stack deploy -c docker-stack.yml my-stack"
```

-  需要提前把 **服务器公钥** 加到 `~/.ssh/authorized_keys`

## **基本结构**

```yaml
name: CI Pipeline   # 工作流名称
on:                 # 触发条件
  push:
    branches: [ main ]
  pull_request:
jobs:               # 任务集合
  build:            # 任务名称
    runs-on: ubuntu-latest   # 运行环境
    steps:          # 执行步骤
      - name: Checkout code  # 步骤名
        uses: actions/checkout@v4   # 插件（Action）
      - name: Run build
        run: npm run build   # 执行命令
      - name: Deploy
        run: echo "Deploying..."
```

## **🔹 常见关键字**
| **关键字** | **作用**                                                 |
| ------- | ------------------------------------------------------ |
| name    | 定义工作流、job 或 step 的名字                                   |
| on      | 定义触发条件（push、pull_request、workflow_dispatch、schedule 等） |
| jobs    | 工作流的任务集合                                               |
| runs-on | 运行环境（ubuntu-latest / windows-latest / macos-latest）    |
| steps   | job 的执行步骤                                              |
| uses    | 调用现成 action                                            |
| run     | 在 shell 中执行命令                                          |
| with    | 给 uses 的 action 传递参数                                   |
| env     | 定义环境变量（全局/job/step 级别）                                 |
| secrets | 调用 GitHub Secrets 里的敏感信息                               |
## 🔹  常用 `Actions` 插件
### **📦 代码管理**
- `actions/checkout@v4` → 拉取代码 
- `actions/cache@v4` → 缓存依赖
### **⚙️ 环境准备**
- `actions/setup-node@v4` → Node.js
- `actions/setup-python@v5` → Python
- `actions/setup-java@v4 → Java
- `actions/setup-go@v5` → Go
- `docker/setup-buildx-action@v3` → 启用 Docker Buildx
### **🐳 Docker**
- `docker/login-action@v3` → 登录 DockerHub/Registry
- `docker/build-push-action@v5` → 构建并推送镜像
### **🚀 部署**
- `appleboy/ssh-action@v1.0.3` → 远程 SSH 部署
- `appleboy/scp-action@v0.1.7` → 远程传输文件
- `azure/webapps-deploy@v2` → 部署到 Azure WebApp
### **✅ 测试 & 报告**
- `codecov/codecov-action@v4 `→ 上传覆盖率报告
- `github/codeql-action/init `→ 代码安全扫描
### **🔔 通知**
- `slackapi/slack-github-action@v1.24.0` → Slack 通知
- `appleboy/telegram-action@v0.1.1` → Telegram 通知

## **🔹 5. Secrets & Envs**
- 在仓库 **Settings → Secrets and variables → Actions** 中配置
- 使用方法：
```bash
- name: SSH Deploy
  uses: appleboy/ssh-action@v1.0.3
  with:
    host: ${{ secrets.SSH_HOST }}
    username: ${{ secrets.SSH_USER }}
    key: ${{ secrets.SSH_PRIVATE_KEY }}
    script: |
      cd /app && docker-compose up -d
```

## **🔹 6. 一个完整的例子**

```yaml
name: Deploy to Server
on:
  push:
    branches: [ main ]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
        
      - name: Log in to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}

      - name: Build and Push Docker Image
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: myrepo/myapp:latest

      - name: Deploy via SSH
        uses: appleboy/ssh-action@v1.0.3
        with:
          host: ${{ secrets.SSH_HOST }}
          username: ${{ secrets.SSH_USER }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            docker pull myrepo/myapp:latest
            docker stack deploy -c docker-stack.yml myapp
```


