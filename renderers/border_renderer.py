import pygame
import math
import random
from typing import Tuple, List
from utils.config import config
from animation.easing import lerp, lerp_color, Easing

class BorderRenderer:
    """外枠描画を担当するレンダラー"""
    
    def __init__(self):
        self.display_config = config.get_display_config()
        self.color_config = config.get_color_config()
        
        # 外枠の基本設定
        self.screen_width = self.display_config['width']
        self.screen_height = self.display_config['height']
        
        # デフォルトの外枠設定
        self.default_border_width = 8
        self.default_margin = 10
        
        # アニメーション用の変数
        self.animation_time = 0.0
        self.color_phase = 0.0
        self.pulse_phase = 0.0
        
    def update(self, dt: float):
        """アニメーション状態を更新
        
        Args:
            dt: デルタタイム（秒）
        """
        self.animation_time += dt
        self.color_phase = math.fmod(self.animation_time * 0.5, 2 * math.pi)  # 2秒で1周
        self.pulse_phase = math.fmod(self.animation_time * 2.0, 2 * math.pi)  # 0.5秒で1周
    
    def get_border_rect(self, margin: int = None) -> pygame.Rect:
        """外枠の矩形を取得
        
        Args:
            margin: 画面端からのマージン
            
        Returns:
            外枠の矩形
        """
        if margin is None:
            margin = self.default_margin
            
        return pygame.Rect(
            margin,
            margin,
            self.screen_width - margin * 2,
            self.screen_height - margin * 2
        )
    
    def draw_solid_border(self, surface: pygame.Surface, color: Tuple[int, int, int], 
                         border_width: int = None, margin: int = None):
        """単色の外枠を描画
        
        Args:
            surface: 描画対象のサーフェス
            color: 枠の色
            border_width: 枠の太さ
            margin: 画面端からのマージン
        """
        if border_width is None:
            border_width = self.default_border_width
            
        border_rect = self.get_border_rect(margin)
        pygame.draw.rect(surface, color, border_rect, border_width)
    
    def draw_blinking_border(self, surface: pygame.Surface, color: Tuple[int, int, int],
                           blink_speed: float = 1.0, border_width: int = None, 
                           margin: int = None):
        """点滅する外枠を描画
        
        Args:
            surface: 描画対象のサーフェス
            color: 基本色
            blink_speed: 点滅速度（倍率）
            border_width: 枠の太さ
            margin: 画面端からのマージン
        """
        if border_width is None:
            border_width = self.default_border_width
            
        # 点滅のアルファ値を計算
        blink_phase = self.animation_time * blink_speed * 4.0  # 4倍速で点滅
        alpha_ratio = (math.sin(blink_phase) + 1.0) / 2.0  # 0.0 - 1.0
        alpha_ratio = Easing.ease_in_out_cubic(alpha_ratio)  # より滑らかな点滅
        
        # 色にアルファ値を適用
        min_alpha = 0.2
        max_alpha = 1.0
        alpha = lerp(min_alpha, max_alpha, alpha_ratio)
        
        blinking_color = (
            int(color[0] * alpha),
            int(color[1] * alpha),
            int(color[2] * alpha)
        )
        
        self.draw_solid_border(surface, blinking_color, border_width, margin)
    
    def draw_rainbow_border(self, surface: pygame.Surface, speed: float = 1.0,
                          border_width: int = None, margin: int = None):
        """レインボー色で変化する外枠を描画
        
        Args:
            surface: 描画対象のサーフェス
            speed: 色変化の速度
            border_width: 枠の太さ
            margin: 画面端からのマージン
        """
        if border_width is None:
            border_width = self.default_border_width
            
        border_rect = self.get_border_rect(margin)
        
        # HSV色空間で色を生成
        hue_phase = self.animation_time * speed * 60.0  # 度数で計算
        hue = math.fmod(hue_phase, 360.0)
        
        # HSVからRGBに変換
        import colorsys
        rgb = colorsys.hsv_to_rgb(hue / 360.0, 1.0, 1.0)
        color = (int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))
        
        pygame.draw.rect(surface, color, border_rect, border_width)
    
    def draw_pulsing_border(self, surface: pygame.Surface, color: Tuple[int, int, int],
                          pulse_speed: float = 1.0, border_width: int = None,
                          margin: int = None):
        """パルス（呼吸）する外枠を描画
        
        Args:
            surface: 描画対象のサーフェス
            color: 基本色
            pulse_speed: パルス速度
            border_width: 基本の枠の太さ
            margin: 画面端からのマージン
        """
        if border_width is None:
            border_width = self.default_border_width
            
        # パルスの強度を計算
        pulse_phase = self.animation_time * pulse_speed * 2.0
        pulse_ratio = (math.sin(pulse_phase) + 1.0) / 2.0
        pulse_ratio = Easing.ease_in_out_sine(pulse_ratio)
        
        # 枠の太さと色の強度を変化
        min_width = border_width
        max_width = border_width * 2
        current_width = int(lerp(min_width, max_width, pulse_ratio))
        
        min_intensity = 0.5
        max_intensity = 1.0
        intensity = lerp(min_intensity, max_intensity, pulse_ratio)
        
        pulsing_color = (
            int(color[0] * intensity),
            int(color[1] * intensity),
            int(color[2] * intensity)
        )
        
        self.draw_solid_border(surface, pulsing_color, current_width, margin)
    
    def draw_gradient_border(self, surface: pygame.Surface, 
                           colors: List[Tuple[int, int, int]], 
                           border_width: int = None, margin: int = None):
        """グラデーション外枠を描画
        
        Args:
            surface: 描画対象のサーフェス
            colors: グラデーションの色リスト
            border_width: 枠の太さ
            margin: 画面端からのマージン
        """
        if border_width is None:
            border_width = self.default_border_width
        if len(colors) < 2:
            colors = [self.color_config['white'], self.color_config['cyan_glow']]
            
        border_rect = self.get_border_rect(margin)
        
        # 複数の太さで描画してグラデーション効果を作成
        for i in range(border_width):
            ratio = i / max(1, border_width - 1)
            
            # 色を補間
            if len(colors) == 2:
                color = lerp_color(colors[0], colors[1], ratio)
            else:
                # 複数色の場合は段階的に補間
                segment_size = 1.0 / (len(colors) - 1)
                segment_index = min(int(ratio / segment_size), len(colors) - 2)
                local_ratio = (ratio - segment_index * segment_size) / segment_size
                color = lerp_color(colors[segment_index], colors[segment_index + 1], local_ratio)
            
            # 外側から内側に向けて描画
            current_rect = pygame.Rect(
                border_rect.x + i,
                border_rect.y + i,
                border_rect.width - i * 2,
                border_rect.height - i * 2
            )
            
            if current_rect.width > 0 and current_rect.height > 0:
                pygame.draw.rect(surface, color, current_rect, 1)
    
    def draw_animated_thinking_border(self, surface: pygame.Surface, 
                                    speed: float = 1.0, border_width: int = None,
                                    margin: int = None):
        """思考中状態用のアニメーション外枠
        
        Args:
            surface: 描画対象のサーフェス
            speed: アニメーション速度
            border_width: 枠の太さ
            margin: 画面端からのマージン
        """
        if border_width is None:
            border_width = self.default_border_width
            
        # ランダムな色の変化とパルス効果を組み合わせ
        thinking_colors = [
            (100, 200, 255),  # 薄い青
            (255, 200, 100),  # 薄いオレンジ
            (200, 255, 100),  # 薄い緑
            (255, 100, 200),  # 薄いピンク
            (200, 100, 255),  # 薄い紫
        ]
        
        # 時間ベースで色を選択
        color_index = int(self.animation_time * speed) % len(thinking_colors)
        next_color_index = (color_index + 1) % len(thinking_colors)
        
        # 色の補間
        color_transition = math.fmod(self.animation_time * speed, 1.0)
        current_color = lerp_color(
            thinking_colors[color_index],
            thinking_colors[next_color_index],
            Easing.ease_in_out_cubic(color_transition)
        )
        
        # パルス効果と組み合わせ
        self.draw_pulsing_border(surface, current_color, speed * 0.7, border_width, margin)