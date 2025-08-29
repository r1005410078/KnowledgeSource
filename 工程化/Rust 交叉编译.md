> 🙋 rust 是如何交叉编译的
> 🤖 

Rust 的交叉编译本质上是**在当前平台上生成针对另一平台（CPU 架构 + 操作系统）的可执行文件或库**，这涉及到**目标三元组（Target Triple）**、**交叉编译工具链（Cross Toolchain）和Rust 标准库 for 目标平台**。

 **Rust 交叉编译核心步骤**
1. **理解目标三元组（Target Triple）**
	Rust 的 target triple 一般形如：

```bash 
<arch>-<vendor>-<os>[-<abi>]
```

1. 例如：
    
    - x86_64-unknown-linux-gnu → x86_64 架构，Linux OS，GNU ABI
        
    - armv7-unknown-linux-gnueabihf → ARMv7 架构，Linux OS，硬件浮点
        
    - aarch64-apple-darwin → ARM64 架构，macOS（Apple Silicon）
        
    - x86_64-pc-windows-gnu → Windows，GNU 工具链（MinGW）
        
    - x86_64-pc-windows-msvc → Windows，MSVC 工具链
        
    
    你可以用：


```bash
rustc --print target-list
```

1. 查看所有支持的 target。

2. **添加目标平台**
    
    使用 Rustup 添加目标（类似交叉编译的“标准库”）：

```bash
rustup target add aarch64-unknown-linux-gnu
```

3. 这会安装该平台的 **Rust 标准库**，但不包含 C 运行时或交叉工具链。
4. **准备交叉工具链**
    如果你的代码包含 **FFI** 或依赖 **C/C++ 库**，需要对应平台的 GCC 或 Clang。
    - 对 Linux ARM 平台：

```bash
# 例如 Ubuntu
sudo apt-get install gcc-aarch64-linux-gnu
```


5. - 对 Windows：
        - MinGW (GNU): mingw-w64  
        - MSVC: 需要 Visual Studio 工具链
    工具链会提供 aarch64-linux-gnu-gcc、arm-linux-gnueabihf-gcc 等，用于编译 C 依赖。


6. **编译**
    最简单的交叉编译命令：
```bash
cargo build --target aarch64-unknown-linux-gnu
```

4. 输出在 target/aarch64-unknown-linux-gnu/debug/。

5. **配置链接器（Linker）**
    
    Rust 默认用系统 linker，如果目标平台不同，需要手动指定。
    例如交叉编译到 ARM Linux：
    - 编辑 .cargo/config.toml：
    
```bash
[target.aarch64-unknown-linux-gnu]
linker = "aarch64-linux-gnu-gcc"
```

---

> 🙋 除了 官方的，zig cc, zigbuild， corss 交叉编译方式，还有哪些
> 🤖  

1. 使用 LLVM/Clang 交叉编译
- Rust 编译器基于 LLVM，可以直接调用 **Clang** 作为 C 编译器。
- 比如
```bash
CC=clang \

AR=llvm-ar \

CFLAGS="--target=aarch64-linux-gnu" \

cargo build --target aarch64-unknown-linux-gnu
```

- 优点：
    - 不需要完整的 GNU 工具链。
- 缺点：
    - 对一些 C 依赖的项目，仍需 sysroot 或预编译库。


2. 使用 Nix 提供交叉编译环境
	- - - **Nix** 可以提供完整的交叉编译工具链（包括 libc、gcc）。

---

> 🙋 在ubuntu 中交叉编译
> 🤖  

```bash
root@vagrant-ubuntu:/www/seal_orm_example# cargo build --target x86_64-unknown-linux-gnu
   Compiling proc-macro2 v1.0.101
   Compiling unicode-ident v1.0.18
   Compiling quote v1.0.40
   Compiling syn v2.0.106
   Compiling libc v0.2.175
   Compiling autocfg v1.5.0
error[E0463]: can't find crate for `core`
  |
  = note: the `x86_64-unknown-linux-gnu` target may not be installed
  = help: consider downloading the target with `rustup target add x86_64-unknown-linux-gnu`

For more information about this error, try `rustc --explain E0463`.
error: could not compile `libc` (lib) due to 1 previous error
```

解决方案
```bash
rustup target add x86_64-unknown-linux-gnu
```