#!/usr/bin/env python3

import pygame
import sys
import os

# パッケージのルートディレクトリをPythonパスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.state_machine import StateMachine
from states.idle_state import IdleState
from utils.config import config
from utils.events import event_system, EventType

class RobotFaceApp:
    """ロボット顔表示アプリケーションのメインクラス"""
    
    def __init__(self):
        # 設定を読み込み
        self.display_config = config.get_display_config()
        
        # Pygame初期化
        pygame.init()
        
        # ディスプレイ設定
        self.setup_display()
        
        # クロック設定
        self.clock = pygame.time.Clock()
        self.fps = self.display_config['fps']
        
        # 状態機械の初期化
        self.state_machine = StateMachine()
        self.setup_states()
        
        # イベントリスナーの設定
        self.setup_event_listeners()
        
        # 実行フラグ
        self.running = True
        
        print("ロボット顔表示システムを初期化しました")
        print(f"解像度: {self.display_config['width']}x{self.display_config['height']}")
        print(f"FPS: {self.fps}")
        print("ESCキーで終了します")
    
    def setup_display(self):
        """ディスプレイを設定"""
        width = self.display_config['width']
        height = self.display_config['height']
        fullscreen = self.display_config['fullscreen']
        
        try:
            if fullscreen:
                self.screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)
            else:
                self.screen = pygame.display.set_mode((width, height))
        except pygame.error as e:
            print(f"フルスクリーンモードでの初期化に失敗: {e}")
            print("ウィンドウモードで実行します")
            self.screen = pygame.display.set_mode((width, height))
        
        pygame.display.set_caption("Communication Robot Face Display")
        pygame.mouse.set_visible(False)
    
    def setup_states(self):
        """状態を設定"""
        # アイドル状態を追加
        idle_state = IdleState()
        self.state_machine.add_state(idle_state)
        
        # 初期状態をアイドルに設定
        self.state_machine.change_state("idle")
    
    def setup_event_listeners(self):
        """イベントリスナーを設定"""
        def on_state_changed(event):
            print(f"状態変更: {event.data['previous_state']} -> {event.data['current_state']}")
        
        event_system.subscribe(EventType.STATE_CHANGED, on_state_changed)
    
    def handle_events(self):
        """イベント処理"""
        for event in pygame.event.get():
            # 終了イベント
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_F11:
                    # フルスクリーン切り替え
                    pygame.display.toggle_fullscreen()
            
            # 現在の状態にイベントを転送
            self.state_machine.handle_event(event)
    
    def update(self, dt: float):
        """更新処理
        
        Args:
            dt: デルタタイム（秒）
        """
        self.state_machine.update(dt)
    
    def render(self):
        """描画処理"""
        self.state_machine.render(self.screen)
        pygame.display.flip()
    
    def run(self):
        """メインループ"""
        print("アプリケーションを開始します...")
        
        last_time = pygame.time.get_ticks()
        
        while self.running:
            # デルタタイムを計算
            current_time = pygame.time.get_ticks()
            dt = (current_time - last_time) / 1000.0  # 秒に変換
            last_time = current_time
            
            # 処理
            self.handle_events()
            self.update(dt)
            self.render()
            
            # フレームレート制御
            self.clock.tick(self.fps)
        
        self.cleanup()
    
    def cleanup(self):
        """終了処理"""
        print("アプリケーションを終了します...")
        pygame.quit()
        sys.exit()

def main():
    """メイン関数"""
    try:
        app = RobotFaceApp()
        app.run()
    except KeyboardInterrupt:
        print("\nキーボード割り込みで終了しました")
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
    finally:
        pygame.quit()

if __name__ == "__main__":
    main()