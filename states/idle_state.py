import pygame
from typing import Dict, Any
from states.base_state import BaseState
from renderers.eye_renderer import EyeRenderer
from animation.controller import AnimationController
from utils.config import config
from utils.constants import States

class IdleState(BaseState):
    """アイドル状態（まばたき＋視線移動）"""
    
    def __init__(self):
        super().__init__(States.IDLE)
        
        # 設定を取得
        self.display_config = config.get_display_config()
        self.eye_config = config.get_eye_config()
        self.color_config = config.get_color_config()
        
        # 目の中心座標を計算
        screen_width = self.display_config['width']
        screen_height = self.display_config['height']
        eye_spacing = self.eye_config['spacing']
        
        self.left_eye_center = (screen_width // 2 - eye_spacing, screen_height // 2)
        self.right_eye_center = (screen_width // 2 + eye_spacing, screen_height // 2)
        
        # レンダラーとアニメーションコントローラーを初期化
        self.eye_renderer = EyeRenderer()
        self.animation_controller = AnimationController(
            self.eye_config['width'],
            self.eye_config['height']
        )
        
        # テクスチャの事前読み込み
        self.eye_renderer.preload_all_textures(
            self.eye_config['width'],
            self.eye_config['height']
        )
    
    def enter(self, previous_state: str = None, **kwargs):
        """アイドル状態開始時の処理"""
        super().enter(previous_state, **kwargs)
        
        # アニメーションをリセット
        self.animation_controller.reset()
        
        print(f"アイドル状態に移行しました（前の状態: {previous_state}）")
    
    def update(self, dt: float) -> Dict[str, Any]:
        """アイドル状態の更新処理
        
        Args:
            dt: デルタタイム（秒）
            
        Returns:
            状態の更新情報
        """
        current_time = pygame.time.get_ticks()
        
        # アニメーション更新
        self.animation_controller.update(current_time)
        
        # アニメーション状態を取得
        animation_state = self.animation_controller.get_animation_state(current_time)
        
        return {
            'state': self.name,
            'animation': animation_state,
            'elapsed_time': self.get_elapsed_time()
        }
    
    def render(self, screen: pygame.Surface):
        """アイドル状態の描画処理
        
        Args:
            screen: 描画対象のサーフェス
        """
        # 背景をクリア
        screen.fill(self.color_config['black'])
        
        # 現在のアニメーション状態を取得
        current_time = pygame.time.get_ticks()
        animation_state = self.animation_controller.get_animation_state(current_time)
        
        eye_offset = animation_state['eye_offset']
        blink_ratio = animation_state['blink_ratio']
        
        # 両目を描画
        self.eye_renderer.draw_eye(
            screen,
            self.left_eye_center,
            eye_offset,
            self.eye_config['width'],
            self.eye_config['height'],
            blink_ratio
        )
        
        self.eye_renderer.draw_eye(
            screen,
            self.right_eye_center,
            eye_offset,
            self.eye_config['width'],
            self.eye_config['height'],
            blink_ratio
        )
    
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
        # スペースキーでまばたき
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.animation_controller.force_blink()
                return True
        
        return False
    
    def force_blink(self):
        """強制的にまばたきを実行"""
        self.animation_controller.force_blink()
    
    def set_eye_target(self, target: pygame.math.Vector2):
        """目のターゲットを手動設定
        
        Args:
            target: 新しいターゲット座標
        """
        self.animation_controller.set_eye_target(target)