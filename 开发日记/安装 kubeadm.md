**[kubeadm](https://kubernetes.io/zh-cn/docs/setup/production-environment/tools/kubeadm/install-kubeadm/)** 是 Kubernetes 官方提供的一个命令行工具，用于 **快速部署和管理 Kubernetes 集群**。它并不是一个完整的 Kubernetes 发行版，而是帮助你在已有的机器上，通过最小化、可复现的方式 **初始化、配置和升级** 一个合规的 Kubernetes 集群。
### **主要作用**
1. **初始化集群**
    - 使用 kubeadm init 在一台节点上初始化 **控制平面（master）**。
    - 它会生成必要的配置文件、证书、密钥等，并启动 kube-apiserver、kube-controller-manager、kube-scheduler 等核心组件。
2. **加入节点**
    - 使用 kubeadm join 命令，将新的 **工作节点（worker）** 或 **额外的控制平面节点** 加入集群。
3. **生成证书和密钥**
    - 处理 Kubernetes 组件所需的 TLS 证书，保证集群安全。
4. **升级集群**
    - 提供 kubeadm upgrade 命令进行安全升级。
5. **配置默认组件**
    - 比如 kube-proxy、CoreDNS 等核心插件的部署。

### **kubeadm 不做的事情**
- **不部署容器运行时**（CRI，比如 containerd 或 CRI-O，你需要自己安装）。
- **不安装网络插件**（CNI，比如 Calico、Flannel、Cilium）。
- **不做机器管理**（比如创建虚拟机、节点扩容）。
- **不提供 Dashboard、监控等额外组件**。
### **为什么用 kubeadm 而不是手动搭建？**
- **标准化**：符合 CNCF 的 Kubernetes 集群最佳实践。
- **节省时间**：自动化证书、密钥生成和配置。
- **简化复杂度**：不用手动写很多 YAML 配置。
- **升级方便**：官方支持 kubeadm upgrade。

### 安装
1.  判断端口是否被占用了
```bash
nc 127.0.0.1 6443 -zv -w 2
```

2. 禁用交换分区
```bash
# 临时
sudo swapoff -a

# 永久生效
sudo sed -i.bak '/swap/s/^/#/' /etc/fstab
```

3. 安装运行时前提条件
```bash
## 安装和配置先决条件

# 设置所需的 sysctl 参数，参数在重新启动后保持不变
cat <<EOF | sudo tee /etc/sysctl.d/k8s.conf
net.ipv4.ip_forward = 1
EOF

# 应用 sysctl 参数而不重新启动
sudo sysctl --system

# 使用以下命令验证 `net.ipv4.ip_forward` 是否设置为 1：
sysctl net.ipv4.ip_forward
```   
4. [开始安装运行时](https://docs.docker.com/engine/install/)
```bash
# 卸载旧版本
for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc; do sudo apt-get remove $pkg; done

# ### [使用`apt`存储库安装](https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository)
# 在新的主机上首次安装 Docker Engine 之前，您需要设置 Docker`apt`仓库。之后，您可以从该仓库安装和更新 Docker。

# 1. 设置 Docker 的`apt`存储库
# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

#要安装最新版本，请运行：
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# 通过运行镜像验证安装是否成功`hello-world`
sudo docker run hello-world

# 要在 `/etc/containerd/config.toml` 中将 `runc` 配置为使用 `systemd` cgroup 驱动， 请根据你使用的 Containerd 版本设置以下配置
# - Kubernetes 和 containerd 要使用相同的 cgroup 驱动。
#- **默认 containerd 用 cgroupfs**，而 kubeadm 推荐 **systemd**。
#- 不一致时，kubeadm init 或 kubelet 会报错：

containerd config default > /etc/containerd/config.toml

vi /etc/containerd/config.toml
[plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runc.options]
    SystemdCgroup = true
    
# 重启服务
systemctl restart containerd


mkdir -p /etc/systemd/system/docker.service.d

cat <<EOF | sudo tee /etc/systemd/system/docker.service.d/proxy.conf
[Service]
Environment="HTTP_PROXY=http://192.168.2.10:7890"
Environment="HTTPS_PROXY=http://192.168.2.10:7890"
EOF
```

4. [安装 kubelet kubeadm kubectl](https://kubernetes.io/zh-cn/docs/setup/production-environment/tools/kubeadm/install-kubeadm/#installing-kubeadm-kubelet-and-kubectl)

```shell
# - 更新 apt 包索引，确保安装的是最新版本
sudo apt-get update
# - **apt-transport-https**
# - - 让 apt 支持通过 HTTPS 协议下载软件包。
# - - 在新版本 Ubuntu/Debian 里，它可能是一个虚拟包，因为 apt 默认已支持 HTTPS。
# - **ca-certificates**
# - - 包含 CA 根证书，保证 HTTPS 连接的安全性。
# - **curl** - - 下载文件或数据，比如拉取 Kubernetes GPG 公钥。
# - **gpg** - - 用于处理 GPG 密钥，确保下载的包是签名验证过的。
# apt-transport-https 可能是一个虚拟包（dummy package）；如果是的话，你可以跳过安装这个包
sudo apt-get install -y apt-transport-https ca-certificates curl gpg

# 如果 `/etc/apt/keyrings` 目录不存在，则应在 curl 命令之前创建它，请阅读下面的注释。
# sudo mkdir -p -m 755 /etc/apt/keyrings
curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.34/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg

# 这条命令的作用是 **往 /etc/apt/sources.list.d/kubernetes.list 文件中写入 Kubernetes 的 apt 软件源地址**，并且要求 apt 使用指定的 GPG 密钥文件进行签名验证。
# 此操作会覆盖 /etc/apt/sources.list.d/kubernetes.list 中现存的所有配置。
# 添加 Kubernetes `apt` 仓库。 请注意，此仓库仅包含适用于 Kubernetes 1.34 的软件包； 对于其他 Kubernetes 次要版本，则需要更改 URL 中的 Kubernetes 次要版本以匹配你所需的次要版本 （你还应该检查正在阅读的安装文档是否为你计划安装的 Kubernetes 版本的文档）。
echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.34/deb/ /' | sudo tee /etc/apt/sources.list.d/kubernetes.list


# 更新 `apt` 包索引，安装 kubelet、kubeadm 和 kubectl，并锁定其版本：

sudo apt-get update
sudo apt-get install -y kubelet kubeadm kubectl
sudo apt-mark hold kubelet kubeadm kubectl

```

5. [安装网络插件](https://github.com/flannel-io/flannel#deploying-flannel-manually)
	```bash
	kubectl apply -f https://github.com/flannel-io/flannel/releases/latest/download/kube-flannel.yml
	```

6. 初始化
```bash
sudo kubeadm init --pod-network-cidr=10.244.0.0/16 --image-repository=registry.aliyuncs.com/google_containers
```

 7.  重置
 ```bash
 # ### **重置 kubeadm**
 sudo kubeadm reset -f
 
 # 这个目录主要用于存放 Kubernetes 集群中所有 TLS 证书、密钥和 CA 证书
 sudo rm -rf /etc/kubernetes/pki
 
 # ### **清理 CNI 网络配置（可选，但推荐）**
 sudo rm -rf /etc/cni/net.d
 sudo rm -rf /var/lib/cni/
 sudo rm -rf /var/lib/kubelet/*
 
 # ### **清理 kubeconfig（可选）** - 如果你之前设置了 KUBECONFIG=/etc/kubernetes/admin.conf，也可以保留或删除
 
 rm -f $HOME/.kube/config
 
 # sudo systemctl restart kubelet
 ```
7. 创建 Token
```bash
sudo kubeadm token create --print-join-command
```


#### 错误

```bash
root@storage-1:~# kubectl describe pod  coredns-7cc97dffdd-k5qjm -n kube-system
mption: 0/1 nodes are available: 1 Preemption is not helpful for scheduling.

  Warning  FailedScheduling        50s                  default-scheduler  0/1 nodes are available: 1 node(s) had untolerated taint {node.kubernetes.io/not-ready: }. no new claims to deallocate, preemption: 0/1 nodes are available: 1 Preemption is not helpful for scheduling.

  Normal   Scheduled               46s                  default-scheduler  Successfully assigned kube-system/coredns-7cc97dffdd-k5qjm to storage-1

  Warning  FailedCreatePodSandBox  45s                  kubelet            Failed to create pod sandbox: rpc error: code = Unknown desc = failed to setup network for sandbox "873b7e293d2202980ae651ffa7fe7525e4ba0fd262218238bce8d8422cba4e91": plugin type="loopback" failed (add): failed to find plugin "loopback" in path [/opt/cni/bin]

root@storage-1:~# ls -l /opt/cni/bin/loopback

ls: cannot access '/opt/cni/bin/loopback': No such file or directory
```

缺少执行文件， 下载 cni 插件放进去就好了


```bash
[preflight] Running pre-flight checks
W0901 14:39:44.478120    9308 checks.go:1049] [preflight] WARNING: Couldn't create the interface used for talking to the container runtime: failed to create new CRI runtime service: validate service connection: validate CRI v1 runtime API for endpoint "unix:///var/run/containerd/containerd.sock": rpc error: code = Unimplemented desc = unknown service runtime.v1.RuntimeService
[preflight] Some fatal errors occurred:
        [ERROR FileAvailable--etc-kubernetes-kubelet.conf]: /etc/kubernetes/kubelet.conf already exists
        [ERROR FileAvailable--etc-kubernetes-bootstrap-kubelet.conf]: /etc/kubernetes/bootstrap-kubelet.conf already exists
        [ERROR FileAvailable--etc-kubernetes-pki-ca.crt]: /etc/kubernetes/pki/ca.crt already exists
[preflight] If you know what you are doing, you can make a check non-fatal with `--ignore-preflight-errors=...`
error: error execution phase preflight: preflight checks failed
To see the stack trace of this error execute with --v=5 or higher
```

join 失败后有遗留问题，reset 一下就好了

🙋 排查问题命令集合

```bash
# 会看到最近发生的事件，已解决的错误事件通常不会再次出现。
kubectl get events -n kube-system --sort-by='.lastTimestamp'

# 查看所有节点状态
kubectl get nodes

# 查看单个节点详细信息（包括 Conditions、Taints、Labels 等）
kubectl describe node <node-name>

# 查看 kube-system 命名空间下所有 Pod
kubectl get pods -n kube-system

# 查看 Pod 详细信息（包括 Events）
kubectl describe pod <pod-name> -n kube-system

# 查看 Pod 日志
kubectl logs <pod-name> -n <namespace>

# 实时查看 kubelet 日志
journalctl -u kubelet -f

# 3. **检查 containerd CRI**
crictl info

# 查看 CNI 配置文件
cat /etc/cni/net.d/10-flannel.conflist

# 查看 CNI 插件二进制文件
ls -l /opt/cni/bin/

# 拉取镜像
docker pull <image>

# 查看 Docker 镜像仓库配置
docker info | grep -i "Registry\|Mirror"

# 测试镜像仓库可达性
curl -v <mirror-url>

# 查看 kubelet 配置文件
cat /var/lib/kubelet/config.yaml


# 查看 kubelet 进程启动参数
ps -ef | grep kubelet

# 当防火墙关闭导致 Flannel 网络失效时，可重启 Flannel Pod
kubectl delete pod -n kube-flannel -l app=flannel

# 确保 CNI 插件目录中插件存在
ls -l /opt/cni/bin/

# 生成加入集群的 token
kubeadm token create

# 查看现有 token
kubeadm token list
  
# 打印 kubeadm join 命令
kubeadm token create --print-join-command

```


### 国内镜像问题 (子节点)

```bash
# Flannel 镜像

docker save ghcr.io/flannel-io/flannel:v0.27.2 -o flannel_v0.27.2.tar

docker save ghcr.io/flannel-io/flannel-cni-plugin:v1.7.1-flannel1 -o flannel-cni-v1.7.1.tar

  

# Pause 镜像

docker save registry.aliyuncs.com/google_containers/pause:3.8 -o pause_3.8.tar
```

##  **导入 containerd 的 k8s.io 命名空间**

```bash
# Pause

ctr -n k8s.io images import pause_3.8.tar

ctr -n k8s.io images tag registry.aliyuncs.com/google_containers/pause:3.8 registry.k8s.io/pause:3.8

  

# Flannel 主镜像

ctr -n k8s.io images import flannel_v0.27.2.tar

  

# Flannel CNI 插件镜像

ctr -n k8s.io images import flannel-cni-v1.7.1.tar
```


### **拉国内加速镜像**

```bash
docker pull registry.aliyuncs.com/google_containers/pause:3.8
```


### Q/A
	1. ctr images 跟 docker images 区别
