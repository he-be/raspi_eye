from typing import Dict, List, Callable, Any
from enum import Enum
import time

class EventType(Enum):
    """イベントタイプの定義"""
    STATE_CHANGED = "state_changed"
    COMMAND_RECEIVED = "command_received" 
    ANIMATION_STARTED = "animation_started"
    ANIMATION_FINISHED = "animation_finished"
    ERROR_OCCURRED = "error_occurred"

class Event:
    """イベントデータクラス"""
    def __init__(self, event_type: EventType, data: Dict[str, Any] = None):
        self.type = event_type
        self.data = data or {}
        self.timestamp = time.time()

class EventSystem:
    """イベントシステム（Observer パターン）"""
    
    def __init__(self):
        self._listeners: Dict[EventType, List[Callable]] = {}
    
    def subscribe(self, event_type: EventType, callback: Callable[[Event], None]):
        """イベントリスナーを登録"""
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        
        if callback not in self._listeners[event_type]:
            self._listeners[event_type].append(callback)
    
    def unsubscribe(self, event_type: EventType, callback: Callable[[Event], None]):
        """イベントリスナーを解除"""
        if event_type in self._listeners:
            try:
                self._listeners[event_type].remove(callback)
            except ValueError:
                pass
    
    def emit(self, event_type: EventType, data: Dict[str, Any] = None):
        """イベントを発行"""
        event = Event(event_type, data)
        
        if event_type in self._listeners:
            for callback in self._listeners[event_type]:
                try:
                    callback(event)
                except Exception as e:
                    print(f"イベントリスナーでエラーが発生しました: {e}")
    
    def clear_listeners(self, event_type: EventType = None):
        """リスナーをクリア"""
        if event_type:
            self._listeners[event_type] = []
        else:
            self._listeners.clear()

# グローバルイベントシステム
event_system = EventSystem()