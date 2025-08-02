from typing import Dict, Optional, Any
import pygame
from states.base_state import BaseState
from utils.events import event_system, EventType
from utils.constants import States

class StateMachine:
    """状態機械の管理クラス"""
    
    def __init__(self):
        self._states: Dict[str, BaseState] = {}
        self._current_state: Optional[BaseState] = None
        self._previous_state: Optional[str] = None
        
    def add_state(self, state: BaseState):
        """状態を追加"""
        self._states[state.name] = state
        
    def remove_state(self, state_name: str):
        """状態を削除"""
        if state_name in self._states:
            if self._current_state and self._current_state.name == state_name:
                self._current_state.exit()
                self._current_state = None
            del self._states[state_name]
            
    def change_state(self, state_name: str, **kwargs) -> bool:
        """状態を変更
        
        Args:
            state_name: 変更先の状態名
            **kwargs: 状態に渡すパラメータ
            
        Returns:
            状態変更が成功したかどうか
        """
        if state_name not in self._states:
            print(f"未知の状態です: {state_name}")
            return False
            
        # 同じ状態への変更は無視
        if self._current_state and self._current_state.name == state_name:
            return True
            
        previous_state_name = None
        
        # 現在の状態を終了
        if self._current_state:
            previous_state_name = self._current_state.name
            self._current_state.exit()
            
        # 新しい状態を開始
        self._previous_state = previous_state_name
        self._current_state = self._states[state_name]
        self._current_state.enter(previous_state=previous_state_name, **kwargs)
        
        # 状態変更イベントを発行
        event_system.emit(EventType.STATE_CHANGED, {
            'previous_state': previous_state_name,
            'current_state': state_name,
            'parameters': kwargs
        })
        
        return True
        
    def update(self, dt: float) -> Dict[str, Any]:
        """現在の状態を更新
        
        Args:
            dt: デルタタイム（秒）
            
        Returns:
            状態の更新情報
        """
        if self._current_state:
            return self._current_state.update(dt)
        return {}
        
    def render(self, screen: pygame.Surface):
        """現在の状態を描画"""
        if self._current_state:
            self._current_state.render(screen)
            
    def handle_event(self, event: pygame.event.Event) -> bool:
        """イベントを現在の状態に転送
        
        Args:
            event: Pygameイベント
            
        Returns:
            イベントが処理されたかどうか
        """
        if self._current_state:
            return self._current_state.handle_event(event)
        return False
        
    @property
    def current_state_name(self) -> Optional[str]:
        """現在の状態名を取得"""
        return self._current_state.name if self._current_state else None
        
    @property
    def previous_state_name(self) -> Optional[str]:
        """前の状態名を取得"""
        return self._previous_state
        
    @property
    def current_state(self) -> Optional[BaseState]:
        """現在の状態オブジェクトを取得"""
        return self._current_state

    def get_current_state(self):
        """現在の状態オブジェクトを取得（エイリアス）"""
        return self.current_state
        
    def get_available_states(self) -> list:
        """利用可能な状態のリストを取得"""
        return list(self._states.keys())
        
    def is_state_active(self, state_name: str) -> bool:
        """指定した状態がアクティブかどうか"""
        return (self._current_state is not None and 
                self._current_state.name == state_name)
                
    def get_state_info(self) -> Dict[str, Any]:
        """状態機械の情報を取得"""
        return {
            'current_state': self.current_state_name,
            'previous_state': self.previous_state_name,
            'available_states': self.get_available_states(),
            'elapsed_time': self._current_state.get_elapsed_time() if self._current_state else 0
        }