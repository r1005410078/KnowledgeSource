
# **🔹 一、Android 系统本身是怎么运行起来的？**

  

Android 基于 **Linux 内核**，所以它的启动流程类似于一个嵌入式 Linux 系统：
1. **Bootloader（引导程序）**
    - 手机开机时，Bootloader 被执行。
    - 它会初始化硬件（CPU、内存、存储等）。
    - 然后把控制权交给 **Linux 内核**。
    
2. **Linux 内核启动**
    - 内核负责驱动硬件：显示、触摸屏、相机、网络等。
    - 初始化系统进程（比如电源管理、Binder 进程间通信）。
    
3. **init 进程**
    - 第一个用户态进程（/init），读取 init.rc 脚本。
    - 启动关键守护进程：如 zygote、surfaceflinger、mediaserver。
    
4. **Zygote 进程（孵化器）**
    - 这是 Android 特有的，作用是：
        - 加载 Java 虚拟机（ART，Android Runtime）。
        - 预加载常用类和资源            
        - 作为孵化器，通过 **fork** 生成应用进程。

5. **SystemServer 进程**
    - 由 Zygote 启动。
    - 负责启动 **Android Framework 的核心服务**：
        - ActivityManagerService（AMS）：管理四大组件和应用生命周期。
        - WindowManagerService（WMS）：窗口管理。
        - PackageManagerService（PMS）：App 安装与管理。
        - 其他服务（电池、网络、通知……）。

6. **Launcher（桌面应用）**
    - AMS 启动 Launcher（相当于 Android 的桌面）。
    - 用户在 Launcher 上点图标，才会启动具体的 App。

---

# **🔹 二、Android App 是怎么运行起来的？**
当你点开一个 App 图标时：
1. **Launcher 通过 Binder 调用 AMS**
    - 请求启动某个应用的 MainActivity。
    
2. **AMS 与 Zygote 通信**
    - AMS 发现该 App 没有进程，就通过 **Socket 请求 Zygote fork 一个新进程**。
    - 新进程里加载 App 的代码和资源。
    
3. **应用进程启动**
    - 新进程启动后，会先运行一个 ActivityThread。
    - ActivityThread 通过 Binder 跟 AMS 通信，接收“启动 Activity”的指令    
    
4. **Activity 生命周期回调**
    - ActivityThread 调用开发者写的 Activity.onCreate()，界面开始绘制。
    - 同时通过 WindowManager 和 SurfaceFlinger 把界面显示到屏幕上。
    
5. **用户看到应用界面**
    - 至此，一个 App 才真正“运行起来”。

# **🔹 三、运行环境**

Android App 运行在 **ART（Android Runtime）虚拟机** 上：
- Java/Kotlin 源码 → 编译成字节码（.class → .dex）。
- dex 文件安装时转换为 **oat/odex**，存储在设备上。
- 运行时由 ART 执行，部分热点代码会 JIT/AOT 编译成本地指令，提升性能。


- **AMS 是什么（ActivityManagerService）**
- **AMS 怎么让你写的 Kotlin 代码真正跑起来的**

# **🔹 1. AMS 是什么？**
**AMS（ActivityManagerService）** 是 Android Framework 里最核心的服务之一，运行在 **SystemServer 进程**中。

它的主要职责是：
- 管理 **四大组件**（Activity、Service、BroadcastReceiver、ContentProvider）的生命周期。
- 负责 **应用进程管理**（启动、切换、回收）。
- 接收 **Launcher/系统/应用的请求**，并协调 Zygote、WMS 等其他服务。

可以把 AMS 看成 Android 系统的大总管：
👉 谁要启动 Activity，谁要关掉 Service，都必须通过 AMS 来调度。

# **🔹 2. AMS 怎么执行 Kotlin 代码？**
你在 Android Studio 写的 **Kotlin 代码**，本质上要经历以下几个阶段：

### **（1）编译阶段**
- Kotlin 源码（.kt） → 编译成 Java 字节码（.class）。
- Gradle 插件把所有字节码打包成 **Dex 文件**（.dex）。
- 打包进 APK，安装到手机时，Dex 文件会被 ART 处理（可能转为 OAT/odex）。

---
### **（2）启动 App 流程

当你点开 App 图标时：
1. **Launcher 请求 AMS**
    - Launcher 通过 Binder 调用 AMS，请求启动 com.xxx.MainActivity。
    
2. **AMS 找 Zygote fork 进程**
    - AMS 发现你的 App 没有进程，就通过 **Socket** 请求 Zygote fork 出一个新进程。
    - fork 出的进程加载 app_process，然后运行 ActivityThread.main()。
    
3. **ActivityThread 启动应用主线程**
    - ActivityThread 是应用的入口类（在你的 App 进程里运行）。
    - 它启动一个 **Looper/MessageQueue**，形成 Android 的主线程（UI 线程）。

-----

### **（3）加载和执行你的 Kotlin 代码**
1. **AMS 通知 ActivityThread 启动 Activity**
    - AMS 通过 Binder 通知新进程：“启动 MainActivity”。
    - 进程内的 ActivityThread 收到消息，调用 Instrumentation.newActivity() 用 **反射** 实例化 MainActivity。
    
2. **调用生命周期方法**
    - 接着调用你的 MainActivity.onCreate()。
    - 此时你写的 Kotlin 代码（UI 初始化、事件绑定等）就在 **UI 线程**上开始执行。
    
3. **ART 执行 Kotlin 编译后的字节码**
    - 你写的 Kotlin 代码最终是 .dex 字节码，运行时由 **ART (Android Runtime)** 解释/编译成 ARM64 的机器码，然后在 CPU 上执行。

# **🔹 3. 总结类比**

可以这样理解：
- **AMS**：像“总调度员”，决定哪个应用进程该创建，哪个 Activity 该跑。
- **ActivityThread**：是“App 的管家”，接收 AMS 的命令，反射加载你的 Activity 类。
- **ART**：是“翻译器”，把 Kotlin 编译好的字节码翻译成 CPU 能跑的指令。
- **最终结果**：你的 Kotlin 代码就这样被系统一层层托管，最后在 ARM CPU 上执行。


ART 又是什么

# **🔹 1. ART 是什么？**
**ART = Android Runtime**
- 它是 Android 系统里的 **应用运行时环境**。
- 用来执行 Android App 的字节码（Dex 格式）。
- 运行在每个应用进程中（不是单独一个进程，而是每个 App 都有一份）。

👉 可以理解成：
- 你写的 Kotlin/Java 代码不会直接变成 CPU 能懂的机器码。
- 它先被编译成 .dex 文件，安装到设备时交给 ART。
- ART 再把这些 .dex 转换成 CPU 可以执行的 **本地机器码**。

早期 Android 用的是 **Dalvik VM**，Android 5.0 之后，谷歌用 **ART** 取代了它。
区别在于：

| **特点** | **Dalvik**                 | **ART**                 |
| ------ | -------------------------- | ----------------------- |
| 执行方式   | **JIT**（Just-In-Time，即时编译） | **AOT + JIT**（预编译+即时编译） |
| 安装速度   | 快（只拷贝 dex）                 | 稍慢（可能要预编译）              |
| 启动速度   | 慢（边运行边解释）                  | 快（提前编译好）                |
| 内存/电量  | 耗电多、效率低                    | 更省电，性能更好                |

# **🔹 3. ART 是怎么执行 Kotlin 代码的？**

流程大概是这样：
1. **源码编译**
    - Kotlin 源码（.kt） → Java 字节码（.class）。
    - Gradle + D8 把所有 .class 转成 .dex 文件。
    
2. **安装时处理**
    - ART 把 .dex 优化成 .oat/.odex（机器码缓存）。
    - 新版本 Android 还会用 **Profile-Guided Compilation**：先运行，再优化热点代码。
        
3. **运行时**
    - App 启动时，ART 把 dex/oat 加载到内存。
    - 热点代码由 **JIT 编译器**即时优化成本地 ARM64 指令。
    - CPU 直接执行这些本地机器码。

👉 也就是说：**ART 就是把 Dex 翻译成 ARM64 的 0 和 1，交给 CPU 跑**。

# **🔹 4. 类比**
- **AMS**：调度员，告诉谁该跑。
- **ActivityThread**：应用管家，帮你创建 Activity。
- **ART**：翻译官，把 Kotlin/Java 编译后的字节码翻译成本地机器码。
- **CPU**：工人，真正干活，执行指令。

ART 跟 java 虚拟机的关系

# **🔹 1. JVM 是什么？**
- JVM（Java Virtual Machine）是运行 Java 程序的标准虚拟机。
- 它执行的是 **Java 字节码（.class/.jar）**。
- 特点：
    - 平台无关（一次编译，到处运行）。
    - 运行时用 **JIT 编译器** 把字节码翻译成机器码。
    - 桌面 Java、服务器 Java（Tomcat、Spring）都跑在 JVM 上。
    
# **🔹 2. ART 是什么？**
- ART（Android Runtime）是 Google 为 **Android 平台** 专门设计的运行时。
- 它执行的是 **Dex 字节码（.dex/.apk 里有的）**。
- 特点：
    - 专门针对 **移动设备优化**（内存有限、电池有限）。
    - 使用 **AOT（Ahead-of-Time 预编译）+ JIT（即时编译）+ Profile 指引优化**。
    - 每个 App 都运行在自己进程里的 ART 实例上。

# **🔹 3. 关系**

可以这么理解：
- **JVM 是 Java 世界的“标准虚拟机”**。
- **ART 是 Android 世界的“定制虚拟机”**，本质上是 JVM 的一个“亲戚/变体”。

它们的主要区别是执行的“字节码格式”不同：


| **对比点** | **JVM**                        | **ART**                                  |
| ------- | ------------------------------ | ---------------------------------------- |
| 输入字节码   | .class（Java 编译输出）              | .dex（Dalvik Executable，适合移动端）            |
| 执行环境    | 桌面/服务器（PC、Linux、Windows）       | 手机（Android 系统，基于 Linux 内核）               |
| 优化方式    | JIT                            | AOT + JIT + Profile Guided               |
| 运行时库    | Java Standard Library (rt.jar) | Android SDK（裁剪过的 Java API + Android API） |
# **🔹 4. 为什么 Android 不直接用 JVM？**

原因有三：
1. **性能和体积问题**
    - JVM 设计时考虑的是 PC/服务器，比较重。
    - Android 设备 CPU/内存/电量有限，需要更轻量的运行时。
    
2. **字节码优化**
    - Java .class 文件是面向 PC 的，不适合移动端。
    - Android 重新设计了 **Dex（Dalvik Executable）格式**，更紧凑，支持寄存器架构。
    
3. **系统集成**
    - Android 把运行时和系统框架（AMS、WMS、Binder 等）深度绑定。
    - JVM 无法直接满足移动端的这种架构需求。

# **🔹 5. 类比总结**
- **JVM**：通用的 Java 运行时，用于 PC/服务器。
- **ART**：专门为 Android 优化的 Java 运行时，跑 Dex 文件。


AOSP 是啥

# **🔹 1. AOSP 是什么？**

**AOSP = Android Open Source Project（安卓开源项目）**
- 这是 Google 维护的 **官方 Android 开源代码库**。
- 里面包含了 **Android 系统的源代码**（从内核接口到 Framework 到系统应用）。
- 所有人都可以下载、编译、定制，搭建属于自己的 Android 系统。
  

换句话说：
👉 你手机里跑的 Android 系统，本质上都是 **基于 AOSP 修改和定制的版本**。
比如：小米的 MIUI、华为的 EMUI、OPPO 的 ColorOS 都是在 AOSP 基础上加料的。

# **🔹 2. AOSP 里面有什么？**

AOSP 是一个超大的代码仓库，主要包括：
- **系统服务（Framework 层）**
    - ActivityManagerService (AMS)
    - WindowManagerService (WMS)
    - PackageManagerService (PMS)
        👉 这些就是 Android 的“中枢神经系统”。
        
- **应用运行环境**
    - **ART（Android Runtime）**：负责运行 Dex 字节码。
- **系统应用**
    - 桌面 (Launcher)
    - 设置 (Settings)
    - 电话、短信等基础 App。
        
- **工具链**
    - 编译系统（基于 Make / Ninja）
    - 模拟器支持

⚡ 唯独 **Google 专有应用（GMS，如 Play 商店、Google 地图）不在 AOSP 里**，因为它们不是开源的


 AOSP 跟 linux 又是什么关系

### **1. Linux 和 Android 的关系**
- **Linux 内核**：是一个操作系统内核，可以管理硬件资源（CPU、内存、驱动、进程调度等等）。
- **Android**：是一个基于 **Linux 内核** 的操作系统，它在 Linux 内核之上加了很多 Android 专属的东西，比如：
    - **HAL（硬件抽象层）**
    - **Binder（进程间通信机制）**
    - **ART（运行应用的虚拟机）**
    - **Framework（系统服务，比如 AMS、WMS）**
    - **系统应用（Settings、Launcher 等）**
  

👉 所以，**Android 系统的底层就是 Linux 内核**，但是它在内核之上堆了一整套 Android 自己的框架。

你在 Linux 里“跑 Android”，其实就是在 Linux 内核上加载 **Android 系统**，而不是单独跑一个 app。


### **2. AOSP 是什么**
- **AOSP（Android Open Source Project）** = **Android 的开源代码项目**。
- Google 把 Android 的大部分系统源码开源，放在 [android.googlesource.com](https://android.googlesource.com)，这就是 AOSP。
- 你能下载 AOSP，把它编译成一个完整的 Android 系统镜像（system.img + boot.img + vendor.img 等等），然后刷到手机、模拟器，或者运行在特定硬件上。

### **3. 为什么会混淆 Linux 和 AOSP**
- 有人说“在 Linux 里跑 Android”，指的是：
    1. 直接在 **Linux 内核** 上跑 Android 系统（就是手机上的 Android）。
    2. 或者在 **普通 Linux 桌面环境里跑一个 Android 模拟器**（比如 Android Emulator、Waydroid、Anbox）。
    
- 所以：
    - **Linux ≠ Android**
    - **Linux 是内核**
    - **Android 是基于 Linux 内核的完整操作系统**
    - **AOSP 是 Android 的源代码**