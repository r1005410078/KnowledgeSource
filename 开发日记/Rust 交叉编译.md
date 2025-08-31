## 故事背景

---

我们公司是一家**传统电力企业**，主要做**储能系统（ESS）**。储能分两种：**大储**和**小储**，区别其实就是**规模大小**。大储并发量高，小储相对轻量。

大储现在跑的是**Java 全家桶 + 分布式架构**，在**刀片服务器**上，这套对大储没问题，但放到小储上就显得**太笨重**了。更关键的是，Java 在国产系统上的兼容性也不算好，有时候还会踩坑。
所以，公司决定搞一套**软硬件一体的小储系统**，既轻量又能灵活适配国产系统。

硬件这边，用的是**瑞芯微的板子**，硬件工程师自己画的，系统也是我们基于 Linux 移植的。

软件这块，分两部分：
- **C++**：主要负责**数据采集**和**数据下发**，直接跟硬件打交道。像那些**Modbus、104、61850 协议**，都是公司元老当年写的“祖传代码”，我们现在也就维护维护。但不得不说，**底层还是香**。
- **Rust**：用来做**Web 服务**，处理采集的数据，然后给前端展示。

你可能会问：**为啥不用 C++ 或 Go？**

其实，用 Go 可能更合适，轻量、生态也好，公司后端语言也严重过剩，Java 太笨重了， 还有装个虚拟机，而且对国产系统兼容性也不是很好。但最后选 Rust，多少带点**个人主义的因素**😂。说实话，我自己也喜欢 Rust，Rust后端主要是我跟我的领导在写。但站在公司角度，这决定我有点不敢苟同：**Rust 招人太难，对个人来说不可替代性非常高**。关键这写rust的出去也不吃香啊，go的就业相对rust还是高很多了。

前端这块更有意思。一开始用的是**Chrome + Vue**，后来换成了**Flutter**。为啥换？因为 Chrome **太吃内存**了，跑几天就**卡死**，不稳定得很。选 Flutter 时，我们还考虑过 **Qt**，Qt 对 Linux 的兼容性确实好，但**开发门槛高**。公司前端 5 个人，本来就**严重过剩**，我也是其中之一，嘿嘿。Flutter 上手快，UI库生态好。于是这活就丢给了我们。我当时的想法很简单：**有项目干，就不用担心裁员，美滋滋**。

Flutter 的坑还不少，下次再聊吧。

早期的功能很少，点号历史等业务数据都是用的文件来做， web框架使用的是 `actix-web` 然后在加一些辅助库 json thiserror http log 等, 我们在 `macos` 上开发 开发完成后，需要在开发版上编译，就这样我们使用了一段时间，当时交叉编译其实我们也知道，就是觉得这玩意太高端了，没敢去碰，每次我们在板子上编译是真的慢， 在加上后面因为我们要做自动运维CI/CD不得不去研究了。

**什么是交叉编译**
交叉编译（Cross Compilation）指的是**在一种平台上编译程序，但目标程序运行在另一种平台上** 对胃口我们在 `macos` 上开发要编译成linux 可执行文件

**为什么要交叉编译呢**
1. **目标设备算力弱**：比如嵌入式板子（ARM）性能不够，直接编译慢
2. **目标设备没有完整开发环境**：小型 Linux 系统、IoT 设备、路由器。
3. **在 CI/CD 或大服务器上统一编译**：统一产物，方便部署。

**Rust自带的交叉编译工具**

	1.交叉编译命令

```bash
 hello git:(master) ✗ cargo build --target x86_64-unknown-netbsd                              
   Compiling cfg-if v1.0.3
   Compiling pin-project-lite v0.2.16
   Compiling futures-core v0.3.31
   Compiling libc v0.2.175
   Compiling serde v1.0.219
   Compiling crossbeam-utils v0.8.21
   Compiling libm v0.2.15
   Compiling stable_deref_trait v1.2.0
   Compiling typenum v1.18.0
   Compiling num-traits v0.2.19
   Compiling parking v2.2.1
   Compiling zerofrom v0.1.6
error[E0463]: can't find crate for `core`
  |
  = note: the `x86_64-unknown-netbsd` target may not be installed
  = help: consider downloading the target with `rustup target add x86_64-unknown-netbsd`
```

	2. 看错误让我添加这个, 执行这句话之前，我们看看 Rust 支持哪些平台交叉编译

```bash
tenant-system git:(master) ✗ rustup target list                                                       
aarch64-apple-darwin (installed)
aarch64-apple-ios
aarch64-apple-ios-macabi
aarch64-apple-ios-sim
aarch64-linux-android (installed)
aarch64-pc-windows-gnullvm
aarch64-pc-windows-msvc
aarch64-unknown-fuchsia
aarch64-unknown-linux-gnu (installed)
aarch64-unknown-linux-musl
aarch64-unknown-linux-ohos
aarch64-unknown-none
aarch64-unknown-none-softfloat
aarch64-unknown-uefi
arm-linux-androideabi
arm-unknown-linux-gnueabi
arm-unknown-linux-gnueabihf
arm-unknown-linux-musleabi
arm-unknown-linux-musleabihf
...
```

	3. 添加完成后我们继续执行

```bash
hello git:(master) ✗ rustup target add x86_64-unknown-linux-gnu     
info: component 'rust-std' for target 'x86_64-unknown-linux-gnu' is up to date

hello git:(master) ✗ cargo build --target x86_64-unknown-linux-gnu     
   Compiling hello v0.1.0 (/Users/rongts/hello)
error: linking with `cc` failed: exit status: 1
  |
  = note:  "cc" "-m64" "/var/folders/vk/hj12b3d9529c3xwt399dlc480000gn/T/rustcPoDzpS/symbols.o" "<7 object files omitted>" "-Wl,--as-needed" "-Wl,-Bstatic" "<sysroot>/lib/rustlib/x86_64-unknown-linux-gnu/lib/{libstd-*,libpanic_unwind-*,libobject-*,libmemchr-*,libaddr2line-*,libgimli-*,librustc_demangle-*,libstd_detect-*,libhashbrown-*,librustc_std_workspace_alloc-*,libminiz_oxide-*,libadler2-*,libunwind-*,libcfg_if-*,liblibc-*,librustc_std_workspace_core-*,liballoc-*,libcore-*,libcompiler_builtins-*}.rlib" "-Wl,-Bdynamic" "-lgcc_s" "-lutil" "-lrt" "-lpthread" "-lm" "-ldl" "-lc" "-L" "/var/folders/vk/hj12b3d9529c3xwt399dlc480000gn/T/rustcPoDzpS/raw-dylibs" "-Wl,--eh-frame-hdr" "-Wl,-z,noexecstack" "-L" "<sysroot>/lib/rustlib/x86_64-unknown-linux-gnu/lib" "-o" "/Users/rongts/hello/target/x86_64-unknown-linux-gnu/debug/deps/hello-807003dda5d5fb85" "-Wl,--gc-sections" "-pie" "-Wl,-z,relro,-z,now" "-nodefaultlibs"
  = note: some arguments are omitted. use `--verbose` to show all linker arguments
  = note: clang: warning: argument unused during compilation: '-pie' [-Wunused-command-line-argument]
          ld: unknown options: --as-needed -Bstatic -Bdynamic --eh-frame-hdr -z --gc-sections -z -z 
          clang: error: linker command failed with exit code 1 (use -v to see invocation)
          

error: could not compile `hello` (bin "hello") due to 1 previous error
```

特喵的有报错！！！

这个错误的核心原因是：**你在 macOS 上交叉编译 x86_64-unknown-linux-gnu 目标时，Rust 能编译 .o 文件，但最后一步 link 失败，因为 macOS 系统默认的 cc（其实是 clang）不会支持 Linux 的链接选项。**

**为什么会报** inking with cc failed**

Rust 编译器能生成目标平台（Linux x86_64）的目标代码，但链接阶段需要：

- Linux 的链接器（ld）
- Linux 的标准库（glibc）
- 对应的交叉编译工具链

但是 macOS 上只有 Darwin 平台的工具链，clang 不认识 --as-needed、-z、--gc-sections 等 GNU ld 的参数，直接报错。

	4. 问题搞清楚了，那我们怎么配置其他编译器呢，而且编译器怎么选择跟下载呢

`macos m系列`， 使用 brew 就可以安装，我使用 x86 aarch64 都是可以直接用的
```bash
hello git:(master) ✗ brew install x86-linux-gnu-gcc
Warning: No available formula with the name "x86-linux-gnu-gcc". Did you mean x86_64-linux-gnu-binutils?
==> Searching for similarly named formulae and casks...
==> Formulae
x86_64-linux-gnu-binutils ✔

To install x86_64-linux-gnu-binutils ✔, run:
  brew install x86_64-linux-gnu-binutils ✔
  
# 根据错误提示，我们执行 brew install x86_64-linux-gnu-gcc

hello git:(master) brew install x86_64-linux-gnu-gcc
hello git:(master) ✗ ls -al  /opt/homebrew/bin/x86_64-linux-gnu-gcc                
lrwxr-xr-x  1 rongts  admin  66  8 15  2024 /opt/homebrew/bin/x86_64-linux-gnu-gcc -> ../Cellar/x86_64-unknown-linux-gnu/13.2.0/bin/x86_64-linux-gnu-gcc

```

其他平台或者没有找到 编译器怎么办呢？
可以使用 docker qemu [corss](https://github.com/cross-rs/cross) 技术 ，或者使用 [cargo_buildzig](https://github.com/rust-cross/cargo-zigbuild) 就是zig整的一套交叉编译工具,可以替代 x86_64-linux-gnu-gcc 非常哇塞，不用再去下载各种编译器了，[详细文档](https://rustprojectprimer.com/building/cross.html)

	5. 开始编译配置编译
```bash
## 在项目根目录下建立配置文件 .cargo/config.toml
hello git:(master) cat <<EOF >> .cargo/config.toml
[target.aarch64-unknown-linux-gnu]
linker = "aarch64-linux-gnu-gcc"
[target.x86_64-unknown-linux-gnu]
linker = "x86_64-linux-gnu-gcc"
EOF

hello git:(master) ✗ cargo build --target x86_64-unknown-linux-gnu
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.03s
```
成功了 🏅 MacOS是最好的开发平台，😄这就解决了

**好景不长**

随着业务的迭代，新增了`mysql mqtt kafka websocket influxdb ` 统统都来了，有一些库依赖了 `openssl` ，这鸟库是c语言开发的，rust 对他做了一层接口包装使用，当我们在编译时候会使用
`pkg-config` 做检查，前期我们被这个困扰了很久， 后面发现在 Rust 中，有一种**vendored 模式**主要用于 **Rust 构建依赖的 C/C++ 库**（通常是 openssl、libssh2、ring 等），或者在使用 cargo 的时候想把所有依赖“本地化”，不依赖系统库或外部网络。

比如openssl 我们可以使用

```
openssl-sys = { version = "0.9.90", features = ["vendored"] }
```

这样交叉编译也能成功。但是这样包会很大，因为他会把这个包打包进去，不使用宿主机的 `openssl` ，

`vendored` 也不是所有的平台都能编译成功，我就遇到 `ubuntu` 中编译 `armv7` 编译报错，当然我是使用的 `zig cc` 来编译的，其他平台 `zig cc` 都能成功


**最好的解决方案 使用 [cross](https://github.com/cross-rs/cross)

cross 是一个由 Rust 社区开发的工具，旨在简化 Rust 项目的交叉编译过程。它通过 Docker 或 Podman 容器提供一个统一的构建环境，使得在不同平台之间构建 Rust 项目变得更加容易

这个工具完美的解决了我们的问题，在交叉编译的时候，提取安装一些包，比如我编译 x84 平台我缺少这个平台的 openssl ，我可以在编译器把 openssl 包安装好。

🧩 配置选项
cross 提供了多种配置方式，以满足不同的需求：
- 在 Cross.toml 中配置：
```bash
[build]
build-std = false # do not build the std library. has precedence over xargo
xargo = true # enable the use of xargo by default
zig = false # do not use zig cc for the builds
default-target = "x86_64-unknown-linux-gnu" # use this target if none is 
pre-build = [ # additional commands to run prior to building the package
"dpkg --add-architecture $CROSS_DEB_ARCH",
"apt-get update && apt-get --assume-yes install libssl-dev:$CROSS_DEB_ARCH"
]
```

- 使用 Cross.toml 文件：
    在项目根目录创建 Cross.toml 文件，进行配置

**🧪实验步骤
1. 在 macos m1 中开始编译

```bash
 hello git:(master) ✗ cross build --target x86_64-unknown-linux-gnu                         
[cross] warning: found unused key(s) in Cross configuration:
 > build.zig
[+] Building 1.6s (2/2) FINISHED                                                                                                                              docker:orbstack
 => [internal] load build definition from Dockerfile.x86_64-unknown-linux-gnu-custom                                                                                     0.0s
 => => transferring dockerfile: 246B                                                                                                                                     0.0s
 => ERROR [internal] load metadata for ghcr.io/cross-rs/x86_64-unknown-linux-gnu:0.2.5                                                                                   1.5s
------
 > [internal] load metadata for ghcr.io/cross-rs/x86_64-unknown-linux-gnu:0.2.5:
------
Dockerfile.x86_64-unknown-linux-gnu-custom:2
--------------------
   1 |     
   2 | >>>                 FROM ghcr.io/cross-rs/x86_64-unknown-linux-gnu:0.2.5
   3 |                     ARG CROSS_DEB_ARCH=
   4 |                     ARG CROSS_CMD
--------------------
ERROR: failed to solve: ghcr.io/cross-rs/x86_64-unknown-linux-gnu:0.2.5: failed to resolve source metadata for ghcr.io/cross-rs/x86_64-unknown-linux-gnu:0.2.5: no match for platform in manifest: not found

View build details: docker-desktop://dashboard/build/orbstack/orbstack/okqylnx30ifvicoynlk4ymqzr
Error: 
   0: could not run container
   1: when building custom image
   2: when pre-building
   3: `docker build --label 'org.cross-rs.for-cross-target=x86_64-unknown-linux-gnu' --label 'org.cross-rs.workspace_root=/Users/rongts/hello' --tag cross-custom-hello:x86_64-unknown-linux-gnu-fd9ec-pre-build --build-arg 'CROSS_CMD=dpkg --add-architecture $CROSS_DEB_ARCH
      apt-get update && apt-get --assume-yes install libssl-dev:$CROSS_DEB_ARCH' --build-arg 'CROSS_DEB_ARCH=amd64' --file /Users/rongts/hello/target/x86_64-unknown-linux-gnu/Dockerfile.x86_64-unknown-linux-gnu-custom /Users/rongts/hello` failed with exit status: 1

Note: CROSS_CMD=dpkg --add-architecture $CROSS_DEB_ARCH
apt-get update && apt-get --assume-yes install libssl-dev:$CROSS_DEB_ARCH
```

我擦讷！！

仔细看错误

```bash
hello git:(master) ✗ cross build --target x86_64-unknown-linux-gnu
[cross] warning: found unused key(s) in Cross configuration:
 > build.zig
[+] Building 2.6s (2/2) FINISHED                                                                                                                              docker:orbstack
 => [internal] load build definition from Dockerfile.x86_64-unknown-linux-gnu-custom                                                                                     0.0s
 => => transferring dockerfile: 246B                                                                                                                                     0.0s
 => ERROR [internal] load metadata for ghcr.io/cross-rs/x86_64-unknown-linux-gnu:0.2.5                                                                                   2.5s
------
 > [internal] load metadata for ghcr.io/cross-rs/x86_64-unknown-linux-gnu:0.2.5:
------
Dockerfile.x86_64-unknown-linux-gnu-custom:2
--------------------
   1 |     
   2 | >>>                 FROM ghcr.io/cross-rs/x86_64-unknown-linux-gnu:0.2.5
   3 |                     ARG CROSS_DEB_ARCH=
   4 |                     ARG CROSS_CMD
--------------------
ERROR: failed to solve: ghcr.io/cross-rs/x86_64-unknown-linux-gnu:0.2.5: failed to resolve source metadata for ghcr.io/cross-rs/x86_64-unknown-linux-gnu:0.2.5: no match for platform in manifest: not found 

View build details: docker-desktop://dashboard/build/orbstack/orbstack/ra8za4nikly8u2uu1maqbjxfd
Error: 
   0: could not run container
   1: when building custom image
   2: when pre-building
   3: `docker build --label 'org.cross-rs.for-cross-target=x86_64-unknown-linux-gnu' --label 'org.cross-rs.workspace_root=/Users/rongts/hello' --tag cross-custom-hello:x86_64-unknown-linux-gnu-fd9ec-pre-build --build-arg 'CROSS_CMD=dpkg --add-architecture $CROSS_DEB_ARCH
      apt-get update && apt-get --assume-yes install libssl-dev:$CROSS_DEB_ARCH' --build-arg 'CROSS_DEB_ARCH=amd64' --file /Users/rongts/hello/target/x86_64-unknown-linux-gnu/Dockerfile.x86_64-unknown-linux-gnu-custom /Users/rongts/hello` failed with exit status: 1

Note: CROSS_CMD=dpkg --add-architecture $CROSS_DEB_ARCH
apt-get update && apt-get --assume-yes install libssl-dev:$CROSS_DEB_ARCH
```

仔细看错误没有 `m1` 平台的镜像

```bash
➜  hello git:(master) ✗ docker manifest inspect ghcr.io/cross-rs/aarch64-unknown-linux-gnu:0.2.5
{
   "schemaVersion": 2,
   "mediaType": "application/vnd.oci.image.index.v1+json",
   "manifests": [
      {
         "mediaType": "application/vnd.oci.image.manifest.v1+json",
         "size": 3716,
         "digest": "sha256:9e5d86740280e021e5f372afcad2eda7367676f33ec40085b49ee88a2652cfe5",
         "platform": {
            "architecture": "amd64",
            "os": "linux"
         }
      },
      {
         "mediaType": "application/vnd.oci.image.manifest.v1+json",
         "size": 566,
         "digest": "sha256:8fc00e4231dfdca09dafab72f9e0cf3f1243dbc87667fe39c4d5d3d0148b212d",
         "platform": {
            "architecture": "unknown",
            "os": "unknown"
         }
      }
   ]
}
```

果然他是 amd64 就是x86架构的

🧍‍♀️解决方案，当我们执行 `cross build --target x86_64-unknown-linux-gnu` 失败的时候，他会在 target/x86_64-unknown-linux-gnu/Dockerfile.x86_64-unknown-linux-gnu-custom` 留下一个 dockerfile 我们给予这个 docker 重新编译，如何使用我们编译好的镜像让 `cross` 给我们打包

target/x86_64-unknown-linux-gnu/Dockerfile.x86_64-unknown-linux-gnu-custom
```Dockerfile
FROM x86_64-unknown-linux-gnu-pre-build:macos
ARG CROSS_DEB_ARCH==
ARG CROSS_CMD
RUN eval "${CROSS_CMD}"
```

```bash
 hello git:(master) ✗ docker build --platform=linux/amd64 \
  --build-arg CROSS_DEB_ARCH=amd64 \
  --build-arg CROSS_CMD="dpkg --add-architecture amd64 && apt-get update && apt-get install --assume-yes libssl-dev:amd64" \
  -f target/x86_64-unknown-linux-gnu/Dockerfile.x86_64-unknown-linux-gnu-custom \
  -t x86_64-unknown-linux-gnu-pre-build:macos \
  /Users/rongts/hello
[+] Building 0.1s (6/6) FINISHED                                                                                            docker:orbstack
 => [internal] load build definition from Dockerfile.x86_64-unknown-linux-gnu-custom                                                   0.0s
 => => transferring dockerfile: 246B                                                                                                   0.0s
 => [internal] load metadata for ghcr.io/cross-rs/x86_64-unknown-linux-gnu:0.2.5                                                       0.0s
 => [internal] load .dockerignore                                                                                                      0.0s
 => => transferring context: 2B                                                                                                        0.0s
 => [1/2] FROM ghcr.io/cross-rs/x86_64-unknown-linux-gnu:0.2.5                                                                         0.0s
 => CACHED [2/2] RUN eval "dpkg --add-architecture amd64 && apt-get update && apt-get install --assume-yes libssl-dev:amd64"           0.0s
 => exporting to image                                                                                                                 0.0s
 => => exporting layers                                                                                                                0.0s
 => => writing image sha256:c20ec5cc1c9d133c66c9d99ac59c706fe5b51c167e62aacb3cde1ec42794cf51                                           0.0s
 => => naming to docker.io/library/aarch64-unknown-linux-gnu-custom-m1:aarch64-unknown-linux-gnu-m1-pre-build                          0.0s

View build details: docker-desktop://dashboard/build/orbstack/orbstack/0x2b1wz6t61dxebctjucwqrjv
```

```bash

➜  hello git:(master) ✗ docker images                        
REPOSITORY                                       TAG                                         IMAGE ID       CREATED         SIZE
x86_64-unknown-linux-gnu-custom-m1               x86_64-unknown-linux-gnu-m1-pre-
```

 Cross.toml 配置文件
```bash
[target.aarch64-unknown-linux-gnu]
image = "cross-custom-hello:aarch64-unknown-linux-gnu-fd9ec-pre-build"
  
[target.x86_64-unknown-linux-gnu]
image = "x86_64-unknown-linux-gnu-pre-build:macos"
```


```执行编译
hello git:(master) ✗ cross build --target x86_64-unknown-linux-gnu
WARNING: The requested image's platform (linux/amd64) does not match the detected host platform (linux/arm64/v8) and no specific platform was requested
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.42s
```

这里有 `warning` 搞不清楚容器是哪个平台, 下面我们加上平台

 ```bash
 hello git:(master) ✗ CROSS_CONTAINER_OPTS="--platform linux/amd64" cross build --target x86_64-unknown-linux-gnu
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.62s
 ```

完结🪸

### Q/A

> **为什么在arm中可以执行x86的容器?

cross 就是用 **Docker + QEMU** 封装目标架构环境，让你在不同架构主机上也能轻松编译 Rust 目标


