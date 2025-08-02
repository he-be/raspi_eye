from abc import ABC, abstractmethod
import pygame
from typing import Dict, Any

class BaseState(ABC):
    """状態の基底クラス（State パターン）"""
    
    def __init__(self, name: str):
        self.name = name
        self.is_active = False
        self.start_time = 0
        
    @abstractmethod
    def enter(self, previous_state: str = None, **kwargs):
        """状態開始時の処理"""
        self.is_active = True
        self.start_time = pygame.time.get_ticks()
        
    @abstractmethod
    def update(self, dt: float) -> Dict[str, Any]:
        """状態の更新処理
        
        Args:
            dt: デルタタイム（秒）
            
        Returns:
            状態の更新情報を含む辞書
        """
        pass
        
    @abstractmethod
    def render(self, screen: pygame.Surface):
        """描画処理
        
        Args:
            screen: 描画対象のサーフェス
        """
        pass
        
    @abstractmethod
    def exit(self):
        """状態終了時の処理"""
        self.is_active = False
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """イベント処理（オプション）
        
        Args:
            event: Pygameイベント
            
        Returns:
            イベントが処理されたかどうか
        """
        return False
        
    def get_elapsed_time(self) -> int:
        """状態開始からの経過時間を取得（ミリ秒）"""
        if self.is_active:
            return pygame.time.get_ticks() - self.start_time
        return 0
        
    def __repr__(self):
        return f"<{self.__class__.__name__}(name={self.name}, active={self.is_active})>"