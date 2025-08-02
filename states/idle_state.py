import pygame
from typing import Dict, Any
from states.base_state import BaseState
from utils.constants import States

class IdleState(BaseState):
    """アイドル状態（まばたき＋視線移動）"""
    
    def __init__(self):
        super().__init__(States.IDLE)
    
    def enter(self, previous_state: str = None, **kwargs):
        """アイドル状態開始時の処理"""
        super().enter(previous_state, **kwargs)
        print(f"アイドル状態に移行しました（前の状態: {previous_state}）")
    
    def update(self, dt: float) -> Dict[str, Any]:
        """アイドル状態の更新処理
        
        Args:
            dt: デルタタイム（秒）
            
        Returns:
            状態の更新情報
        """
        return {
            'state': self.name,
            'elapsed_time': self.get_elapsed_time()
        }
    
    def render(self, screen: pygame.Surface):
        """アイドル状態の描画処理（オーバーレイなし）
        
        Args:
            screen: 描画対象のサーフェス
        """
        # アイドル状態では特別な描画は行わない
        # 目の描画は共通システムで処理される
        pass
    
    def exit(self):
        """アイドル状態終了時の処理"""
        super().exit()
        print(f"アイドル状態を終了しました")
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """イベント処理
        
        Args:
            event: Pygameイベント
            
        Returns:
            イベントが処理されたかどうか
        """
        # アイドル状態では特別なイベント処理は行わない
        # まばたきなどは共通システムで処理される
        return False