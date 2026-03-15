# 🛡️ OpenClaw 24小时在线稳定性配置

## 问题描述
用户发现：**关闭电脑显示屏后，OpenClaw无法响应手机飞书消息**

## 根本原因
OpenClaw Gateway 运行在用户电脑上，当电脑：
1. **进入睡眠模式** - 进程被挂起
2. **关闭显示屏** - 可能触发节能模式，断开网络
3. **网络进入节能** - WiFi/网络连接中断

即使手机能发送消息，电脑端的Gateway无法接收和处理。

## 解决方案（三选一）

### 方案A：彻底防睡眠（Mac）
```bash
# 一次性设置，需要sudo密码
sudo pmset -a disablesleep 1    # 完全禁用睡眠
sudo pmset -a sleep 0           # 永不睡眠
sudo pmset -a displaysleep 0    # 显示器永不睡眠
sudo pmset -a disksleep 0       # 硬盘永不睡眠
sudo pmset -a womp 1            # 启用网络唤醒
sudo pmset -a powernap 1        # 睡眠时仍处理网络
sudo pmset -a tcpkeepalive 1    # 保持TCP连接
sudo pmset -a networkoversleep 0 # 网络不休眠
```

**效果**：合盖、关屏、长时间不操作都不休眠，电脑24小时在线。

**恢复默认**：
```bash
sudo pmset -a disablesleep 0
sudo pmset -a sleep 1
sudo pmset -a displaysleep 10
```

### 方案B：GUI设置（无需命令行）
1. **系统设置** → **电池**
2. **电源适配器**选项卡：
   - 将「显示器进入睡眠」拉到「永不」
   - 将「电脑进入睡眠」拉到「永不」
   - 关闭「如果可能，使硬盘进入睡眠」
3. **电池**选项卡（同样设置，防止拔电后失效）
4. **网络**设置：
   - 系统设置 → **网络** → **高级** → **硬件**
   - 取消勾选「在可能的情况下使网络进入睡眠」

### 方案C：服务器部署（一劳永逸）
将OpenClaw Gateway部署到24小时在线的设备：

#### 选项1：云服务器（推荐）
- **阿里云/腾讯云**轻量应用服务器（30-50元/月）
- 安装Ubuntu/Debian，部署OpenClaw
- 不受本地电脑影响，专业稳定

#### 选项2：旧手机/平板
- 安装Termux（Android）或Shelly（iOS）
- 24小时充电运行
- 低成本，利用闲置设备

#### 选项3：树莓派/NAS
- 低功耗，常年运行
- 性能足够运行OpenClaw

## 测试方法
1. 应用设置后，等待1分钟
2. **关闭显示屏**（或合上笔记本）
3. 等待2-3分钟
4. 用**手机飞书**发送"测试"
5. 检查是否收到自动回复

## 故障排除

### 问题1：设置后仍然睡眠
```bash
# 检查当前设置
pmset -g

# 查看哪些进程阻止睡眠
pmset -g assertions
```

### 问题2：网络仍然断开
```bash
# 检查网络状态
networksetup -getinfo "Wi-Fi"

# 防止WiFi休眠
sudo systemsetup -setcomputersleep Never
```

### 问题3：合盖后断网（笔记本）
```bash
# 禁止合盖休眠
sudo nvram boot-args="serverperfmode=1"
# 重启生效
```

## 节能考虑
如果担心电脑24小时运行耗电：
- 使用**方案C**（服务器部署）
- 设置**自动关机/重启**时间（如凌晨4-6点）
- 使用**智能插座**定时供电

## 监控状态
```bash
# 查看OpenClaw Gateway状态
openclaw gateway status

# 查看日志
tail -f ~/.openclaw/logs/gateway.log

# 检查最后在线时间
date && echo "最后心跳：" && tail -1 ~/.openclaw/logs/heartbeat.log
```

## 紧急联系
如果OpenClaw完全离线：
1. **重启Gateway**：`openclaw gateway restart`
2. **检查网络**：`ping 8.8.8.8`
3. **查看进程**：`ps aux | grep openclaw`
4. **重新登录飞书**：检查token是否过期

---

**建议**：对于生产环境，使用**方案C（云服务器）**；对于个人使用，使用**方案A（彻底防睡眠）**并定期重启电脑。