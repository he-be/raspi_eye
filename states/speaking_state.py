import pygame
from typing import Dict, Any, List
from states.base_state import BaseState
from renderers.border_renderer import BorderRenderer
from utils.config import config
from utils.constants import States

class SpeakingState(BaseState):
    """発話中状態（白い点滅外枠オーバーレイ）"""
    
    def __init__(self):
        super().__init__(States.SPEAKING)
        
        # 設定を取得
        self.color_config = config.get_color_config()
        self.speaking_config = config.get_state_config('speaking')
        
        # 外枠レンダラーを初期化
        self.border_renderer = BorderRenderer()
        
        # 発話中状態の設定
        self.border_width = self.speaking_config.get('border_width', 8)
        self.blink_speed = self.speaking_config.get('blink_speed', 4.0)
        self.intensity_default = self.speaking_config.get('intensity_default', 1.0)
        
        # 発話状態
        self.speaking_intensity = self.intensity_default
        self.is_speaking = True
        self.speech_data = []  # 音声データや強度データ
        self.duration = None  # 無制限
        
        # 疑似リップシンク用のデータ
        self.lip_sync_pattern = []
        self.lip_sync_index = 0
    
    def enter(self, previous_state: str = None, **kwargs):
        """発話中状態開始時の処理"""
        super().enter(previous_state, **kwargs)
        
        # パラメータを取得
        self.speaking_intensity = kwargs.get('intensity', self.intensity_default)
        self.duration = kwargs.get('duration', None)  # ミリ秒
        self.lip_sync_pattern = kwargs.get('lip_sync_pattern', [])
        
        # 疑似リップシンクパターンがない場合はランダム生成
        if not self.lip_sync_pattern:
            self._generate_random_lip_sync_pattern()
        
        # 外枠アニメーションをリセット
        self.border_renderer.animation_time = 0.0
        self.lip_sync_index = 0
        self.is_speaking = True
        
        print(f"発話中状態に移行しました（前の状態: {previous_state}, 強度: {self.speaking_intensity}）")
        if self.duration:
            print(f"発話時間: {self.duration/1000:.1f}秒")
    
    def _generate_random_lip_sync_pattern(self):
        """ランダムな疑似リップシンクパターンを生成"""
        import random
        
        # 0.1秒間隔で強度を設定（0.0-1.0）
        pattern_length = 50  # 5秒分
        self.lip_sync_pattern = []
        
        for i in range(pattern_length):
            # より自然な発話パターンを生成
            if i < 5:  # 開始部分は徐々に強く
                intensity = (i / 5) * random.uniform(0.7, 1.0)
            elif i > pattern_length - 10:  # 終了部分は徐々に弱く
                remaining = pattern_length - i
                intensity = (remaining / 10) * random.uniform(0.3, 0.8)
            else:  # 中間部分はランダム
                base_intensity = random.uniform(0.4, 1.0)
                # 隣接する値との連続性を保つ
                if self.lip_sync_pattern:
                    prev_intensity = self.lip_sync_pattern[-1]
                    intensity = (base_intensity + prev_intensity) / 2
                else:
                    intensity = base_intensity
            
            self.lip_sync_pattern.append(max(0.0, min(1.0, intensity)))
    
    def update(self, dt: float) -> Dict[str, Any]:
        """発話中状態の更新処理
        
        Args:
            dt: デルタタイム（秒）
            
        Returns:
            状態の更新情報
        """
        # 外枠アニメーション更新
        self.border_renderer.update(dt)
        
        # 疑似リップシンクの更新
        self._update_lip_sync()
        
        # 制限時間がある場合のチェック
        should_return_to_idle = False
        if self.duration and self.get_elapsed_time() >= self.duration:
            should_return_to_idle = True
            self.is_speaking = False
        
        # リップシンクパターンが終了した場合
        if self.lip_sync_index >= len(self.lip_sync_pattern):
            should_return_to_idle = True
            self.is_speaking = False
        
        return {
            'state': self.name,
            'speaking_intensity': self.speaking_intensity,
            'is_speaking': self.is_speaking,
            'elapsed_time': self.get_elapsed_time(),
            'should_return_to_idle': should_return_to_idle,
            'lip_sync_progress': self.get_lip_sync_progress(),
            'current_lip_intensity': self.get_current_lip_intensity()
        }
    
    def _update_lip_sync(self):
        """疑似リップシンクの更新"""
        if not self.lip_sync_pattern:
            return
            
        # 100ms間隔でパターンを更新
        elapsed_ms = self.get_elapsed_time()
        target_index = int(elapsed_ms / 100)  # 100ms間隔
        
        if target_index < len(self.lip_sync_pattern):
            self.lip_sync_index = target_index
        else:
            self.lip_sync_index = len(self.lip_sync_pattern)
    
    def get_current_lip_intensity(self) -> float:
        """現在のリップシンク強度を取得"""
        if (not self.lip_sync_pattern or 
            self.lip_sync_index >= len(self.lip_sync_pattern)):
            return 0.0
        
        return self.lip_sync_pattern[self.lip_sync_index]
    
    def render(self, screen: pygame.Surface):
        """発話中状態の描画処理（外枠オーバーレイのみ）
        
        Args:
            screen: 描画対象のサーフェス
        """
        # 発話中の白い点滅外枠を描画（オーバーレイ）
        if self.is_speaking:
            lip_intensity = self.get_current_lip_intensity()
            adjusted_speed = self.blink_speed * self.speaking_intensity * (0.5 + lip_intensity * 0.5)
            
            self.border_renderer.draw_blinking_border(
                screen,
                self.color_config['white'],
                blink_speed=adjusted_speed,
                border_width=self.border_width
            )
    
    def exit(self):
        """発話中状態終了時の処理"""
        super().exit()
        print(f"発話中状態を終了しました（経過時間: {self.get_elapsed_time()/1000:.1f}秒）")
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """イベント処理
        
        Args:
            event: Pygameイベント
            
        Returns:
            イベントが処理されたかどうか
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                # 発話強度を上げる
                self.speaking_intensity = min(2.0, self.speaking_intensity + 0.1)
                print(f"発話強度: {self.speaking_intensity:.1f}")
                return True
            elif event.key == pygame.K_DOWN:
                # 発話強度を下げる
                self.speaking_intensity = max(0.1, self.speaking_intensity - 0.1)
                print(f"発話強度: {self.speaking_intensity:.1f}")
                return True
            elif event.key == pygame.K_RETURN:
                # 発話の停止/再開
                self.is_speaking = not self.is_speaking
                print(f"発話状態: {'ON' if self.is_speaking else 'OFF'}")
                return True
        
        return False
    
    def set_speaking_intensity(self, intensity: float):
        """発話の強度を設定
        
        Args:
            intensity: 発話強度（0.0-2.0）
        """
        self.speaking_intensity = max(0.1, min(2.0, intensity))
    
    def set_lip_sync_pattern(self, pattern: List[float]):
        """リップシンクパターンを設定
        
        Args:
            pattern: 強度のリスト（0.0-1.0）
        """
        self.lip_sync_pattern = [max(0.0, min(1.0, x)) for x in pattern]
        self.lip_sync_index = 0
    
    def set_duration(self, duration_ms: int):
        """発話時間を設定
        
        Args:
            duration_ms: 発話時間（ミリ秒、Noneで無制限）
        """
        self.duration = duration_ms
    
    def stop_speaking(self):
        """発話を停止"""
        self.is_speaking = False
    
    def resume_speaking(self):
        """発話を再開"""
        self.is_speaking = True
    
    def get_lip_sync_progress(self) -> float:
        """リップシンクの進行度を取得
        
        Returns:
            進行度（0.0-1.0）
        """
        if not self.lip_sync_pattern:
            return 1.0
        
        return min(1.0, self.lip_sync_index / len(self.lip_sync_pattern))
    
    def get_speaking_progress(self) -> float:
        """発話の進行度を取得（制限時間がある場合）
        
        Returns:
            進行度（0.0-1.0）、無制限の場合は0.0
        """
        if not self.duration:
            return 0.0
        
        elapsed = self.get_elapsed_time()
        return min(1.0, elapsed / self.duration)