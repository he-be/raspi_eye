import pygame
from typing import Dict, Any
from states.base_state import BaseState
from renderers.border_renderer import BorderRenderer
from utils.config import config
from utils.constants import States

class ThinkingState(BaseState):
    """思考中状態（カラフルな外枠オーバーレイ）"""
    
    def __init__(self):
        super().__init__(States.THINKING)
        
        # 設定を取得
        self.thinking_config = config.get_state_config('thinking')
        
        # 外枠レンダラーを初期化
        self.border_renderer = BorderRenderer()
        
        # 思考中状態の設定
        self.border_width = self.thinking_config.get('border_width', 8)
        self.color_change_speed = self.thinking_config.get('color_change_speed', 0.5)
        self.pulse_speed = self.thinking_config.get('pulse_speed', 0.7)
        
        # アニメーション状態
        self.thinking_intensity = 1.0
        self.duration = None  # 無制限
    
    def enter(self, previous_state: str = None, **kwargs):
        """思考中状態開始時の処理"""
        super().enter(previous_state, **kwargs)
        
        # パラメータを取得
        self.thinking_intensity = kwargs.get('intensity', 1.0)
        self.duration = kwargs.get('duration', None)  # ミリ秒
        
        # 外枠アニメーションをリセット
        self.border_renderer.animation_time = 0.0
        
        print(f"思考中状態に移行しました（前の状態: {previous_state}, 強度: {self.thinking_intensity}）")
        if self.duration:
            print(f"思考時間: {self.duration/1000:.1f}秒")
    
    def update(self, dt: float) -> Dict[str, Any]:
        """思考中状態の更新処理
        
        Args:
            dt: デルタタイム（秒）
            
        Returns:
            状態の更新情報
        """
        # 外枠アニメーション更新
        self.border_renderer.update(dt)
        
        # 制限時間がある場合のチェック
        should_return_to_idle = False
        if self.duration and self.get_elapsed_time() >= self.duration:
            should_return_to_idle = True
        
        return {
            'state': self.name,
            'thinking_intensity': self.thinking_intensity,
            'elapsed_time': self.get_elapsed_time(),
            'should_return_to_idle': should_return_to_idle,
            'border_animation_time': self.border_renderer.animation_time
        }
    
    def render(self, screen: pygame.Surface):
        """思考中状態の描画処理（外枠オーバーレイのみ）
        
        Args:
            screen: 描画対象のサーフェス
        """
        # 思考中の外枠アニメーションを描画（オーバーレイ）
        adjusted_speed = self.color_change_speed * self.thinking_intensity
        self.border_renderer.draw_animated_thinking_border(
            screen,
            speed=adjusted_speed,
            border_width=self.border_width
        )
    
    def exit(self):
        """思考中状態終了時の処理"""
        super().exit()
        print(f"思考中状態を終了しました（経過時間: {self.get_elapsed_time()/1000:.1f}秒）")
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """イベント処理
        
        Args:
            event: Pygameイベント
            
        Returns:
            イベントが処理されたかどうか
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                # 思考強度を上げる
                self.thinking_intensity = min(2.0, self.thinking_intensity + 0.1)
                print(f"思考強度: {self.thinking_intensity:.1f}")
                return True
            elif event.key == pygame.K_DOWN:
                # 思考強度を下げる
                self.thinking_intensity = max(0.1, self.thinking_intensity - 0.1)
                print(f"思考強度: {self.thinking_intensity:.1f}")
                return True
        
        return False
    
    def set_thinking_intensity(self, intensity: float):
        """思考の強度を設定
        
        Args:
            intensity: 思考強度（0.0-2.0）
        """
        self.thinking_intensity = max(0.1, min(2.0, intensity))
    
    def set_duration(self, duration_ms: int):
        """思考時間を設定
        
        Args:
            duration_ms: 思考時間（ミリ秒、Noneで無制限）
        """
        self.duration = duration_ms
    
    def get_thinking_progress(self) -> float:
        """思考の進行度を取得（制限時間がある場合）
        
        Returns:
            進行度（0.0-1.0）、無制限の場合は0.0
        """
        if not self.duration:
            return 0.0
        
        elapsed = self.get_elapsed_time()
        return min(1.0, elapsed / self.duration)