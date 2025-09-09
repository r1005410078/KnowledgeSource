## **1️⃣ Rust + Docker 构建相关**

**问题背景：**

- 你有 Rust 服务（如 domus、user_system），希望在 Mac 上通过 Docker 构建 x86_64 静态二进制。
- 使用了 musl 和 cargo build --target x86_64-unknown-linux-musl。
- Dockerfile 使用了两阶段构建：rust 镜像作为 builder，scratch 作为运行镜像。  

**遇到的问题：**
1. **平台指定问题**
    - 在 Dockerfile 中 FROM --platform=linux/amd64 rust:1.89 可以避免交叉编译卡住。
    - 即使在 docker buildx build --platform linux/amd64 指定了平台，Dockerfile 里也建议写 --platform，否则在 M1/M2/M3 架构下容易出错。
    
2. **交叉编译卡住**
    - 编译一些依赖（如 openssl、futures-task）会卡住。
    - 使用 openssl = { version = "0.10", features = ["vendored"] } 或者 openssl-sys 旧版本，也可能引起编译卡住。
    - 可能与 BuildKit 或容器环境（OrbStack）缓存有关。
    
3. **Build 缓存和容器管理**
    - 删除容器后，原来的 docker buildx 构建器可能失效（如 desktop-linux）。
    - 使用 docker buildx ls 查看 builder 状态，发现 inactive 或 error。
    - OrbStack 的 builder 容器丢失后，无法直接删除或恢复，需要切换到默认 context 或重新创建 builder。

----

## **2️⃣ Docker Buildx & OrbStack / Docker Desktop**

**问题背景：**
- Mac M 系列 + OrbStack。
- 原来使用 desktop-linux builder，编译不卡。
- 删除了部分容器后，buildx builder 状态异常。
- 
**遇到的问题：**
1. **无法连接 Docker daemon**
    - Cannot connect to the Docker daemon at unix:///Users/rongts/.docker/run/docker.sock
    - OrbStack 被卸载后，原来的 builder（desktop-builder0 / orbstack）失效。
    
2. **重新创建 builder 错误**
    - docker buildx create --name desktop-linux --use 报错：名字已存在。
        
3. **切换 context / use default**
    - docker context use default 可以切换到默认 context。
    - OrbStack builder 与默认 Docker builder 是不同 context。
        
4. **最终方案**
    - 安装 Docker Desktop，恢复原来的 desktop-linux builder。
    - 确认 builder 正常运行后再执行交叉编译。

-----

## **3️⃣ Next.js 前端代理 Rust 后端**

**问题背景：**
- 前端 Next.js 项目，后端 Rust 服务。
- 需要在开发时或 Docker 容器中使用代理访问 Rust 接口。
   
**遇到的问题：**
1. **环境变量未生效**
    - NEXT_PUBLIC_DOMUS_API_URL / NEXT_PUBLIC_USER_SYSTEM_API_URL 在容器中运行 Next.js 时仍然是 localhost。
    - 解决方法：
        - 确认 Docker container 环境变量正确传入（-e NEXT_PUBLIC_DOMUS_API_URL=http://domus-api:8091）。
        - Next.js 中 next.config.ts 使用 process.env。
        - 注意客户端环境变量必须以 NEXT_PUBLIC_ 开头。
    
2. **容器之间互相访问**
    - 127.0.0.1 无法访问其他容器。
    - 使用容器名称作为主机名（Docker 内部 DNS）即可。
    - 可以在 docker-compose 中统一网络，让服务通过 service_name:port 互相访问。

## **4️⃣ Docker Compose & 多服务管理**
**问题背景：**
- 前端和后端各自独立容器，想统一管理。
**遇到的问题：**
1. **compose 文件位置与管理**
    - 可以使用一个顶层 docker-compose.yml 管理多服务，也可以每个项目一个 compose 文件。
    - 顶层 compose 里服务可指定镜像、端口、依赖等。
2. **Compose 配置问题**
    - secrets 错误：你把 build 放到 secrets 下，导致报错 Additional property build is not allowed。
    - 正确写法：build 只能在 services 下。
3. **端口和 host 配置**
    - 环境变量可以用容器名称作为 host。
    - 不建议在前端容器里写 localhost，应写成 domus-api。

---- 

## **5️⃣ Rust / OpenSSL**
**问题背景：**
- Rust 项目依赖 openssl-sys 或 openssl crate。
**遇到的问题：**
1. openssl-sys 编译失败：缺少 perl 或 OpenSSL dev 库。
2. 对策：
    - 在 Dockerfile 中安装依赖：apt-get install -y musl-tools build-essential pkg-config libssl-dev perl。
    - 使用 features = ["vendored"] 可以静态编译 OpenSSL，但在 cross build 时容易卡。
3. 卡住的 crate 多为基础依赖，如 futures-task、unicode-ident


---- 

## **6️⃣ 总结经验教训**

1. **交叉编译 x86_64 在 M 系列 Mac 上容易卡**
    - 建议使用独立 Linux builder（`desktop-linux` 或` buildx container`）。
    - BuildKit / OrbStack / Docker Desktop 的 builder 状态影响交叉编译。
2. `Docker buildx `与 context、builder 容器管理**
    - 删除 builder 容器可能导致 ` buildx builder` 异常。
    - `docker buildx ls、docker context use default、docker buildx rm` 是排查工具。
3. **Next.js 前端容器访问后端**
    - 不能用 localhost，要用服务名称。
    - 环境变量必须在容器运行时生效。
4. **缓存和依赖问题**
    - Cargo 卡住可能是依赖编译或 buildx 缓存问题。
    - 可以尝试 docker builder prune 或清理 target 文件夹。
5. **Docker Desktop / OrbStack**
    - OrbStack 卸载后，之前依赖的 builder 无法恢复。
    - 重新安装 Docker Desktop 可以恢复 desktop-linux builder。

