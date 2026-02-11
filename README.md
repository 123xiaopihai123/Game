# Python 射击小游戏

一个使用 **Pygame** 编写的简单 PC 端 2D 射击小游戏。

## 功能

- 玩家左右移动（`A/D` 或 `←/→`）
- 空格发射子弹
- 敌机随机下落
- 子弹命中得分
- 敌机漏掉会扣生命
- 碰撞玩家即游戏结束
- `R` 重新开始，`ESC` 退出

## 运行环境

- Python 3.10+
- pygame

安装依赖：

```bash
pip install pygame
```

启动游戏：

```bash
python shooter_game.py
```

## 适配说明

- 默认窗口大小：`900 x 600`
- 刷新率：`60 FPS`

如需调整难度，可在 `shooter_game.py` 顶部修改：

- `ENEMY_SPAWN_EVERY_MS`（刷怪速度）
- `ENEMY_MIN_SPEED` / `ENEMY_MAX_SPEED`（敌机速度）
- `MAX_LIVES`（初始生命）
