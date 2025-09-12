## **🔹 1. 准备工作**

  

### **在 Mac 上：**

- 安装 **UTM**（官网：https://mac.getutm.app/）
    
- 下载 **Ubuntu ARM64 镜像**（推荐 Ubuntu 22.04 LTS ARM64 Desktop Server）
    
    - 官网：https://ubuntu.com/download/server/arm

## **🔹 2. 创建 Ubuntu 虚拟机（UTM）**
1. 打开 UTM → 点击 **+** → “Virtualize”
    - **Architecture**：ARM64
    - **System**：Linux
    
2. **启动 ISO 镜像**：加载下载的 Ubuntu ARM64 ISO
3. 分配资源：
    - CPU 核心：至少 4 核
    - 内存：至少 8GB（推荐 16GB）
    - 硬盘：≥40GB
    
4. 完成安装，启动 Ubuntu 系统，创建用户

## **🔹 3. 在 Ubuntu 上安装 Waydroid**

### **3.1 安装依赖**

```bash
sudo apt update
sudo apt install curl lxc wget git sudo -y
```


### **3.2 安装 Waydroid 官方工具**

```bash
sudo curl https://repo.waydro.id | sudo bash
sudo apt install waydroid -y
```

### **3.3 初始化 Waydroid**

```bash
sudo waydroid init
```

### **3.4 启动 Waydroid**

```bash
sudo waydroid container start
waydroid session start
waydroid show-full-ui
```



为什么安卓系统，不能想安装 linux 一样安装呢

## **🔹 1. Linux 的安装方式**

- Linux（Ubuntu、Fedora 等）是一套 **完整操作系统**
- 安装时直接把 **内核 + 用户空间 + 桌面环境 +软件包管理器** 写入硬盘
- 你可以随意添加删除应用，通过包管理器（apt、dnf、yum）安装软件
  

特点：
1. **完整文件系统**：/bin /usr /etc /home …
2. **包管理**：系统可以统一管理应用
3. **硬件抽象简单**：大部分设备都有通用驱动


## **🔹 2. Android 的安装方式不同的原因**

Android 并不是传统 Linux 系统，它是 **嵌入式操作系统**，设计理念不同：
### **（1）应用安装机制不同**
- Android 应用是 **APK 包**，打包了字节码、资源、Manifest
- 不直接操作文件系统，而是：
    - 每个 App 有 **自己的私有目录**（/data/data/package.name）
    - 通过 **PackageManager + ART** 运行
    
- 不像 Linux，你不能把 App 放在 /usr/bin 就能运行
    
### **（2）系统是针对设备裁剪的**
- Android 压根没有完整的桌面文件系统（比如 /usr/bin、/etc/init.d）
- 系统核心（Framework、ART、系统服务）都是为 ARM 手机硬件优化的
- 不同手机厂商有自己的 HAL（硬件抽象层）、驱动、定制 ROM
- 因此不能通用安装方式，必须和硬件绑定
    

### **（3）应用沙箱与安全机制**
- 每个 Android App 都运行在 **独立 UID 下**，被沙箱隔离
- 文件系统权限严格控制，防止 App 随意改系统文件
- Linux 则更开放，root 权限可以随意安装软件
    

### **（4）系统更新方式**
- Linux：包管理 + 系统升级
- Android：**ROM 镜像**整体更新，或者 OTA 升级
- 你不能像 Linux apt install 某个系统服务那样更新核心系统

