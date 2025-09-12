
## **🔹 Flutter 在 Android 系统中的运行总结**

### **1. 应用启动**
- 用户点击 Launcher 图标或通过系统启动应用
- **AMS (ActivityManagerService)** 接收到请求
- Zygote 进程 fork 出一个新的进程作为 Flutter 应用
- ART（Android Runtime）在新进程中初始化应用

### **2. FlutterActivity 初始化**
- ART 执行 **FlutterActivity / FlutterApplication** 的 Java/Kotlin 代码
- 初始化 **Flutter Engine**
- 加载 Dart 代码（AOT 编译后的机器码，或开发模式下的 JIT 字节码）
- 初始化渲染管线和 Platform Channel

### **3. Flutter Engine 启动**
- **C++ 实现的核心引擎**
- 功能：
    - 执行 Dart 代码逻辑
    - 处理触摸、手势、事件分发
    - 调用 Android 系统服务（通过 Platform Channel → Java/Kotlin → ART → Framework）
    - 使用 **Skia 引擎** 渲染 UI
        
### **4. UI 渲染**
- Flutter Engine 将 UI 绘制到 **Surface**
- Android 系统的 **SurfaceFlinger** 合成显示到屏幕
- 用户看到的界面就是 Flutter 绘制的结果

### **5. 系统交互**
- Flutter 通过 **Platform Channel** 调用系统服务：
    - 相机、传感器、文件、通知等
- Java/Kotlin 层在 ART 上执行
- 最终由 Linux 内核访问硬件

## **🔹 总体执行链路（简化图示）**

```bash
用户点击应用
      ↓
AMS (ActivityManagerService) fork 新进程
      ↓
ART 加载 FlutterActivity (Java/Kotlin)
      ↓
FlutterActivity 初始化 Flutter Engine
      ↓
Flutter Engine 执行 Dart 代码
      ↓
Flutter Engine 使用 Skia 绘制 UI
      ↓
SurfaceFlinger 显示到屏幕
      ↓
Platform Channel 调用系统服务
```

### **🔹 核心理解**
1. **Flutter 应用不是直接被 Android 系统渲染的**
    - 系统只是提供窗口、Surface、事件和系统服务
        
2. **Flutter Engine 才是渲染核心**
    - Dart 逻辑 + Skia 绘图
    
3. **ART 的作用**
    - 运行系统服务和 FlutterActivity 的 Java 层代码
    - 作为桥梁连接 Flutter Engine 与 Android Framework