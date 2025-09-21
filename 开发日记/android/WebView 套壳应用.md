## 基础代码

`MainActivity.kt`

```kotlin
package com.meida.greetingcard  

import android.os.Bundle  
import android.view.ViewGroup  
import android.webkit.WebChromeClient  
import android.webkit.WebSettings  
import android.webkit.WebView  
import android.webkit.WebViewClient  
import androidx.activity.ComponentActivity  
import androidx.activity.OnBackPressedDispatcher  
import androidx.activity.addCallback  
import androidx.activity.compose.setContent  
import androidx.compose.foundation.layout.WindowInsets  
import androidx.compose.foundation.layout.asPaddingValues  
import androidx.compose.foundation.layout.fillMaxSize  
import androidx.compose.foundation.layout.padding  
import androidx.compose.foundation.layout.safeDrawing  
import androidx.compose.material3.Surface  
import androidx.compose.material3.Text  
import androidx.compose.runtime.*  
import androidx.compose.ui.Modifier  
import androidx.compose.ui.graphics.Color  
import androidx.compose.ui.tooling.preview.Preview  
import androidx.compose.ui.unit.dp  
import androidx.compose.ui.viewinterop.AndroidView  
import com.meida.greetingcard.ui.theme.GreetingCardTheme  
  
class MainActivity : ComponentActivity() {  
    override fun onCreate(savedInstanceState: Bundle?) {  
        super.onCreate(savedInstanceState)  
  
        setContent {  
            // "http://192.168.2.10:3001"  
            WebViewSafeScreen(  
                "http://114.55.227.206:3000",  
                onBack = { finish() },  
                backPressedDispatcher = onBackPressedDispatcher  
            )  
        }  
  
    }  
}  
  
@Composable  
fun WebViewSafeScreen(  
    url: String,  
    onBack: () -> Unit,  
    backPressedDispatcher: OnBackPressedDispatcher  
) {  
    var webViewRef by remember { mutableStateOf<WebView?>(null) }  
  
    // 系统返回键处理  
    DisposableEffect(backPressedDispatcher) {  
        val callback = backPressedDispatcher.addCallback {  
            if (webViewRef?.canGoBack() == true) {  
                webViewRef?.goBack()  
            } else {  
                onBack()  
            }  
        }  
        onDispose { callback.remove() }  
    }  
    AndroidView(  
        modifier = Modifier  
            .fillMaxSize()  
            .padding(WindowInsets.safeDrawing.asPaddingValues()), // 安全区域  
        factory = { context ->  
            WebView(context).apply {  
                // 注入 JS 修正 vh 高度  
                layoutParams = ViewGroup.LayoutParams(  
                    ViewGroup.LayoutParams.MATCH_PARENT,  
                    ViewGroup.LayoutParams.MATCH_PARENT  
                )  
  
                webViewClient = WebViewClient()  
                webChromeClient = WebChromeClient() // 可根据需要添加 onReceivedTitle  
                settings.apply {  
                    javaScriptEnabled = true                 // JS 支持  
                    domStorageEnabled = true                 // DOM Storage / localStorage  
                    allowFileAccess = true                   // 文件访问  
                    allowContentAccess = true                // 内容访问  
                    useWideViewPort = true                   // 支持 viewport                    setGeolocationEnabled(true)              // 支持定位  
                    mixedContentMode = WebSettings.MIXED_CONTENT_ALWAYS_ALLOW // 混合内容  
                    textZoom = 100  
                    userAgentString = "Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0 Mobile Safari/537.36"  
                }  
  
                loadUrl(url)  
                webViewRef = this  
            }  
        }    )  
}
```

`res/network_security_config.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>  
<network-security-config>  
    <!-- 全局允许 HTTP -->    <domain-config cleartextTrafficPermitted="true">  
        <!-- 注意这里必须写 IP，不要写 http:// --><!--        <domain includeSubdomains="false">114.55.227.206</domain>-->  
        <domain includeSubdomains="false">192.168.2.10</domain>  
    </domain-config></network-security-config>
```

`manifests/AndroidManifest.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>  
<manifest xmlns:android="http://schemas.android.com/apk/res/android"  
    xmlns:tools="http://schemas.android.com/tools">  
    <!-- 网络权限 -->  
    <uses-permission android:name="android.permission.INTERNET"/>  
    <application
        android:usesCleartextTraffic="true"  
        android:allowBackup="true"  
        android:networkSecurityConfig="@xml/network_security_config"  
        android:dataExtractionRules="@xml/data_extraction_rules"  
        android:fullBackupContent="@xml/backup_rules"  
        android:icon="@mipmap/ic_launcher"  
        android:label="@string/app_name"  
        android:roundIcon="@mipmap/ic_launcher_round"  
        android:supportsRtl="true"  
        android:theme="@style/Theme.GreetingCard">  
        <activity  
	        android:name=".MainActivity"  
            android:exported="true"  
            android:label="@string/app_name"  
            android:theme="@style/Theme.GreetingCard">  
            <intent-filter> 
	            <action android:name="android.intent.action.MAIN" />  
                <category android:name="android.intent.category.LAUNCHER" />  
            </intent-filter>        
        </activity>    
    </application>
</manifest>
```

 🔧 **1. `android:usesCleartextTraffic="true"`

- 含义：是否允许 **明文 HTTP 通信**（非 HTTPS）。
- 默认：Android 9（API 28）以后，默认禁止明文流量，只允许 HTTPS。
- 设置 true → 允许 http:// 请求。
- 风险：不安全，容易被中间人攻击。
- 建议：开发/调试环境可以开，生产环境最好配合 network_security_config 精细控制。

----

 🔧  **2. `android:allowBackup="true"`

- 含义：允许用户通过 adb 或 Google 备份功能，备份/恢复应用数据。
- 默认：true。
- 风险：可能导致敏感数据被导出。
- 建议：如果你的应用有敏感信息（比如用户密码、token），设为 false。

----

 🔧 **3. `android:networkSecurityConfig="@xml/network_security_config"`

- 含义：引用 **网络安全配置文件**（位于 res/xml/network_security_config.xml）。
- 作用：
    - 控制哪些域名允许明文请求。
    - 是否信任某些自签名证书。
    ```xml
    <network-security-config>
	    <domain-config cleartextTrafficPermitted="true">
	        <domain>example.com</domain>
	    </domain-config>
	</network-security-config>
    ``` 

----

🔧 **4. `android:dataExtractionRules="@xml/data_extraction_rules"`

- 含义：指定 **数据提取规则**（Android 12+）。
- 作用：控制系统自动备份和迁移（如换手机时）的 **哪些数据可以被提取**。
- 示例：

```xml
<data-extraction-rules>
    <cloud-backup>
        <include domain="sharedpref" path="user_prefs.xml" />
        <exclude domain="database" path="cache.db" />
    </cloud-backup>
</data-extraction-rules>
```

----

🔧 **5 `android:fullBackupContent="@xml/backup_rules"`

- 含义：指定 **完整备份规则**（Android 6+）。
- 作用：告诉系统在 **adb backup** 或 Google 云备份时，哪些文件/目录需要包含或排除。
- 示例：
```xml
<full-backup-content>
    <include domain="file" path="important_data/" />
    <exclude domain="sharedpref" path="temp.xml" />
</full-backup-content>
```

🔧 **6. `android:icon="@mipmap/ic_launcher"**`

- 含义：应用的主图标（显示在桌面）。
- 位置：通常在 res/mipmap-*dpi/ic_launcher.png。
- 建议：用 Adaptive Icon（ic_launcher.xml + foreground/background 图层）。

---

 🔧 **7.  `android:label="@string/app_name"`
- 含义：应用显示名称。
- 来源：res/values/strings.xml → <string name="app_name">GreetingCard</string>。
- 作用：显示在 **桌面图标下方**，任务切换器标题等。

---

 🔧 **8. `android:roundIcon="@mipmap/ic_launcher_round"`

- 含义：应用的 **圆形图标**（主要用于 Android 7.1+ 圆形启动器图标）。
- 如果没有，系统会 fallback 到 android:icon。

---

🔧 **9.  `android:supportsRtl="true"`

- 含义：是否支持 **RTL（从右到左的语言）布局**（如阿拉伯语、希伯来语）。
- true → 系统会自动镜像布局。
- 建议：国际化应用保持 true，国内只用中文/英文可以不太在意。

--- 

 🔧 **10. `android:theme="@style/Theme.GreetingCard"`
- 含义：应用的默认 **主题样式**。
- 来源：res/values/styles.xml。
- 控制全局背景色、状态栏颜色、ActionBar、字体等。
- 示例：
```xml
<style name="Theme.GreetingCard" parent="Theme.Material3.DayNight">
    <item name="colorPrimary">@color/teal_700</item>
    <item name="android:statusBarColor">@color/black</item>
</style>
```

## **2. 安全区域显示**

- 用 setContentView(webView) 时，会覆盖整个屏幕。
- 如果需要和系统状态栏适配（安全区域），可以用 **ConstraintLayout + WebView**，然后 android:fitsSystemWindows="true"。
- Flutter/Compose 里则用 **SafeArea / Scaffold** 包裹。

## **3. 常见问题**

- **输入框无法输入**
    → 需要 android:windowSoftInputMode="adjustResize"（在 AndroidManifest.xml 中设置）。
- **CSS vh 不生效**
    → 在 WebView 必须 MATCH_PARENT，否则布局高度计算会出错。
- **签名错误**
    → 真机/模拟器安装时必须先签名 apk，否则报 INSTALL_PARSE_FAILED_NO_CERTIFICATES。
- **安装失败签名不一致**
    → 先卸载旧版本 adb uninstall com.package.name，再安装。
## **4. 真机 & 模拟器调试**
- **真机测试**：
    1. 手机开启「开发者模式」+「USB调试」。
    2. 用数据线连接电脑。
    3. 执行 adb devices 确认识别到设备。
    4. 执行 adb install app-release.apk 安装。
    
- **模拟器测试**：
    - Android Studio 自带 **AVD Manager**（Pixel 系列）。
    - 其他厂商模拟器（小米、华为）一般需要收费或在官方 SDK。
    - 免费替代：Bluestacks、Genymotion（个人可免费）、夜神模拟器（国内）。
    
## **5. 生产环境注意**

- WebView 并不是完整浏览器，和 Chrome/Safari 有差异。
- 一般需要设置 **User-Agent** 来兼容。
- 如果目标是 PWA/完整浏览器体验，推荐使用 **Chrome Custom Tabs** 或直接引导用户用浏览器。

## **5. Release key（签名配置**）****


1.   **`AndroidManifest.xml`**

**关键配置**

已经在上面加过注释，这里总结要点：
- **网络**：
    - android:usesCleartextTraffic="true" → 调试阶段允许 HTTP，生产建议 **强制 HTTPS** 或通过 network_security_config 控制。
    - android:permission.INTERNET → 必须。
    
- **安全**：
    - android:allowBackup="false"（生产建议关闭，避免用户数据被 adb 导出）。
    - android:fullBackupContent / android:dataExtractionRules → 只保留必要的数据。
    
- **显示**：
    - 图标：icon / roundIcon。
    - 名称：label。
    - 主题：theme。

---

 **2.** **build.gradle.kts**
 
**签名配置 (Release Key)**
  
你的项目是 **Gradle Kotlin DSL**，所以写法如下：

```kotlin
android {
    signingConfigs {
        create("release") {
            // 使用相对路径，避免写死绝对路径
            storeFile = file("my-release-key.jks")
            storePassword = "your-store-password"
            keyAlias = "my-key-alias"
            keyPassword = "your-key-password"
        }

    }

    buildTypes {
        getByName("release") {
            isMinifyEnabled = true // 启用混淆，减小包体
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
            signingConfig = signingConfigs.getByName("release") // 应用签名
        }
        getByName("debug") {
            // 调试包用默认 debug 签名
        }
    }
}
```

👉 注意：
- my-release-key.jks 放在 **app 目录下**，用 file("my-release-key.jks") 就是相对路径。
- 密码和 alias 建议不要直接写在代码里，可以放到 gradle.properties：

```kotlin
storePassword = project.property("MY_KEY_STORE_PASSWORD") as String
keyAlias = project.property("MY_KEY_ALIAS") as String
keyPassword = project.property("MY_KEY_PASSWORD") as String
```

 **3. 打包流程**

1. **生成签名文件**

```bash
keytool -genkey -v -keystore my-release-key.jks -keyalg RSA -keysize 2048 -validity 10000 -alias my-key-alias
```

2. **输出文件**：

    - APK → app/build/outputs/apk/release/app-release.apk
    - AAB → app/build/outputs/bundle/release/app-release.aab（推荐上传 Play Store）

3. **安装到设备**

![[Pasted image 20250913145425.png||200]]

```bash
# ~/opt/Android/SDK/platform-tools/adb
adb install app-release.apk
```
- -r 表示替换安装（覆盖旧版本）。
- 如果之前用 debug 签名安装过，要先卸载：

```bash
adb uninstall com.meida.demo
```

4. **验证签名是否正确**

你可以检查 APK 的签名：
```bash
apksigner verify --verbose app/build/outputs/apk/release/app-release.apk
```

输出类似：
```bash
Verified using v1 scheme (JAR signing): true
Verified using v2 scheme (APK Signature Scheme v2): true
Verified using v3 scheme (APK Signature Scheme v3): true
```
这说明签名没问题。

5. **安装包的位置**
```
app/build/outputs/apk/release/app-release.apk
```


# Q&A

## **1️⃣ 键盘顶起底部菜单问题**
**问题**：
- WebView 内有底部菜单或者输入框时，键盘弹出会把它顶起来，尤其是 position: fixed 的元素。

**原因**：

- Android WebView 默认不处理 **安全区域**，键盘弹出时会调整布局，导致 CSS vh 高度或 fixed 元素错位。

**解决方案**：
1. 在 Compose 中使用 Modifier.padding(WindowInsets.safeDrawing.asPaddingValues()) 包裹 AndroidView，确保 WebView 在安全区域内。
2. 在 WebView 设置中启用：

```kotlin
settings.useWideViewPort = true
settings.loadWithOverviewMode = true
```

3. 让 WebView **撑满安全区域**：
```kotlin
layoutParams = ViewGroup.LayoutParams(
    ViewGroup.LayoutParams.MATCH_PARENT,
    ViewGroup.LayoutParams.MATCH_PARENT
)
```


## **2️⃣ 文件上传问题**

**问题**：

- WebView 默认的 WebChromeClient() **不支持 <input type="file">** 文件上传。
- 点击上传按钮会无反应。

**解决方案**：

1. 自定义 WebChromeClient，重写 onShowFileChooser：
```kotlin
@Composable

fun WebViewScreen(url: String) {
    var filePathCallback by remember { mutableStateOf<ValueCallback<Array<Uri>>?>(null) }

    // 1️⃣ 创建 launcher
    val launcher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.StartActivityForResult()
    ) { result ->
        // 2️⃣ 处理回调
        val data = result.data
        val uris = if (result.resultCode == Activity.RESULT_OK && data != null) {
            data.data?.let { arrayOf(it) }
        } else null
        
        filePathCallback?.onReceiveValue(uris)
        filePathCallback = null
    }

  

    AndroidView(
        factory = { context ->
            WebView(context).apply {
                webChromeClient = object : WebChromeClient() {
                    override fun onShowFileChooser(
                        webView: WebView?,
                        filePathCallbackParam: ValueCallback<Array<Uri>>?,
                        fileChooserParams: FileChooserParams?
                    ): Boolean {
                        filePathCallback = filePathCallbackParam
                        try {
                            val intent = fileChooserParams?.createIntent()
                            if (intent != null) {
                                launcher.launch(intent) // ✅ 用 launcher 启动选择器
                            }
                        } catch (e: ActivityNotFoundException) {
                            filePathCallback = null
                            return false
                        }
                        return true
                    }
                }
            }
        }
    )
}
```

2. 保存回调到外层 remember 变量，以便在 onActivityResult 中返回文件：
```kotlin
filePathCallback?.onReceiveValue(uris)
filePathCallback = null
```


3. WebView 设置中开启相关权限：
```kotlin
settings.javaScriptEnabled = true
settings.domStorageEnabled = true
settings.allowFileAccess = true
settings.allowContentAccess = true
settings.mixedContentMode = WebSettings.MIXED_CONTENT_ALWAYS_ALLOW
```
