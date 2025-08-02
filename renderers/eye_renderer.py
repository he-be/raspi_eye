import pygame
import os
import colorsys
from typing import Dict, Tuple
from utils.config import config
from utils.constants import BLINK_PRESETS

class EyeRenderer:
    """目の描画を担当するレンダラー"""
    
    def __init__(self):
        self.glow_cache: Dict[Tuple[int, int], pygame.Surface] = {}
        self.cache_config = config.get_cache_config()
        self.color_config = config.get_color_config()
        self.ensure_cache_dir()
        
    def ensure_cache_dir(self):
        """キャッシュディレクトリを確保"""
        cache_dir = self.cache_config['directory']
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
    
    def get_cache_filename(self, width: int, height: int, blink_ratio: float) -> str:
        """キャッシュファイル名を生成"""
        closest_ratio = min(BLINK_PRESETS, key=lambda x: abs(x - blink_ratio))
        cache_dir = self.cache_config['directory']
        cache_version = self.cache_config['version']
        return os.path.join(cache_dir, f"glow_{cache_version}_{width}x{height}_{int(closest_ratio*100)}.png")
    
    def load_cached_texture(self, filename: str) -> pygame.Surface:
        """キャッシュされたテクスチャを読み込む"""
        try:
            if os.path.exists(filename):
                return pygame.image.load(filename).convert_alpha()
        except Exception as e:
            print(f"キャッシュ読み込みエラー: {e}")
        return None
    
    def save_texture_cache(self, surface: pygame.Surface, filename: str):
        """テクスチャをキャッシュに保存"""
        try:
            pygame.image.save(surface, filename)
        except Exception as e:
            print(f"キャッシュ保存エラー: {e}")
    
    def create_radial_gradient_surface(self, width: int, height: int, center_color: tuple, edge_color: tuple, steps: int = 20) -> pygame.Surface:
        """放射状グラデーションを持つサーフェスを作成"""
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        center_x = width // 2
        center_y = height // 2
        
        # ステップごとに楕円を描画
        for i in range(steps):
            # 内側から外側へ
            ratio = i / steps
            
            # 現在のステップのサイズ
            current_width = int(width * (1 - ratio))
            current_height = int(height * (1 - ratio))
            
            if current_width <= 0 or current_height <= 0:
                continue
            
            # 色の補間
            r = int(center_color[0] * (1 - ratio) + edge_color[0] * ratio)
            g = int(center_color[1] * (1 - ratio) + edge_color[1] * ratio)
            b = int(center_color[2] * (1 - ratio) + edge_color[2] * ratio)
            
            # アルファ値（外側ほど透明に）
            alpha = int(255 * (1 - ratio))
            
            # 楕円を描画
            rect = pygame.Rect(center_x - current_width // 2, 
                              center_y - current_height // 2,
                              current_width, current_height)
            
            # 一時サーフェスに描画してからブレンド
            temp_surface = pygame.Surface((width, height), pygame.SRCALPHA)
            pygame.draw.ellipse(temp_surface, (r, g, b, alpha), rect)
            surface.blit(temp_surface, (0, 0))
        
        return surface
    
    def generate_glow_layers(self, core_color: tuple, outer_color: tuple, num_layers: int = 6) -> list:
        """コアから最外層まで滑らかに黒にフェードアウトするグローレイヤーを生成"""
        # RGBをHSVに変換（0-255を0-1に正規化）
        core_hsv = colorsys.rgb_to_hsv(core_color[0]/255, core_color[1]/255, core_color[2]/255)
        outer_hsv = colorsys.rgb_to_hsv(outer_color[0]/255, outer_color[1]/255, outer_color[2]/255)
        
        layers = []
        
        for i in range(num_layers):
            # 補間率（0.0 = 最外層, 1.0 = コア）
            t = i / (num_layers - 1)
            
            # サイズ比率（最外層=1.0, コア=0.0）
            size_ratio = 1.0 - t
            
            # 3段階の補間
            if t < 0.5:
                # 最外層から中間まで：黒からouter_colorへ
                local_t = t * 2  # 0.0 -> 1.0
                
                # アルファ値は徐々に上げる
                alpha = 0.1 + 0.4 * local_t
                
                # 黒（V=0）からouter_colorへ補間
                h = outer_hsv[0]
                s = outer_hsv[1]
                v = outer_hsv[2] * local_t  # 0 -> outer_v
                
            else:
                # 中間からコアまで：outer_colorからcore_colorへ
                local_t = (t - 0.5) * 2  # 0.0 -> 1.0
                
                # アルファ値をさらに上げる
                alpha = 0.5 + 0.5 * local_t
                
                # outer_colorからcore_colorへ補間
                h = outer_hsv[0]  # 色相は固定
                s = outer_hsv[1] + (core_hsv[1] - outer_hsv[1]) * local_t
                v = outer_hsv[2] + (core_hsv[2] - outer_hsv[2]) * local_t
            
            # HSVをRGBに戻す
            rgb = colorsys.hsv_to_rgb(h, s, v)
            color = (int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))
            
            layers.append((size_ratio, alpha, color))
        
        return layers
    
    def create_glow_texture(self, width: int, height: int, blink_ratio: float = 1.0) -> pygame.Surface:
        """新しいグローテクスチャを生成"""
        current_height = int(height * blink_ratio)
        
        # グロー用のサーフェスを作成
        glow_radius = int(min(width, current_height) * 0.4)
        total_width = width + glow_radius * 2
        total_height = current_height + glow_radius * 2
        
        # メインのグローサーフェス
        glow_surface = pygame.Surface((total_width, total_height), pygame.SRCALPHA)
        
        # 多層グローエフェクト
        layers = self.generate_glow_layers(
            core_color=self.color_config['white'],
            outer_color=self.color_config['cyan_glow'],
            num_layers=8
        )
        
        for size_ratio, alpha, color in layers:
            layer_width = int(width + glow_radius * 2 * size_ratio)
            layer_height = int(current_height + glow_radius * 2 * size_ratio)
            
            if layer_width > 0 and layer_height > 0:
                # グラデーションサーフェスを作成
                if size_ratio > 0:
                    gradient = self.create_radial_gradient_surface(
                        layer_width, layer_height,
                        (*color, int(255 * alpha)),
                        (*color, 0),
                        steps=15
                    )
                else:
                    # コア部分は単色
                    gradient = pygame.Surface((layer_width, layer_height), pygame.SRCALPHA)
                    pygame.draw.ellipse(gradient, (*color, int(255 * alpha)), 
                                      gradient.get_rect())
                
                # 中心に配置
                x = (total_width - layer_width) // 2
                y = (total_height - layer_height) // 2
                glow_surface.blit(gradient, (x, y))
        
        return glow_surface
    
    def get_or_create_glow_texture(self, width: int, height: int, blink_ratio: float = 1.0) -> pygame.Surface:
        """グローテクスチャを取得またはキャッシュから生成"""
        # まばたき比率を最も近いプリセット値に丸める
        closest_ratio = min(BLINK_PRESETS, key=lambda x: abs(x - blink_ratio))
        current_height = int(height * closest_ratio)
        cache_key = (width, current_height)
        
        # メモリキャッシュをチェック
        if cache_key in self.glow_cache:
            return self.glow_cache[cache_key]
        
        # ファイルキャッシュをチェック
        cache_filename = self.get_cache_filename(width, height, closest_ratio)
        cached_texture = self.load_cached_texture(cache_filename)
        
        if cached_texture:
            self.glow_cache[cache_key] = cached_texture
            return cached_texture
        
        # 新規生成
        print(f"グローテクスチャを生成中: {width}x{current_height}")
        glow_texture = self.create_glow_texture(width, height, closest_ratio)
        
        # ファイルに保存
        self.save_texture_cache(glow_texture, cache_filename)
        
        # メモリキャッシュに保存
        self.glow_cache[cache_key] = glow_texture
        
        return glow_texture
    
    def preload_all_textures(self, width: int, height: int):
        """全てのテクスチャを事前読み込み"""
        print("テクスチャを事前読み込み中...")
        for ratio in BLINK_PRESETS:
            self.get_or_create_glow_texture(width, height, ratio)
        print("テクスチャの読み込み完了")
    
    def draw_smooth_glow_ellipse(self, surface: pygame.Surface, center: tuple, width: int, height: int, blink_ratio: float = 1.0):
        """滑らかなグローエフェクト付きの楕円を描画"""
        current_height = int(height * blink_ratio)
        
        if current_height <= 5:
            return
        
        # グローテクスチャを取得
        glow_texture = self.get_or_create_glow_texture(width, height, blink_ratio)
        
        # 描画位置を計算
        x = center[0] - glow_texture.get_width() // 2
        y = center[1] - glow_texture.get_height() // 2
        
        # メインサーフェスに描画
        surface.blit(glow_texture, (x, y), special_flags=pygame.BLEND_ADD)
    
    def draw_eye(self, surface: pygame.Surface, center: tuple, offset: pygame.math.Vector2, width: int, height: int, blink_ratio: float = 1.0):
        """片目を描画する関数"""
        eye_center = (int(center[0] + offset.x), int(center[1] + offset.y))
        self.draw_smooth_glow_ellipse(surface, eye_center, width, height, blink_ratio)