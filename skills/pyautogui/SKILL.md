# PyAutoGUI 技能学习笔记

## 基本信息
- **名称**: PyAutoGUI
- **类型**: Python 桌面自动化库
- **功能**: 控制鼠标、键盘，实现桌面自动化

## 核心功能

### 1. 鼠标控制
- `pyautogui.moveTo(x, y)` - 移动鼠标到指定位置
- `pyautogui.click()` - 点击鼠标
- `pyautogui.doubleClick()` - 双击
- `pyautogui.rightClick()` - 右键点击
- `pyautogui.dragTo(x, y)` - 拖拽到指定位置
- `pyautogui.scroll(n)` - 滚轮滚动

### 2. 键盘控制
- `pyautogui.typewrite('text')` - 输入文字
- `pyautogui.press('enter')` - 按单个键
- `pyautogui.hotkey('ctrl', 'c')` - 组合键
- `pyautogui.keyDown('shift')` / `pyautogui.keyUp('shift')` - 按住/释放键

### 3. 屏幕操作
- `pyautogui.screenshot()` - 截图
- `pyautogui.locateOnScreen('image.png')` - 在屏幕上找图
- `pyautogui.pixel(x, y)` - 获取像素颜色
- `pyautogui.size()` - 获取屏幕尺寸

### 4. 消息弹窗
- `pyautogui.alert('message')` - 提示框
- `pyautogui.confirm('message')` - 确认框
- `pyautogui.prompt('message')` - 输入框

## 安全功能
- `pyautogui.FAILSAFE = True` - 开启故障保护（鼠标移到左上角停止）
- `pyautogui.PAUSE = 0.5` - 设置操作间隔

## 应用场景
- 自动化重复操作
- 软件测试
- 游戏脚本
- 批量处理任务
- 微信/QQ 自动化（配合找图功能）

## 学习状态
- [x] 了解基本功能
- [ ] 安装 PyAutoGUI
- [ ] 编写测试脚本
- [ ] 实际应用

## 备注
- 需要管理员权限运行某些操作
- Mac 需要辅助功能权限
- 使用时注意安全，防止误操作
