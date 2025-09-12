
**cgroup** 才是用来控制 **资源配额** 的地方。

相关挂载点通常在：
## **🔹 cgroup v1**

- **设计思路**：一个子系统一个控制器，比如 cpu、memory、blkio 各自独立。
- **设计思路**：一个子系统一个控制器，比如 cpu、memory、blkio 各自独立。
- **目录结构**：
```bash
/sys/fs/cgroup/cpu/docker/<container-id>/cpu.cfs_quota_us
/sys/fs/cgroup/memory/docker/<container-id>/memory.limit_in_bytes
```

- **CPU 限制方式**：
    - cpu.cfs_quota_us（配额，单位微秒）
    - cpu.cfs_period_us（周期，默认 100000 微秒 = 100ms）
比如：
```bash
echo 20000 > cpu.cfs_quota_us   # 限制 20ms
echo 100000 > cpu.cfs_period_us # 周期 100ms
```
代表 **20% CPU**。

**缺点**：每个控制器独立，容易导致配置不一致；层级关系复杂。

## **🔹 cgroup v2**

- **设计思路**：统一层级，所有控制器挂在一个树下，接口文件更直观。
- **目录结构**：
```bash
/sys/fs/cgroup/system.slice/docker-<container-id>.scope/cpu.max
/sys/fs/cgroup/system.slice/docker-<container-id>.scope/memory.max
```

- **CPU 限制方式**：
    - cpu.max（两个数字：quota period）
例如：
```bash
echo "20000 100000" > cpu.max
```

- 就是 **20% CPU**。
    - 如果写 max 100000 → 表示不限 CPU。
- **优点**：接口统一，简化了配置，支持更强的功能（比如 PSI 压力信息 cpu.pressure）。

## **🔹 Docker 与 cgroup v1/v2**

- **旧版本 Docker + 老内核** → 默认用 **cgroup v1**。
- **新内核 (5.x+) + systemd** → 默认是 **cgroup v2**，这就是你现在看到的 cpu.max 而不是 cpu.cfs_quota_us。
- Docker 启动参数 --exec-opt native.cgroupdriver=systemd 会决定它是走 systemd cgroup 驱动还是 cgroupfs。

### 配置

| **文件名**         | **可写/只读** | **作用**             | **说明**                                                                                                            |
| --------------- | --------- | ------------------ | ----------------------------------------------------------------------------------------------------------------- |
| cpu.max         | 可写        | 限制 CPU 使用上限        | 格式 <quota> <period>，quota=每个周期允许的运行时间（µs），period=周期长度（µs），例如 20000 100000 表示 20% CPU。写 max 100000 表示无限制。          |
| cpu.max.burst   | 可写        | 短时突发 CPU 时间        | 允许容器在短时间内使用超过 cpu.max 的 CPU，单位 µs。                                                                                |
| cpu.stat        | 只读        | CPU 使用统计信息         | 包括：usage_usec（总使用时间）、user_usec（用户态）、system_usec（内核态）、nr_periods（调度周期数）、nr_throttled（受限周期数）、throttled_usec（受限总时间）。 |
| cpu.weight      | 可写        | CPU 权重             | 1-10000，决定公平调度下容器获得 CPU 的相对优先级。默认 100。                                                                            |
| cpu.weight.nice | 可写        | 通过 nice 值设置 CPU 权重 | 对应传统 nice 值范围 -20~19，内核会映射为 cpu.weight。                                                                           |
| cpu.uclamp.min  | 可写        | CPU 使用下限（QoS）      | 0-1024，表示调度器保证的最小 CPU “性能”，用于性能保障。                                                                                |
| cpu.uclamp.max  | 可写        | CPU 使用上限（QoS）      | 0-1024，表示调度器限制的最大 CPU “性能”，和 cpu.max 不同，更偏向调度 QoS 而非硬限制。                                                          |
| cpu.idle        | 可写        | 控制 CPU 空闲时间        | 用于实时调度或高级场景，不常直接修改。                                                                                               |
| cpu.pressure    | 只读        | CPU 压力信息（PSI）      | 显示 CPU 资源不足时进程等待的情况，包括 some（部分进程受限）、full（所有进程受限）及平均值。                                                             |

|                     |     |             |                                                   |
| ------------------- | --- | ----------- | ------------------------------------------------- |
| memory.current      | 只读  | 当前内存使用量     | 显示该 cgroup 当前使用的内存总量（字节）。                         |
| memory.events       | 只读  | 内存事件统计      | 统计 OOM 或内存压力事件，如 low、high、max 被触发次数。              |
| memory.events.local | 只读  | 本地内存事件      | 统计本 NUMA 节点上触发的内存事件。                              |
| memory.high         | 可写  | 高内存水位       | 超过该值时内核会尝试回收，非硬限制，类似软限制。                          |
| memory.low          | 可写  | 低内存水位       | 内核会保证至少为该值分配内存，用于 QoS 保证。                         |
| memory.max          | 可写  | 最大内存限制      | 硬限制，容器使用超过该值会触发 OOM。                              |
| memory.min          | 可写  | 最小内存限制      | 保证最少可用内存，类似 QoS 下限。                               |
| memory.numa_stat    | 只读  | NUMA 内存统计   | 显示 NUMA 节点上内存分配情况，统计每个节点使用量。                      |
| memory.oom.group    | 可写  | OOM 行为控制    | 设置为 1 表示 cgroup 内 OOM 会影响整个 cgroup，而不仅仅是单个进程。     |
| memory.pressure     | 只读  | 内存压力信息（PSI） | 显示该 cgroup 内存不足时进程等待情况，包括 some 和 full。            |
| memory.stat         | 只读  | 内存使用统计      | 包括 anon、file、kernel_stack、pgfault、pgmajfault 等指标。 |
| memory.swap.current | 只读  | 当前 swap 使用量 | 显示该 cgroup 当前 swap 使用量（字节）。                       |
| memory.swap.events  | 只读  | swap 事件统计   | 统计 swap 使用的事件次数。                                  |
| memory.swap.high    | 可写  | swap 高水位限制  | 超过该值时会触发 swap 回收，但不是硬限制。                          |
| memory.swap.max     | 可写  | swap 最大限制   | 硬限制，超过该值就不能再使用 swap。                              |

| **文件名**                | **可写/只读** | **作用**         | **说明**                                                          |
| ---------------------- | --------- | -------------- | --------------------------------------------------------------- |
| cgroup.procs           | 可写        | 添加/查看进程        | 写入 PID 可以把进程加入该 cgroup；读出当前 cgroup 内所有进程 PID。                   |
| cgroup.threads         | 只读        | 查看线程           | 显示该 cgroup 内所有线程 TID（thread id）。                                |
| cgroup.subtree_control | 可写        | 启用子 cgroup 控制器 | 用于开启 CPU/memory/pids 等控制器对子 cgroup 的管理能力，例如 +cpu +memory +pids。 |
| cgroup.controllers     | 只读        | 查看可用控制器        | 列出当前 cgroup 可用的控制器，如 cpu memory io pids 等。                      |
| cgroup.events          | 只读        | 事件统计           | 显示子 cgroup 的一些事件标志，如 OOM、冻结（frozen）状态等。                         |
| cgroup.freeze          | 可写        | 冻结 / 解冻进程      | 写 1 冻结该 cgroup 内所有进程，写 0 解冻。                                    |
| cgroup.max.descendants | 可写        | 子 cgroup 数量限制  | 限制当前 cgroup 下子 cgroup 的最大数量。                                    |
| pids.max               | 可写        | 最大进程数          | 限制该 cgroup 内允许的最大进程数，max 表示无限制。                                 |
| pids.current           | 只读        | 当前进程数          | 显示该 cgroup 内当前活跃进程数。                                            |

