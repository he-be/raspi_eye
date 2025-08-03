import os

# 画面設定（デフォルト値）
SCREEN_WIDTH = 720
SCREEN_HEIGHT = 480
FPS = 60

# 色定数
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CYAN_GLOW = (0, 255, 255)
BLUE_WHITE = (180, 200, 255)

# キャッシュ設定
CACHE_DIR = os.path.expanduser("~/.cyber_eyes_cache")
CACHE_VERSION = "v2.0"

# 画面サイズに基づいた設定
BASE_SIZE = min(SCREEN_WIDTH, SCREEN_HEIGHT) // 3

# 目の設定（縦長楕円）
EYE_WIDTH = int(BASE_SIZE * 0.6)
EYE_HEIGHT = int(BASE_SIZE * 1.4)
EYE_SPACING = int(BASE_SIZE * 1.2)

# 動きの設定
LOOK_INTERVAL_MIN = 1500
LOOK_INTERVAL_MAX = 4000
MOVE_SPEED = 0.03

# まばたき設定
BLINK_INTERVAL_MIN = 2000
BLINK_INTERVAL_MAX = 6000
BLINK_DURATION = 200
BLINK_HEIGHT_RATIO = 0.2

# まばたきのプリセット比率
BLINK_PRESETS = [1.0, 0.8, 0.6, 0.4, 0.2]

# 状態定数
class States:
    IDLE = "idle"
    THINKING = "thinking" 
    SPEAKING = "speaking"
    SLEEPING = "sleeping"

# コマンドインターフェース設定
COMMAND_HOST = "localhost"
COMMAND_PORT = 8888
COMMAND_BUFFER_SIZE = 1024