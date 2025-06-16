# 专注计时器 / Focus Timer

[English](#english) | [中文](#中文)

---

## 中文

### 📖 项目简介

专注计时器是一个基于Python开发的番茄工作法计时工具，帮助用户提高专注力和工作效率。程序采用随机工作时间间隔，避免固定时间带来的心理预期，同时支持暂停/恢复功能和自定义设置。

### ✨ 功能特性

- **🎯 三种工作模式**
  - **默认模式**：标准番茄工作法时间设置（3-5分钟随机专注，10秒短休息，90分钟后20分钟长休息）
  - **测试模式**：所有时间大幅缩短，便于快速测试功能（1-2秒专注，1秒短休息，6秒后2秒长休息）
  - **自定义模式**：完全自定义时间间隔和音效文件

- **⏸️ 暂停/恢复功能**
  - 在任意计时过程中按 `P` 键暂停或恢复
  - 暂停时间会被单独统计，不影响专注时间计算
  - 支持暂停状态提示和操作指导

- **🔔 音效提醒**
  - 工作开始音效 (`work.mp3`)
  - 短休息音效 (`small_rest.mp3`)
  - 长休息音效 (`big_rest.mp3`)
  - 支持自定义音效文件路径

- **📊 详细统计**
  - 会话总时长统计
  - 累计专注时间统计
  - 暂停时间统计
  - 完成的大周期次数

- **🔄 智能菜单系统**
  - 会话结束后可选择返回主菜单或退出程序
  - 支持多次使用不同模式
  - 友好的用户交互界面

### 🧠 默认模式设计原理

默认模式的设计基于三个科学理论，旨在最大化学习效率和专注力：

#### 1. 神经重放理论 (Neural Replay)
**短暂休息的科学依据**
- 神经科学研究证明，在休息时大脑会自动"重放"之前学习的内容
- 即使只休息几秒钟，大脑也会出现显著的神经重放现象
- 这种重放的速度比实际学习时快约20倍，相当于高效复习
- **应用**：每3-5分钟插入10秒休息，让大脑自动巩固刚学的知识

#### 2. 变比率强化理论 (Variable Ratio Reinforcement)
**随机时间间隔的心理学优势**
- 来自行为心理学，随机奖励比固定奖励更容易让人坚持
- 类似游戏中的"保底机制"：不知道何时获得奖励，但知道一定会获得
- 每次提示音响起都是一次正向反馈，告诉你"成功专注了一段时间"
- **应用**：3-5分钟随机提示音比固定时间更能维持专注动力

#### 3. 大脑活力周期理论 (Brain Vitality Cycle)
**90分钟专注周期的生理基础**
- 科学研究表明，大脑最佳高频工作时间约为90分钟
- 超过90分钟后，大脑活力明显下降，需要充分休息恢复
- 20分钟休息时间足够补充大脑能量，避免过度消耗
- **应用**：90分钟专注 + 20分钟休息的大周期设计

这种设计让您能够：
- 🎯 连续专注90分钟而不感到疲惫
- 📈 学习效率提升高达150%
- 🌊 更容易进入"心流"状态
- 🧠 增强记忆力和信息处理能力

### 🚀 使用方法

#### 方法一：运行源代码
```bash
# 确保已安装依赖
pip install pygame

# 运行程序
python focus_timer.py
```

#### 方法二：运行打包后的可执行文件
直接双击 `dist/专注计时器.exe` 即可运行，无需安装Python环境。

### 🎮 操作指南

1. **启动程序**：选择运行模式（0-3）
2. **专注期间**：
   - 按 `P` 键暂停/恢复计时
   - 按 `Ctrl+C` 停止程序
3. **会话结束**：选择返回主菜单(1)或退出程序(2)

### 📁 项目结构

```
focus_timer/
├── focus_timer.py          # 主程序文件
├── focus_timer_test.spec   # PyInstaller打包配置
├── work.mp3               # 工作开始音效
├── small_rest.mp3         # 短休息音效
├── big_rest.mp3           # 长休息音效
├── dist/                  # 打包输出目录
│   └── 专注计时器.exe      # 可执行文件
└── README.md              # 项目说明文档
```

### 🔧 打包说明

使用PyInstaller进行打包，包含所有音频文件：

```bash
# 激活conda环境
conda activate test

# 安装依赖
pip install pygame pyinstaller

# 打包
pyinstaller focus_timer_test.spec
```

打包后的可执行文件位于 `dist/专注计时器.exe`，大小约29MB。

### ⚙️ 自定义设置

在自定义模式中，您可以设置：
- 专注循环总时长（分钟）
- 短休息时长（秒）
- 长休息时长（分钟）
- 自定义音效文件路径

### 📋 系统要求

- **开发环境**：Python 3.7+, pygame库
- **运行环境**：Windows 10+ (可执行文件)
- **音频支持**：支持mp3和wav格式

### 🛠️ 技术栈

- **语言**：Python 3.13
- **音频库**：pygame
- **打包工具**：PyInstaller
- **开发环境**：conda

---

## English

### 📖 Project Introduction

Focus Timer is a Python-based Pomodoro Technique timer tool designed to help users improve focus and work efficiency. The program uses random work intervals to avoid psychological expectations from fixed times, while supporting pause/resume functionality and custom settings.

### ✨ Features

- **🎯 Three Working Modes**
  - **Default Mode**: Standard Pomodoro settings (3-5 min random focus, 10s short break, 20min long break after 90min)
  - **Test Mode**: All times significantly shortened for quick testing (1-2s focus, 1s short break, 2s long break after 6s)
  - **Custom Mode**: Fully customizable time intervals and sound effect files

- **⏸️ Pause/Resume Functionality**
  - Press `P` key to pause or resume during any timing process
  - Pause time is tracked separately and doesn't affect focus time calculation
  - Pause status indicators and operation guidance

- **🔔 Sound Notifications**
  - Work start sound (`work.mp3`)
  - Short break sound (`small_rest.mp3`)
  - Long break sound (`big_rest.mp3`)
  - Support for custom sound file paths

- **📊 Detailed Statistics**
  - Total session duration
  - Cumulative focus time
  - Pause time tracking
  - Number of completed major cycles

- **🔄 Smart Menu System**
  - Option to return to main menu or exit after session ends
  - Support for multiple uses with different modes
  - User-friendly interactive interface

### 🧠 Default Mode Design Theory

The default mode design is based on three scientific theories to maximize learning efficiency and focus:

#### 1. Neural Replay Theory
**Scientific basis for short breaks**
- Neuroscience research proves that the brain automatically "replays" previously learned content during rest
- Even just a few seconds of rest triggers significant neural replay phenomena
- This replay is about 20 times faster than actual learning, equivalent to highly efficient review
- **Application**: 10-second breaks every 3-5 minutes allow the brain to automatically consolidate newly learned knowledge

#### 2. Variable Ratio Reinforcement Theory
**Psychological advantages of random intervals**
- From behavioral psychology: random rewards are more engaging than fixed rewards
- Similar to gaming "guaranteed reward" mechanisms: you don't know when you'll get the reward, but you know you will
- Each notification sound is positive feedback, telling you "you've successfully focused for a period"
- **Application**: 3-5 minute random notifications maintain focus motivation better than fixed intervals

#### 3. Brain Vitality Cycle Theory
**Physiological basis for 90-minute focus cycles**
- Scientific research shows optimal high-frequency brain work time is approximately 90 minutes
- After 90 minutes, brain vitality significantly decreases and requires adequate rest for recovery
- 20-minute rest periods are sufficient to replenish brain energy and avoid over-consumption
- **Application**: 90-minute focus + 20-minute rest cycle design

This design enables you to:
- 🎯 Focus continuously for 90 minutes without fatigue
- 📈 Improve learning efficiency by up to 150%
- 🌊 More easily enter "flow" states
- 🧠 Enhance memory and information processing capabilities

### 🚀 Usage

#### Method 1: Run Source Code
```bash
# Ensure dependencies are installed
pip install pygame

# Run the program
python focus_timer.py
```

#### Method 2: Run Packaged Executable
Simply double-click `dist/专注计时器.exe` to run, no Python installation required.

### 🎮 Operation Guide

1. **Start Program**: Choose running mode (0-3)
2. **During Focus**:
   - Press `P` key to pause/resume timer
   - Press `Ctrl+C` to stop program
3. **Session End**: Choose to return to main menu(1) or exit program(2)

### 📁 Project Structure

```
focus_timer/
├── focus_timer.py          # Main program file
├── focus_timer_test.spec   # PyInstaller packaging config
├── work.mp3               # Work start sound effect
├── small_rest.mp3         # Short break sound effect
├── big_rest.mp3           # Long break sound effect
├── dist/                  # Package output directory
│   └── 专注计时器.exe      # Executable file
└── README.md              # Project documentation
```

### 🔧 Packaging Instructions

Package with PyInstaller including all audio files:

```bash
# Activate conda environment
conda activate test

# Install dependencies
pip install pygame pyinstaller

# Package
pyinstaller focus_timer_test.spec
```

The packaged executable is located at `dist/专注计时器.exe`, approximately 29MB in size.

### ⚙️ Custom Settings

In custom mode, you can configure:
- Total focus cycle duration (minutes)
- Short break duration (seconds)
- Long break duration (minutes)
- Custom sound effect file paths

### 📋 System Requirements

- **Development**: Python 3.7+, pygame library
- **Runtime**: Windows 10+ (executable file)
- **Audio Support**: Supports mp3 and wav formats

### 🛠️ Tech Stack

- **Language**: Python 3.13
- **Audio Library**: pygame
- **Packaging Tool**: PyInstaller
- **Development Environment**: conda

---

### 📝 License

This project is open source and available under the MIT License.

### 🤝 Contributing

Contributions, issues, and feature requests are welcome!

### 📧 Contact

If you have any questions or suggestions, please feel free to contact us.

---

**Happy Focusing! 🎯** 