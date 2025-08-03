import pygame
from typing import Dict, Any
from states.base_state import BaseState
from utils.config import config
from utils.constants import States

class SleepingState(BaseState):
    """休止状態（睡眠中の円弧状の目）"""
    
    def __init__(self):
        super().__init__(States.SLEEPING)
        
        # 設定を取得
        self.color_config = config.get_color_config()
        
        # アニメーション用の変数
        self.breathing_phase = 0.0  # 呼吸アニメーション用
        self.breathing_speed = 0.5  # 呼吸の速度
        self.breathing_amplitude = 5  # 呼吸の振幅（ピクセル）
    
    def enter(self, previous_state: str = None, **kwargs):
        """休止状態開始時の処理"""
        super().enter(previous_state, **kwargs)
        
        # アニメーションをリセット
        self.breathing_phase = 0.0
        
        print(f"休止状態に移行しました（前の状態: {previous_state}）")
    
    def update(self, dt: float) -> Dict[str, Any]:
        """休止状態の更新処理
        
        Args:
            dt: デルタタイム（秒）
            
        Returns:
            状態の更新情報
        """
        # 呼吸アニメーションの更新
        self.breathing_phase += dt * self.breathing_speed * 2 * 3.14159  # 2π
        
        return {
            'state': self.name,
            'elapsed_time': self.get_elapsed_time(),
            'breathing_offset': self.get_breathing_offset()
        }
    
    def render(self, screen: pygame.Surface):
        """休止状態の描画処理（オーバーレイなし）
        
        Args:
            screen: 描画対象のサーフェス
        """
        # 休止状態では特別な描画は行わない
        # 円弧の目の描画は共通システムで処理される
        pass
    
    def exit(self):
        """休止状態終了時の処理"""
        super().exit()
        print(f"休止状態を終了しました")
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """イベント処理
        
        Args:
            event: Pygameイベント
            
        Returns:
            イベントが処理されたかどうか
        """
        # 休止状態では特別なイベント処理は行わない
        return False
    
    def get_breathing_offset(self) -> float:
        """呼吸アニメーションのオフセット値を取得
        
        Returns:
            Y軸方向のオフセット値
        """
        import math
        return math.sin(self.breathing_phase) * self.breathing_amplitude