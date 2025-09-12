## **1️⃣ Dockerfile**

- **作用**：构建镜像（image）。
- **功能**：
    - 指定基础镜像（FROM）
    - 安装依赖、拷贝文件、运行命令（RUN / COPY / ADD）
    - 设置启动命令（CMD / ENTRYPOINT）
    
- **输出**：生成一个可运行的 Docker 镜像。

## **2️⃣ Docker Compose**
- **作用**：描述 **如何运行一个或多个容器**（容器编排）。
- **功能**：
    - 定义多个服务（service）及镜像
    - 网络、卷挂载、环境变量、端口映射
    - 服务之间的依赖关系
    
- **输出**：docker-compose up 后，创建多个容器并按配置启动。

## **3️⃣ Kubernetes（K8s）**
- **作用**：生产级容器编排，取代 Docker Compose。
- **特点**：
    - **Pods**：最小运行单元（1~多个容器）
    - **Deployment / StatefulSet / DaemonSet**：管理 Pod 生命周期
    - **Service / Ingress**：管理网络和流量
    - **ConfigMap / Secret / Volume**：配置和存储管理
        
    
- **区别于 Compose**：
    - 不需要 docker-compose.yml
    - 用 **YAML 配置文件（Deployment、Service 等）** 描述如何运行容器
    - 支持自动扩容、滚动更新、健康检查、调度到不同节点等高级功能

### **🔹 对比总结**

| **工具**         | **作用**            | **输出**                        |
| -------------- | ----------------- | ----------------------------- |
| Dockerfile     | 构建镜像              | 镜像（image）                     |
| Docker Compose | 运行/编排容器（dev/小型环境） | 容器集合（单机或少量节点）                 |
| Kubernetes     | 生产级容器编排（集群级）      | Pods/Deployment/Service 等资源对象 |

## **4️⃣** Docker Swarm 模式（集群级调度）**
- Docker 的内置集群管理工具，可以跨多台机器部署多副本。
- 功能：
    - docker swarm init → 初始化 Swarm 集群
    - docker service create --replicas 3 myimage → 创建服务并运行 3 个实例
    - 自动调度、负载均衡、故障恢复
    
- 核心机制：
    - **Swarm Manager**：管理整个集群，调度副本到不同节点
    - **Worker Node**：运行容器实例
    - **Service + Replica**：指定服务副本数量，Manager 负责维护

|**场景**|**多实例实现方式**|**守护方式**|
|---|---|---|
|单机 Docker|手动 docker run -d 或 Docker Compose|dockerd 负责保持容器运行|
|单机 Compose|docker-compose up -d|dockerd + Compose 自动启动多个容器|
|多机集群|Docker Swarm / Kubernetes|Swarm Manager / K8s 控制器保证副本数量和健康|
✅ 核心结论：
- **普通 Docker** 只能单机守护，多实例需要手动或 Compose 配合。
- **Docker Swarm** 可以跨节点自动调度副本并守护。
- **Kubernetes** 更高级，提供自动扩容、滚动升级、健康检查、调度到指定节点等功能。