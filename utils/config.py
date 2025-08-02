import yaml
import os
from typing import Dict, Any, Optional
from .constants import *

class Config:
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self._config = {}
        self.load_config()
    
    def load_config(self):
        """設定ファイルを読み込み"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self._config = yaml.safe_load(f) or {}
            else:
                print(f"設定ファイル {self.config_path} が見つかりません。デフォルト値を使用します。")
                self._config = {}
        except Exception as e:
            print(f"設定ファイルの読み込みエラー: {e}")
            self._config = {}
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """階層的なキーで設定値を取得"""
        keys = key_path.split('.')
        value = self._config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def get_display_config(self) -> Dict[str, Any]:
        """画面設定を取得"""
        return {
            'width': self.get('display.width', SCREEN_WIDTH),
            'height': self.get('display.height', SCREEN_HEIGHT),
            'fps': self.get('display.fps', FPS),
            'fullscreen': self.get('display.fullscreen', True)
        }
    
    def get_color_config(self) -> Dict[str, tuple]:
        """色設定を取得"""
        return {
            'black': tuple(self.get('colors.black', BLACK)),
            'white': tuple(self.get('colors.white', WHITE)),
            'cyan_glow': tuple(self.get('colors.cyan_glow', CYAN_GLOW)),
            'blue_white': tuple(self.get('colors.blue_white', BLUE_WHITE))
        }
    
    def get_eye_config(self) -> Dict[str, Any]:
        """目の設定を取得"""
        display_config = self.get_display_config()
        base_size = min(display_config['width'], display_config['height']) * self.get('eye.base_size_ratio', 1/3)
        
        return {
            'base_size': int(base_size),
            'width': int(base_size * self.get('eye.width_ratio', 0.6)),
            'height': int(base_size * self.get('eye.height_ratio', 1.4)),
            'spacing': int(base_size * self.get('eye.spacing_ratio', 1.2))
        }
    
    def get_animation_config(self) -> Dict[str, Any]:
        """アニメーション設定を取得"""
        return {
            'look_interval_min': self.get('animation.look_interval_min', LOOK_INTERVAL_MIN),
            'look_interval_max': self.get('animation.look_interval_max', LOOK_INTERVAL_MAX),
            'move_speed': self.get('animation.move_speed', MOVE_SPEED),
            'blink_interval_min': self.get('animation.blink_interval_min', BLINK_INTERVAL_MIN),
            'blink_interval_max': self.get('animation.blink_interval_max', BLINK_INTERVAL_MAX),
            'blink_duration': self.get('animation.blink_duration', BLINK_DURATION),
            'blink_height_ratio': self.get('animation.blink_height_ratio', BLINK_HEIGHT_RATIO)
        }
    
    def get_cache_config(self) -> Dict[str, Any]:
        """キャッシュ設定を取得"""
        return {
            'directory': os.path.expanduser(self.get('cache.directory', CACHE_DIR)),
            'version': self.get('cache.version', CACHE_VERSION)
        }
    
    def get_command_interface_config(self) -> Dict[str, Any]:
        """コマンドインターフェース設定を取得"""
        return {
            'host': self.get('command_interface.host', COMMAND_HOST),
            'port': self.get('command_interface.port', COMMAND_PORT),
            'buffer_size': self.get('command_interface.buffer_size', COMMAND_BUFFER_SIZE)
        }
    
    def get_state_config(self, state_name: str) -> Dict[str, Any]:
        """状態別設定を取得"""
        return self.get(f'states.{state_name}', {})

# グローバル設定インスタンス
config = Config()