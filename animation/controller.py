import pygame
import random
from typing import Tuple
from utils.config import config
from utils.constants import BLINK_PRESETS
from animation.easing import lerp, Easing

class BlinkController:
    """まばたきアニメーションを制御するクラス"""
    
    def __init__(self):
        self.animation_config = config.get_animation_config()
        self.reset()
    
    def reset(self):
        """まばたきの状態をリセット"""
        self.last_blink_time = 0
        self.next_blink_interval = random.randint(
            self.animation_config['blink_interval_min'],
            self.animation_config['blink_interval_max']
        )
        self.blink_start_time = 0
        self.is_blinking = False
    
    def update(self, current_time: int):
        """まばたきの状態を更新
        
        Args:
            current_time: 現在時刻（ミリ秒）
        """
        if not self.is_blinking:
            # まばたき開始判定
            if current_time - self.last_blink_time > self.next_blink_interval:
                self.is_blinking = True
                self.blink_start_time = current_time
                self.last_blink_time = current_time
                self.next_blink_interval = random.randint(
                    self.animation_config['blink_interval_min'],
                    self.animation_config['blink_interval_max']
                )
        else:
            # まばたき終了判定
            if current_time - self.blink_start_time > self.animation_config['blink_duration']:
                self.is_blinking = False
    
    def get_blink_ratio(self, current_time: int) -> float:
        """現在のまばたき比率を計算し、最も近いプリセット値に丸める
        
        Args:
            current_time: 現在時刻（ミリ秒）
            
        Returns:
            まばたき比率（0.0-1.0）
        """
        if not self.is_blinking:
            return 1.0
        
        # まばたきの進行度（0.0 -> 1.0 -> 0.0）
        duration = self.animation_config['blink_duration']
        progress = (current_time - self.blink_start_time) / duration
        blink_height_ratio = self.animation_config['blink_height_ratio']
        
        if progress <= 0.5:
            # 閉じていく（1.0 -> BLINK_HEIGHT_RATIO）
            ratio = lerp(1.0, blink_height_ratio, progress * 2, Easing.ease_in_out_cubic)
        else:
            # 開いていく（BLINK_HEIGHT_RATIO -> 1.0）
            ratio = lerp(blink_height_ratio, 1.0, (progress - 0.5) * 2, Easing.ease_in_out_cubic)
        
        ratio = max(blink_height_ratio, min(1.0, ratio))
        
        # 最も近いプリセット値に丸める
        return min(BLINK_PRESETS, key=lambda x: abs(x - ratio))

class EyeMovementController:
    """目の動きを制御するクラス"""
    
    def __init__(self, eye_width: int, eye_height: int):
        self.eye_width = eye_width
        self.eye_height = eye_height
        self.animation_config = config.get_animation_config()
        self.reset()
    
    def reset(self):
        """目の動きの状態をリセット"""
        self.eye_offset = pygame.math.Vector2(0, 0)
        self.target_offset = pygame.math.Vector2(0, 0)
        self.last_look_time = 0
        self.next_look_interval = random.randint(
            self.animation_config['look_interval_min'],
            self.animation_config['look_interval_max']
        )
    
    def get_new_target(self) -> pygame.math.Vector2:
        """新しい視線ターゲットを生成
        
        Returns:
            新しいターゲット座標
        """
        # 目の移動範囲を制限
        max_x = self.eye_width // 1.5
        max_y = self.eye_height // 2.5
        
        x = random.uniform(-max_x, max_x)
        y = random.uniform(-max_y, max_y)
        return pygame.math.Vector2(x, y)
    
    def update(self, current_time: int):
        """目の動きを更新
        
        Args:
            current_time: 現在時刻（ミリ秒）
        """
        # 視線の移動
        if current_time - self.last_look_time > self.next_look_interval:
            self.target_offset = self.get_new_target()
            self.last_look_time = current_time
            self.next_look_interval = random.randint(
                self.animation_config['look_interval_min'],
                self.animation_config['look_interval_max']
            )
        
        # 滑らかな移動
        move_speed = self.animation_config['move_speed']
        self.eye_offset = self.eye_offset.lerp(self.target_offset, move_speed)
    
    def get_current_offset(self) -> pygame.math.Vector2:
        """現在の目のオフセットを取得
        
        Returns:
            現在のオフセット
        """
        return self.eye_offset
    
    def set_target(self, target: pygame.math.Vector2):
        """手動でターゲットを設定
        
        Args:
            target: 新しいターゲット座標
        """
        self.target_offset = target

class AnimationController:
    """アニメーション全体を制御するメインクラス"""
    
    def __init__(self, eye_width: int, eye_height: int):
        self.blink_controller = BlinkController()
        self.eye_movement_controller = EyeMovementController(eye_width, eye_height)
    
    def reset(self):
        """すべてのアニメーションをリセット"""
        self.blink_controller.reset()
        self.eye_movement_controller.reset()
    
    def update(self, current_time: int):
        """すべてのアニメーションを更新
        
        Args:
            current_time: 現在時刻（ミリ秒）
        """
        self.blink_controller.update(current_time)
        self.eye_movement_controller.update(current_time)
    
    def get_animation_state(self, current_time: int) -> dict:
        """現在のアニメーション状態を取得
        
        Args:
            current_time: 現在時刻（ミリ秒）
            
        Returns:
            アニメーション状態の辞書
        """
        return {
            'blink_ratio': self.blink_controller.get_blink_ratio(current_time),
            'eye_offset': self.eye_movement_controller.get_current_offset(),
            'is_blinking': self.blink_controller.is_blinking
        }
    
    def set_eye_target(self, target: pygame.math.Vector2):
        """目のターゲットを手動設定
        
        Args:
            target: 新しいターゲット座標
        """
        self.eye_movement_controller.set_target(target)
    
    def force_blink(self):
        """強制的にまばたきを開始"""
        current_time = pygame.time.get_ticks()
        self.blink_controller.is_blinking = True
        self.blink_controller.blink_start_time = current_time