
# 🎵 Rhythm Stacker

一个使用 Pygame 开发的节奏堆叠游戏。玩家需要跟随音乐节拍，在正确的时间点击按键，将不断下落的“砖块”精准堆叠。

项目灵感来源于《节奏医生》（Rhythm Doctor）中的小游戏，并在此基础上扩展了评分系统、校准工具、成绩快照等丰富功能。

---

## ✨ 功能特性

- **🎯 核心玩法**：跟随 BPM 节拍堆叠砖块，每次按键的偏移量会实时显示，并影响生命值和连击。
- **⚙️ 动态 BPM 支持**：可自由调整音乐速度和判定窗口，适配不同曲目。
- **📊 实时状态显示**：偏移量、连击数（COMBO）、生命值、帧率（FPS）等关键数据一目了然。
- **🔧 内置校准模式**：通过 `F4` 键进入校准模式，自动测量并调整 `DELAY` 参数，消除音画不同步。
- **📁 成绩快照系统**：按 `F2` 可导出当前成绩为 `.stack` 文件（带 HMAC 签名），防止篡改；也可导入他人成绩进行展示。
- **🔐 检查模式**：启动时传入 `check` 参数，可设置目标砖块数作为“锁”，达到目标后方可继续（可用于登录验证等场景）。
- **🎨 视觉与反馈**：砖块堆叠时有颜色变化和红标提示（失误），支持自定义色板、星空背景和滚动歌词（LRC）。
- **🛠️ 高度可配置**：几乎所有参数（判定窗口、BPM、音量、显示选项等）都可通过 `stacker.cfg` 文件调整。

---

## 🚀 快速开始

### 环境要求

- Python 3.11 或更高
- 依赖库：pygame（或 pygame-ce）

### 安装与运行

#### 1. 克隆或下载项目
```bash
git clone https://github.com/your-username/rhythm-stacker.git
cd rhythm-stacker
```

#### 2. 安装依赖
```bash
pip install -r requirements.txt
```

#### 3. 运行游戏（普通模式）
```bash
pythonw main.pyw
```

#### 4. 运行检查模式（例如：需要堆叠 50 块砖才能继续）
```
pythonw main.pyw [output_file] 50
```
> [!TIP]  
> 特别的，当`output_file`为`user_login`时，会有更高级的效果哦(仅限Windows)~

### 配置文件

根目录中的 `stacker.cfg` 是配置文件，你可以在此调整所有游戏参数：

- `NAME`：玩家名称 ，在成绩快照中展示。
- `DELAY`：音频延迟补偿（毫秒），可通过校准模式自动调整。
- `BPM`：音乐节拍速度。
- `JUDGE_WINDOW`：完美判定窗口（毫秒）。
- `INFINITY_MODE`：无敌模式（血量不减）。
- `SHOW_FPS`、`SHOW_OFFSET` 等：显示开关。
- **还有更多**......

---

## 🎮 操作说明

| 按键 | 功能 |
| :--- | :--- |
| **任意其他键** | 堆叠砖块 |
| **F2** | 导出/导入成绩快照 |
| **F3** | 隐藏/显示状态栏（HUD） |
| **F4** | 进入/退出校准模式 |
| **ESC** | 退出游戏 / 返回主菜单（在检查模式下会触发特定逻辑） |

---

## 📁 项目结构

```
rhythm-stacker/
├── main.pyw                   # 游戏主程序
├── stacker.cfg                # 游戏配置文件（首次运行自动生成）
├── resources/                 # 资源目录（需用户自行放置）
│   ├── ...ttf                 # 字体文件（Minecraft AE.ttf, emj.ttf）
│   ├── ...ogg/wav             # 音效文件
│   └── sndRhythmStacker.wav   # 默认背景音乐
├── requirements.txt           # 依赖列表
├── README.md                  # 本文件
└── LICENSE                    # 许可文件
```

> [!IMPORTANT]
> 为了保持程序轻量和灵活性，游戏资源（音乐、字体、音效）**不会被打包进可执行文件**，在移动程序位置时请注意携带资源和配置文件。

---

## 📄 许可

本项目采用 **MIT 许可证**，你可以自由使用、修改、分发，但需保留版权声明。

---

**祝你堆叠愉快！🎵**

---
---
> [!Tip]
> 👆**中文**  
> 👇**English**
---
---

# 🎵 Rhythm Stacker

A rhythm stacking game built with Pygame. Players stack "bricks" in time with the music by pressing a key at the right moment.

Inspired by the mini‑game from *Rhythm Doctor*, this project extends the concept with a scoring system, calibration tools, and tamper‑proof score snapshots.

---

## ✨ Features

- **🎯 Core Gameplay**: Stack bricks to the beat. Your timing offset is displayed in real time, affecting your health and combo.
- **⚙️ Dynamic BPM Support**: Freely adjust BPM and judge window to match different songs.
- **📊 Real‑time HUD**: Offset, combo, health, and FPS are all visible at a glance.
- **🔧 Built‑in Calibration**: Press `F4` to enter calibration mode and automatically measure your audio delay.
- **📁 Score Snapshots**: Press `F2` to export your current score as a `.stack` file with an HMAC signature to prevent tampering. You can also import others' snapshots for display.
- **🔐 Check Mode**: Launch with a `check` parameter to set a brick target as a "lock" – the game continues only when you reach it (useful for login‑style scenarios).
- **🎨 Visual Feedback**: Bricks change color on hit, with red hints for mistakes. Supports custom palettes, starfield backgrounds, and scrolling LRC lyrics.
- **🛠️ Highly Configurable**: Almost every parameter (judge window, BPM, volume, display options) can be tuned via `stacker.cfg`.

---

## 🚀 Quick Start

### Requirements

- Python 3.11 or higher
- pygame (or pygame-ce)

### Installation & Running

#### 1. Clone or download the project
```bash
git clone https://github.com/your-username/rhythm-stacker.git
cd rhythm-stacker
```

#### 2. Install dependencies
```bash
pip install -r requirements.txt
```

#### 3. Run the game (normal mode)
```bash
pythonw main.pyw
```

#### 4. Run in check mode (e.g., require 50 bricks to unlock)
```bash
pythonw main.pyw [output_file] 50
```
> [!TIP]  
> When `output_file` is set to `user_login`, an advanced effect will be triggered (Windows only)~

### Configuration

The `stacker.cfg` file in the root directory is the configuration file. You can adjust all game parameters here:

- `NAME`: Player name, displayed in score snapshots.
- `DELAY`: Audio latency compensation (ms) – can be auto‑set via calibration.
- `BPM`: Song tempo.
- `JUDGE_WINDOW`: Perfect judge window (ms).
- `INFINITY_MODE`: Invincibility mode (health never drops).
- `SHOW_FPS`, `SHOW_OFFSET`, etc.: Toggle HUD elements.
- **And many more...**

---

## 🎮 Controls

| Key | Action |
| :--- | :--- |
| **Any other key** | Stack a brick |
| **F2** | Export / import score snapshot |
| **F3** | Toggle HUD visibility |
| **F4** | Enter / exit calibration mode |
| **ESC** | Quit / return to menu (triggers check‑mode logic when active) |

---

## 📁 Project Structure

```
rhythm-stacker/
├── main.pyw                   # Main game script
├── stacker.cfg                # Game configuration (auto‑generated on first run)
├── resources/                 # Resource directory (user‑provided)
│   ├── ...ttf                 # Font files (Minecraft AE.ttf, emj.ttf)
│   ├── ...ogg/wav             # Sound effect files
│   └── sndRhythmStacker.wav   # Default background music
├── requirements.txt           # Dependencies
├── README.md                  # This file
└── LICENSE                    # License file
```

> [!IMPORTANT]
> To keep the executable lightweight and flexible, game resources (music, fonts, sound effects) are **not** bundled. When moving the program, please ensure the resource files and configuration are carried along.

---

## 📄 License

This project is licensed under the **MIT License** – you are free to use, modify, and distribute it, as long as the original copyright notice is retained.

---

**Happy stacking! 🎵**
