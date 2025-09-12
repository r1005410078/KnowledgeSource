## **🔹 1. SDK 是什么**

- SDK = **Software Development Kit**，软件开发工具包
- Android SDK 就是 **开发 Android 应用的一整套工具和库**
- 你写 Android 程序（Java、Kotlin、Flutter），最终都要依赖 SDK
  

它相当于：
- 给开发者准备的“积木盒子”
- 里面放着：编译器、工具、类库、调试器、模拟器镜像

---

## **🔹 2. SDK 的主要作用**

1. **API 接口**
    - 提供 Android 系统功能的 Java/Kotlin 接口
    - 例如：
        - android.view.View（UI 控件）
        - android.location.LocationManager（定位服务）
        - android.media.MediaPlayer（多媒体）
    
2. **编译工具**
    - aapt → 打包资源
    - aidl → 生成跨进程通信代码
    - dx/d8 → 把 Java 字节码转成 DEX
    - zipalign → APK 优化
        
    
3. **调试工具**
    - adb → 设备调试、日志、安装 APK
    - emulator → 启动模拟器
    
4. **平台库**
    - 每个 Android 版本（API Level）对应的 framework 库
    - 例如：API 33 = Android 13 (Tiramisu)
    - 你编译时依赖这些库，保证应用能调用对应版本的功能

---

## **🔹 3. 为什么有很多版本的 SDK**

- Android 每个大版本升级（Android 5、6、7…13…），都会引入新的 API
- Google 用 **API Level** 来标记 SDK 版本
    - API 21 = Android 5.0 (Lollipop)
    - API 23 = Android 6.0 (Marshmallow)
    - API 33 = Android 13 (Tiramisu)
        
    
- 如果你的应用要用新功能 → 必须下载对应 SDK
    
👉 所以 Android SDK 是 **版本化的 API + 工具包**，保证开发者可以针对不同 Android 系统版本写应用。

---

## **🔹 4. 关系梳理**

- **Android 系统** = 运行环境（手机上的系统）
    
- **Android SDK** = 面向开发者的接口和工具（写应用用的）
    
- **Android NDK** = 面向 C/C++ 的接口（写底层库/游戏引擎用的）


那我使用的新的SDK 那么对于旧机器要重新基于旧的SDK 重新写？


## **🔹 1. 新 SDK ≠ 只能跑在新系统**

- 你用 **最新的 SDK**（比如 API 34 / Android 14）写应用，并不会导致旧手机直接不能运行。
- 关键在于：
    - **编译 SDK 版本（compileSdkVersion）**
    - **最小支持版本（minSdkVersion）**
    - **目标版本（targetSdkVersion）**
        
    

---

## **🔹 2. 这三个版本号的作用**

1. **compileSdkVersion**
    - 你在编译时使用的 SDK
    - 决定你能调用哪些 API（比如 Android 13 的新 API）
        
2. **minSdkVersion**
    - 应用能安装的最低 Android 系统版本
    - 如果 minSdk = 21 → Android 5.0 以下的机器不能安装
    
3. **targetSdkVersion**
    - 告诉系统你主要针对哪个版本优化
    - 系统会对旧版本 App 开启“兼容模式”
    - 比如 targetSdk < 30 时，可能默认允许某些权限（新版本则强制申请）
    

---

## **🔹 3. 向下兼容的策略**

- **旧系统上运行时**：
    
    - 如果调用了不存在的新 API → 会崩溃
    - 所以要用 Build.VERSION.SDK_INT 做判断
    
```java
if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
    // 调用 Android 13 的新 API
} else {
    // 用旧 API 或者跳过
}
```


- **Google 提供 support libraries / AndroidX**
    
    - 把很多新特性“向下兼容”实现
    - 比如 RecyclerView、AppCompatActivity
    - 这样你可以用新 SDK 写代码，但它们能在旧系统上运行

## **🔹 4. 举例说明**

- 你用 **API 34 (Android 14)** SDK 写一个应用：
    - compileSdkVersion = 34
    - minSdkVersion = 23（Android 6.0 起）
    - targetSdkVersion = 34
        

👉 那么这个应用可以在 **Android 6.0 ~ 14** 之间的设备安装运行。
👉 但如果你调用了 Android 13/14 独有的 API，要加兼容判断。

---

## **🔹 5. 总结**

- 不需要为旧机器“重新基于旧 SDK 写应用”
    
- 只要设置好 **minSdkVersion**，并通过 **兼容性代码 + AndroidX** 处理差异
    
- 就能用一个代码工程同时支持新旧设备

## **Android SDK 版本关系图**


```bash
                 ┌─────────────────────────────┐
                 │   compileSdkVersion         │
                 │   - 用哪个 SDK 来编译代码    │
                 │   - 决定能用哪些 API        │
                 └─────────────────────────────┘
                                │
                                ▼
 ┌─────────────────────────────┐
 │   minSdkVersion             │
 │   - 应用能安装的最低系统版本 │
 │   - 低于此版本 → 无法安装    │
 └─────────────────────────────┘
                                │
                                ▼
 ┌─────────────────────────────┐
 │   targetSdkVersion          │
 │   - 告诉系统主要适配的版本   │
 │   - 系统根据它决定兼容模式   │
 └─────────────────────────────┘
```

