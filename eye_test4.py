import pygame
import random
import math
import time
import os
import pickle

# --- 定数 ---
# OSの解像度が固定されているため、Pygameもそれに合わせる
SCREEN_WIDTH = 720
SCREEN_HEIGHT = 480
FPS = 60

# 色
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CYAN_GLOW = (0, 255, 255)
BLUE_WHITE = (180, 200, 255)

# キャッシュディレクトリ
CACHE_DIR = os.path.expanduser("~/.cyber_eyes_cache")
CACHE_VERSION = "v1.2"  # キャッシュバージョン（変更時に再生成）

# --- 初期化 ---
pygame.init()

# フルスクリーンモードでディスプレイを使用
try:
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
except pygame.error as e:
    print(f"ディスプレイの初期化に失敗しました: {e}")
    # フォールバックとしてウィンドウモードで試す
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

pygame.display.set_caption("Cyber Auto Moving Eyes")
clock = pygame.time.Clock()
pygame.mouse.set_visible(False)

# --- 画面サイズに基づいた設定 ---
# 画面の縦横のうち、短い方の辺を基準に目の基本サイズを決定
BASE_SIZE = min(SCREEN_WIDTH, SCREEN_HEIGHT) // 3

# 目の設定（縦長楕円）
EYE_WIDTH = int(BASE_SIZE * 0.6)  # 横幅
EYE_HEIGHT = int(BASE_SIZE * 1.4)  # 縦幅（縦長にする）
EYE_SPACING = int(BASE_SIZE * 1.2)

# 動きの設定
LOOK_INTERVAL_MIN = 1500  # 最小間隔（ミリ秒）
LOOK_INTERVAL_MAX = 4000  # 最大間隔（ミリ秒）
MOVE_SPEED = 0.03

# まばたき設定
BLINK_INTERVAL_MIN = 2000  # 最小まばたき間隔
BLINK_INTERVAL_MAX = 6000  # 最大まばたき間隔
BLINK_DURATION = 200       # まばたき持続時間
BLINK_HEIGHT_RATIO = 0.2   # まばたき時の高さ比率

# まばたきのプリセット比率（事前計算）
BLINK_PRESETS = [1.0, 0.8, 0.6, 0.4, 0.2]  # 5段階のまばたき状態

# --- 変数 ---
# 目の中心座標
left_eye_center = (SCREEN_WIDTH // 2 - EYE_SPACING, SCREEN_HEIGHT // 2)
right_eye_center = (SCREEN_WIDTH // 2 + EYE_SPACING, SCREEN_HEIGHT // 2)

# 目の動き
eye_offset = pygame.math.Vector2(0, 0)
target_offset = pygame.math.Vector2(0, 0)
last_look_time = 0
next_look_interval = random.randint(LOOK_INTERVAL_MIN, LOOK_INTERVAL_MAX)

# まばたき
last_blink_time = 0
next_blink_interval = random.randint(BLINK_INTERVAL_MIN, BLINK_INTERVAL_MAX)
blink_start_time = 0
is_blinking = False

# グローテクスチャのキャッシュ
glow_cache = {}

def ensure_cache_dir():
    """キャッシュディレクトリを確保"""
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)

def get_cache_filename(width, height, blink_ratio):
    """キャッシュファイル名を生成"""
    # まばたき比率を最も近いプリセット値に丸める
    closest_ratio = min(BLINK_PRESETS, key=lambda x: abs(x - blink_ratio))
    return os.path.join(CACHE_DIR, f"glow_{CACHE_VERSION}_{width}x{height}_{int(closest_ratio*100)}.png")

def load_cached_texture(filename):
    """キャッシュされたテクスチャを読み込む"""
    try:
        if os.path.exists(filename):
            return pygame.image.load(filename).convert_alpha()
    except Exception as e:
        print(f"キャッシュ読み込みエラー: {e}")
    return None

def save_texture_cache(surface, filename):
    """テクスチャをキャッシュに保存"""
    try:
        pygame.image.save(surface, filename)
    except Exception as e:
        print(f"キャッシュ保存エラー: {e}")

def get_new_target():
    """新しい視線ターゲットを生成"""
    # 目の移動範囲を制限
    max_x = EYE_WIDTH // 1.5
    max_y = EYE_HEIGHT // 2.5
    
    x = random.uniform(-max_x, max_x)
    y = random.uniform(-max_y, max_y)
    return pygame.math.Vector2(x, y)

def create_radial_gradient_surface(width, height, center_color, edge_color, steps=20):
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
    
def generate_glow_layers(core_color, outer_color, num_layers=6):
    """コアから最外層まで滑らかに黒にフェードアウトするグローレイヤーを生成"""
    import colorsys
    
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

def create_glow_texture(width, height, blink_ratio=1.0):
    """新しいグローテクスチャを生成"""
    current_height = int(height * blink_ratio)
    
    # グロー用のサーフェスを作成
    glow_radius = int(min(width, current_height) * 0.4)
    total_width = width + glow_radius * 2
    total_height = current_height + glow_radius * 2
    
    # メインのグローサーフェス
    glow_surface = pygame.Surface((total_width, total_height), pygame.SRCALPHA)
    
    # 多層グローエフェクト
    layers = generate_glow_layers(
        core_color=WHITE,           # コアの色
        outer_color=CYAN_GLOW,     # 最外層の色
        num_layers=8                # レイヤー数
    )
    
    for size_ratio, alpha, color in layers:
        layer_width = int(width + glow_radius * 2 * size_ratio)
        layer_height = int(current_height + glow_radius * 2 * size_ratio)
        
        if layer_width > 0 and layer_height > 0:
            # グラデーションサーフェスを作成
            if size_ratio > 0:
                gradient = create_radial_gradient_surface(
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

def get_or_create_glow_texture(width, height, blink_ratio=1.0):
    """グローテクスチャを取得またはキャッシュから生成"""
    # まばたき比率を最も近いプリセット値に丸める
    closest_ratio = min(BLINK_PRESETS, key=lambda x: abs(x - blink_ratio))
    current_height = int(height * closest_ratio)
    cache_key = (width, current_height)
    
    # メモリキャッシュをチェック
    if cache_key in glow_cache:
        return glow_cache[cache_key]
    
    # ファイルキャッシュをチェック
    cache_filename = get_cache_filename(width, height, closest_ratio)
    cached_texture = load_cached_texture(cache_filename)
    
    if cached_texture:
        glow_cache[cache_key] = cached_texture
        return cached_texture
    
    # 新規生成
    print(f"グローテクスチャを生成中: {width}x{current_height}")
    glow_texture = create_glow_texture(width, height, closest_ratio)
    
    # ファイルに保存
    save_texture_cache(glow_texture, cache_filename)
    
    # メモリキャッシュに保存
    glow_cache[cache_key] = glow_texture
    
    return glow_texture

def preload_all_textures():
    """全てのテクスチャを事前読み込み"""
    print("テクスチャを事前読み込み中...")
    for ratio in BLINK_PRESETS:
        get_or_create_glow_texture(EYE_WIDTH, EYE_HEIGHT, ratio)
    print("テクスチャの読み込み完了")

def draw_smooth_glow_ellipse(surface, center, width, height, blink_ratio=1.0):
    """滑らかなグローエフェクト付きの楕円を描画"""
    current_height = int(height * blink_ratio)
    
    if current_height <= 5:
        return
    
    # グローテクスチャを取得
    glow_texture = get_or_create_glow_texture(width, height, blink_ratio)
    
    # 描画位置を計算
    x = center[0] - glow_texture.get_width() // 2
    y = center[1] - glow_texture.get_height() // 2
    
    # メインサーフェスに描画
    surface.blit(glow_texture, (x, y), special_flags=pygame.BLEND_ADD)

def draw_eye(center, offset, blink_ratio=1.0):
    """片目を描画する関数"""
    eye_center = (int(center[0] + offset.x), int(center[1] + offset.y))
    draw_smooth_glow_ellipse(screen, eye_center, EYE_WIDTH, EYE_HEIGHT, blink_ratio)

def update_blink(current_time):
    """まばたきの状態を更新"""
    global last_blink_time, next_blink_interval, blink_start_time, is_blinking
    
    if not is_blinking:
        # まばたき開始判定
        if current_time - last_blink_time > next_blink_interval:
            is_blinking = True
            blink_start_time = current_time
            last_blink_time = current_time
            next_blink_interval = random.randint(BLINK_INTERVAL_MIN, BLINK_INTERVAL_MAX)
    else:
        # まばたき終了判定
        if current_time - blink_start_time > BLINK_DURATION:
            is_blinking = False

def get_blink_ratio(current_time):
    """現在のまばたき比率を計算し、最も近いプリセット値に丸める"""
    if not is_blinking:
        return 1.0
    
    # まばたきの進行度（0.0 -> 1.0 -> 0.0）
    progress = (current_time - blink_start_time) / BLINK_DURATION
    
    if progress <= 0.5:
        # 閉じていく（1.0 -> BLINK_HEIGHT_RATIO）
        ratio = 1.0 - (1.0 - BLINK_HEIGHT_RATIO) * (progress * 2)
    else:
        # 開いていく（BLINK_HEIGHT_RATIO -> 1.0）
        ratio = BLINK_HEIGHT_RATIO + (1.0 - BLINK_HEIGHT_RATIO) * ((progress - 0.5) * 2)
    
    ratio = max(BLINK_HEIGHT_RATIO, min(1.0, ratio))
    
    # 最も近いプリセット値に丸める
    return min(BLINK_PRESETS, key=lambda x: abs(x - ratio))

# --- 初期化処理 ---
ensure_cache_dir()
preload_all_textures()

# --- メインループ ---
running = True
while running:
    # イベント処理
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False

    # --- 更新処理 ---
    current_time = pygame.time.get_ticks()
    
    # 視線の移動
    if current_time - last_look_time > next_look_interval:
        target_offset = get_new_target()
        last_look_time = current_time
        next_look_interval = random.randint(LOOK_INTERVAL_MIN, LOOK_INTERVAL_MAX)
    
    eye_offset = eye_offset.lerp(target_offset, MOVE_SPEED)
    
    # まばたきの更新
    update_blink(current_time)
    blink_ratio = get_blink_ratio(current_time)

    # --- 描画処理 ---
    screen.fill(BLACK)
    
    # 両目を描画
    draw_eye(left_eye_center, eye_offset, blink_ratio)
    draw_eye(right_eye_center, eye_offset, blink_ratio)
    
    pygame.display.flip()

    # フレームレートを維持
    clock.tick(FPS)

# --- 終了処理 ---
pygame.quit()