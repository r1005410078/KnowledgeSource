### **1. 基本概念**
- **Swarm**：Docker 内置的集群管理和编排工具（Docker 自带，不需要额外安装）。
- **Manager 节点**：负责调度、服务管理、集群状态维护。
- **Worker 节点**：只运行容器，听从 Manager 的调度。
- **Swarm mode**：通过 docker swarm init 或 docker swarm join 启用。

### **2. 核心对象**
- **Service**
    - Swarm 的最小调度单位，相当于一组副本（Replica）。
    - 定义镜像、运行参数、副本数、网络、端口等。
    - 示例：
```bash
docker service create --name web -p 80:80 nginx
```

- **Task**
    - Service 的一个实例（容器）。
    - Swarm 会根据 Service 定义，自动创建和分配 Task 到节点。
- **Stack**
    - 一组 Service 的集合，用 docker-compose.yml 文件描述。
    - 部署命令：
```bash
docker stack deploy -c docker-stack.yml myapp
```

### **3. 网络**
- **Overlay 网络**（Swarm 专用）
    - 跨节点的虚拟网络，支持 Service 之间通过 **服务名 (DNS)** 互相访问。
    - 必须在 docker-stack.yml 中配置共享网络，或手动创建外部 overlay 网络。
    
- **Ingress 网络**
    - 默认创建的 overlay 网络，用于 **负载均衡**。
    - 当你 -p 80:80 暴露端口时，Swarm 会在所有节点监听 80，然后把流量转发到运行该 Service 的节点。
    
- **Service 发现**
    - Service 名就是 DNS 名。
    - 例如：http://user-system-api:9001。

### **4. 服务更新**
- **滚动更新**
    - 修改 Service 的镜像/tag 或配置后，Swarm 按策略滚动重启容器。
    - 命令：
```bash
docker service update --image myimage:v2 myservice
```

- **强制更新（即使 tag 没变）**
```bash
docker service update --force myservice
```

- **Stack 更新**
    - 修改 docker-stack.yml，再执行：
```bash
docker stack deploy -c docker-stack.yml mystack
```


### **5. 常用命令**
```bash
docker swarm init                    # 初始化 Swarm
docker swarm join-token worker       # 获取加入集群的 worker token
docker swarm join-token manager      # 获取加入集群的 manager token
```

- **Service**
```bash
docker service ls                    # 查看所有服务
docker service ps myservice          # 查看服务的任务状态
docker service logs myservice        # 查看日志
docker service rm myservice          # 删除服务
```

- **Stack**
```bash
docker stack ls                      # 查看所有 Stack
docker stack ps mystack              # 查看 Stack 的 Task 状态
docker stack rm mystack              # 删除 Stack
```

- **网络**
```bash
docker network ls                    # 查看网络
docker network create -d overlay net # 创建 overlay 网络
```

### **6. 部署最佳实践**
1. **CI/CD 镜像管理**
    - 每次构建用唯一 tag（比如 commit SHA）。
    - 避免 latest，否则更新时可能拉不到新镜像。
    
2. **网络共享**
    - 多个 Stack 需要互通时，用外部 overlay 网络：
```yaml
networks:
  shared_net:
    external: true
```

3. **高可用**
    - Manager 节点建议至少 3 个（奇数个）。
    - Service 设置副本数 >1，保证容错。
    
4. **数据持久化**
    - 使用 volumes 绑定外部存储，而不是容器本地目录。

### **7. 优缺点**
✅ 优点：
- Docker 内置（简单易用）
- Service 发现 + 负载均衡自动化
- 滚动更新 / 回滚机制
- 适合小中型集群

❌ 缺点：
- 社区活跃度远低于 Kubernetes
- 生态不如 K8s 完善
- 高级调度能力有限

📌 **一句话总结**：
Docker Swarm = **轻量级 K8s**，适合快速部署和中小规模生产环境。核心就是：
- **stack** 管理应用
- **service** 管理容器组
- **overlay 网络** 让服务名互通
- **service update** / **stack deploy** 实现升级

