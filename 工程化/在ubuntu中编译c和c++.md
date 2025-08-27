
## 使用gcc编译c


### 🙋 实验问题 

  - c语言有很多的版本，跟gcc又有什么关系
  - 如何编译c的代码的
  - c语言文件是如何互相引入的
  - c 语言是如何找头文件的，就是.h
  - 编译阶段跟链接阶段
  - c 语言是如何引入动态库静态库的
  - c make是什么，他是c语言工程化工具吗，解决什么问题
  
✅ 实验步骤
 ```bash
 # 第一步安装 gcc
 apt install gcc
 ```

```c
// 第二步 编写代码 hello.cpp
#include <stdio.h>

int main() {
    printf("Hello, C!\n");
    return 0;
}
```

