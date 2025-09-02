```bash
───────────────────────────────
 macOS + Docker (Linux 容器)
───────────────────────────────
[macOS Host]
    │
    ├─ Docker Desktop App
    │
    └─ LinuxKit VM (轻量虚拟机)
         │
         └─ Container 进程 (PID 隔离)
              e.g. nginx, rust build, etc.
  
宿主 macOS 看不到 Container 的真实 PID
只能看到 LinuxKit 进程
───────────────────────────────
 Linux + Docker (原生 Linux)
───────────────────────────────
[Linux Host]
    │
    ├─ containerd / dockerd
    │
    └─ Container 进程 (PID 共享/隔离可选)
         e.g. nginx, rust build, etc.


宿主 Linux 可以通过 ps/top/htop 看到容器进程 PID
───────────────────────────────
 Windows + Docker (Linux 容器)
───────────────────────────────
[Windows Host]
    │
    └─ WSL2 VM (Linux 内核)
         │
         └─ Container 进程 (PID 隔离)
              e.g. nginx, rust build, etc.

宿主 Windows 看不到 Container 的 PID
需要进入 WSL2 才能看到
───────────────────────────────
 Windows + Docker (Windows 容器)
───────────────────────────────
[Windows Host]
    │
    └─ Container 进程 (直接运行在 Windows 内核)
         e.g. IIS, .NET app, etc.
宿主 Windows 可以看到 Container 的 PID
```

📌 总结：
1. **macOS / Windows + Linux 容器** → 容器在虚拟机里，宿主看不到真实 PID。
2. **Linux 原生** → 容器和宿主共享 PID namespace（可选隔离），宿主可直接看到。
3. **Windows 容器** → 容器直接在 Windows 内核上运行，宿主可直接看到 PID。

## 实验 🧪

1. 如何查看容器的进程 id

```bash
root@ems:~# docker ps -a
CONTAINER ID   IMAGE                             COMMAND                  CREATED        STATUS        PORTS     NAMES
c7c01f17b697   scada-console-server              "/wait-for-it.sh -t …"   16 hours ago   Up 16 hours             scada-console-server
b636a7c5321e   scada-tool-server                 "/wait-for-it.sh -t …"   20 hours ago   Up 20 hours             scada-tool-server
762a9271edcb   scada-gateway-server              "java -jar -Dspring.…"   22 hours ago   Up 22 hours             scada-gateway-server
5dd607006c51   scada-datahandle-server           "/wait-for-it.sh -t …"   23 hours ago   Up 17 hours             scada-datahandle-server
edbc25dd980d   scada-websocket-server            "/wait-for-it.sh -t …"   7 days ago     Up 22 hours             scada-websocket-server
dd36e63c6937   scada-ppc-server1                 "/bin/bash -c /home/…"   2 months ago   Up 19 hours             scada-ppc-server1
c971b9a60ecf   ghcr.io/deepch/rtsptoweb:latest   "./rtsp-to-web --con…"   2 months ago   Up 22 hours             scada-rstp-server
root@ems:~# docker inspect dd36e63c | grep Pid
            "Pid": 57351,
            "PidMode": "",
            "PidsLimit": null,
root@ems:~# ps -ef |grep 57351
root       57351   57331  0 Sep01 ?        00:00:09 /bin/bash /home/econ/guard.sh
root       57380   57351 11 Sep01 ?        02:08:10 ./pdscanner
root       57575   57351  0 Sep01 ?        00:05:53 /home/econ/ppc/ppc-server
root      158060   57351  0 09:35 ?        00:00:00 sleep 5
root      158069   19867  0 09:35 pts/2    00:00:00 grep --color=auto 57351
root@ems:~# ps -ef |grep 57331
root       57331       1  0 Sep01 ?        00:00:04 /usr/bin/containerd-shim-runc-v2 -namespace moby -id dd36e63c693700f1c3bd4213655b08561f2cf6f7309890f31b432f83f214d4f0 -address /run/containerd/containerd.sock
root       57351   57331  0 Sep01 ?        00:00:09 /bin/bash /home/econ/guard.sh
root       57632   57331  0 Sep01 pts/0    00:00:00 /bin/bash
root      158100   19867  0 09:36 pts/2    00:00:00 grep --color=auto 57331
```

2. 查看进程对应的 namespace
3. 
```bash
root@ems:~# ps -ef |grep 57331
root       57331       1  0 Sep01 ?        00:00:04 /usr/bin/containerd-shim-runc-v2 -namespace moby -id dd36e63c693700f1c3bd4213655b08561f2cf6f7309890f31b432f83f214d4f0 -address /run/containerd/containerd.sock
root       57351   57331  0 Sep01 ?        00:00:09 /bin/bash /home/econ/guard.sh
root       57632   57331  0 Sep01 pts/0    00:00:00 /bin/bash
root      158100   19867  0 09:36 pts/2    00:00:00 grep --color=auto 57331
root@ems:~# 
root@ems:~# 
root@ems:~# ls -al /proc/57331/ns
total 0
dr-x--x--x 2 root root 0 Sep  1 17:44 .
dr-xr-xr-x 9 root root 0 Sep  1 14:20 ..
lrwxrwxrwx 1 root root 0 Sep  2 09:38 cgroup -> 'cgroup:[4026531835]'
lrwxrwxrwx 1 root root 0 Sep  2 09:38 ipc -> 'ipc:[4026531839]'
lrwxrwxrwx 1 root root 0 Sep  2 09:38 mnt -> 'mnt:[4026531841]'
lrwxrwxrwx 1 root root 0 Sep  2 09:38 net -> 'net:[4026531840]'
lrwxrwxrwx 1 root root 0 Sep  2 09:38 pid -> 'pid:[4026531836]'
lrwxrwxrwx 1 root root 0 Sep  2 09:38 pid_for_children -> 'pid:[4026531836]'
lrwxrwxrwx 1 root root 0 Sep  2 09:38 time -> 'time:[4026531834]'
lrwxrwxrwx 1 root root 0 Sep  2 09:38 time_for_children -> 'time:[4026531834]'
lrwxrwxrwx 1 root root 0 Sep  2 09:38 user -> 'user:[4026531837]'
lrwxrwxrwx 1 root root 0 Sep  2 09:38 uts -> 'uts:[4026531838]'
root@ems:~# ls -al /proc/57351/ns
total 0
dr-x--x--x 2 root root 0 Sep  1 14:20 .
dr-xr-xr-x 9 root root 0 Sep  1 14:20 ..
lrwxrwxrwx 1 root root 0 Sep  1 14:20 cgroup -> 'cgroup:[4026532215]'
lrwxrwxrwx 1 root root 0 Sep  1 14:20 ipc -> 'ipc:[4026532213]'
lrwxrwxrwx 1 root root 0 Sep  1 14:20 mnt -> 'mnt:[4026532211]'
lrwxrwxrwx 1 root root 0 Sep  1 14:20 net -> 'net:[4026531840]'
lrwxrwxrwx 1 root root 0 Sep  1 14:20 pid -> 'pid:[4026532214]'
lrwxrwxrwx 1 root root 0 Sep  2 09:38 pid_for_children -> 'pid:[4026532214]'
lrwxrwxrwx 1 root root 0 Sep  2 09:38 time -> 'time:[4026531834]'
lrwxrwxrwx 1 root root 0 Sep  2 09:38 time_for_children -> 'time:[4026531834]'
lrwxrwxrwx 1 root root 0 Sep  2 09:38 user -> 'user:[4026531837]'
lrwxrwxrwx 1 root root 0 Sep  1 14:20 uts -> 'uts:[4026532212]'
root@ems:~# ls -al /proc/57632/ns
total 0
dr-x--x--x 2 root root 0 Sep  1 17:36 .
dr-xr-xr-x 9 root root 0 Sep  1 14:20 ..
lrwxrwxrwx 1 root root 0 Sep  2 09:39 cgroup -> 'cgroup:[4026532215]'
lrwxrwxrwx 1 root root 0 Sep  2 09:39 ipc -> 'ipc:[4026532213]'
lrwxrwxrwx 1 root root 0 Sep  2 09:39 mnt -> 'mnt:[4026532211]'
lrwxrwxrwx 1 root root 0 Sep  2 09:39 net -> 'net:[4026531840]'
lrwxrwxrwx 1 root root 0 Sep  2 09:39 pid -> 'pid:[4026532214]'
lrwxrwxrwx 1 root root 0 Sep  2 09:39 pid_for_children -> 'pid:[4026532214]'
lrwxrwxrwx 1 root root 0 Sep  2 09:39 time -> 'time:[4026531834]'
lrwxrwxrwx 1 root root 0 Sep  2 09:39 time_for_children -> 'time:[4026531834]'
lrwxrwxrwx 1 root root 0 Sep  2 09:39 user -> 'user:[4026531837]'
lrwxrwxrwx 1 root root 0 Sep  2 09:39 uts -> 'uts:[4026532212]'
```

**Q/A 为什么 容器的namespace 跟 容器内的应用不是一个 namespace

- 容器的主进程（通常 PID 1）在宿主机看是一个进程，PID 可能很大，比如 12345。
- 容器内部，PID namespace 会重新编号，容器主进程在容器内就是 **PID 1**。
- 容器内的应用进程也在这个 PID namespace 内，但 PID 会按照容器内的编号显示。