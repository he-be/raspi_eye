#!/usr/bin/env python3

import pygame
import sys
import os
import asyncio

# パッケージのルートディレクトリをPythonパスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.state_machine import StateMachine
from states.idle_state import IdleState
from states.thinking_state import ThinkingState
from states.speaking_state import SpeakingState
from renderers.eye_renderer import EyeRenderer
from renderers.border_renderer import BorderRenderer
from animation.controller import AnimationController
from utils.config import config
from utils.events import event_system, EventType

class RobotFaceApp:
    """ロボット顔表示アプリケーションのメインクラス"""
    
    def __init__(self, enable_command_interface: bool = True):
        # 設定を読み込み
        self.display_config = config.get_display_config()
        self.eye_config = config.get_eye_config()
        self.color_config = config.get_color_config()
        
        # Pygame初期化
        pygame.init()
        
        # ディスプレイ設定
        self.setup_display()
        
        # クロック設定
        self.clock = pygame.time.Clock()
        self.fps = self.display_config['fps']
        
        # 共通のレンダリングとアニメーションシステム
        self.setup_rendering_system()
        
        # 状態機械の初期化
        self.state_machine = StateMachine()
        self.setup_states()
        
        # コマンドインターフェース
        self.command_interface = None
        self.enable_command_interface = enable_command_interface
        if enable_command_interface:
            from core.command_interface import CommandInterface
            self.command_interface = CommandInterface()
        
        # イベントリスナーの設定
        self.setup_event_listeners()
        
        # 実行フラグ
        self.running = True
        
        print("ロボット顔表示システムを初期化しました")
        print(f"解像度: {self.display_config['width']}x{self.display_config['height']}")
        print(f"FPS: {self.fps}")
        if self.command_interface:
            command_config = config.get_command_interface_config()
            print(f"コマンドインターフェース: {command_config['host']}:{command_config['port']}")
        print("\n=== 操作方法 ===")
        print("ESC: 終了")
        print("F11: フルスクリーン切り替え")
        print("1: アイドル状態")
        print("2: 思考中状態")
        print("3: 発話中状態")
        print("4: 休止状態")
        print("R: アイドル状態にリセット")
        print("SPACE: まばたき")
        print("↑/↓: 強度調整（思考中・発話中状態で）")
        print("ENTER: 発話停止/再開（発話中状態で）")
        print("================\n")
    
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
    
    def setup_rendering_system(self):
        """共通のレンダリングとアニメーションシステムを設定"""
        # 目の中心座標を計算
        screen_width = self.display_config['width']
        screen_height = self.display_config['height']
        eye_spacing = self.eye_config['spacing']
        
        self.left_eye_center = (screen_width // 2 - eye_spacing, screen_height // 2)
        self.right_eye_center = (screen_width // 2 + eye_spacing, screen_height // 2)
        
        # 共通のレンダラーとアニメーションコントローラー
        self.eye_renderer = EyeRenderer()
        self.border_renderer = BorderRenderer()
        self.animation_controller = AnimationController(
            self.eye_config['width'],
            self.eye_config['height']
        )
        
        # テクスチャの事前読み込み
        self.eye_renderer.preload_all_textures(
            self.eye_config['width'],
            self.eye_config['height']
        )
    
    def setup_states(self):
        """状態を設定"""
        # 全ての状態を追加（共通レンダリングシステムを渡す）
        idle_state = IdleState()
        thinking_state = ThinkingState(self.border_renderer)
        speaking_state = SpeakingState(self.border_renderer)
        
        from states.sleeping_state import SleepingState
        sleeping_state = SleepingState()
        
        self.state_machine.add_state(idle_state)
        self.state_machine.add_state(thinking_state)
        self.state_machine.add_state(speaking_state)
        self.state_machine.add_state(sleeping_state)
        
        # 初期状態をアイドルに設定
        self.state_machine.change_state("idle")
    
    def setup_event_listeners(self):
        """イベントリスナーを設定"""
        def on_state_changed(event):
            print(f"状態変更: {event.data['previous_state']} -> {event.data['current_state']}")
        
        def on_command_received(event):
            """外部コマンド受信時の処理"""
            command_data = event.data
            command = command_data.get('command')
            
            if command == 'change_state':
                state_name = command_data.get('state')
                parameters = command_data.get('parameters', {})
                
                # 状態変更を実行
                self.state_machine.change_state(state_name, **parameters)
                print(f"コマンドで状態変更: {state_name}")
                
            elif command == 'set_parameter':
                parameters = command_data.get('parameters', {})
                # パラメータ設定を実行（現在の状態に応じて）
                current_state = self.state_machine.get_current_state()
                if current_state and hasattr(current_state, 'set_parameters'):
                    current_state.set_parameters(parameters)
                print(f"パラメータ設定: {parameters}")
                
            elif command == 'shutdown':
                print("シャットダウンコマンドを受信しました")
                self.running = False
        
        event_system.subscribe(EventType.STATE_CHANGED, on_state_changed)
        if self.command_interface:
            event_system.subscribe(EventType.COMMAND_RECEIVED, on_command_received)
    
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
                elif event.key == pygame.K_1:
                    # アイドル状態に切り替え
                    self.state_machine.change_state("idle")
                elif event.key == pygame.K_2:
                    # 思考中状態に切り替え
                    self.state_machine.change_state("thinking", intensity=1.0)
                elif event.key == pygame.K_3:
                    # 発話中状態に切り替え
                    self.state_machine.change_state("speaking", intensity=1.0)
                elif event.key == pygame.K_4:
                    # 休止状態に切り替え
                    self.state_machine.change_state("sleeping")
                elif event.key == pygame.K_r:
                    # 現在の状態をリセットしてアイドルに戻る
                    current_state = self.state_machine.current_state_name
                    self.state_machine.change_state("idle")
                    print(f"状態をリセットしました: {current_state} -> idle")
                elif event.key == pygame.K_SPACE:
                    # 強制まばたき（全状態で共通）
                    self.animation_controller.force_blink()
            
            # 現在の状態にイベントを転送
            self.state_machine.handle_event(event)
    
    def update(self, dt: float):
        """更新処理
        
        Args:
            dt: デルタタイム（秒）
        """
        # 共通のアニメーション更新
        current_time = pygame.time.get_ticks()
        self.animation_controller.update(current_time)
        self.border_renderer.update(dt)
        
        # 状態固有の更新
        self.state_machine.update(dt)
    
    def render(self):
        """描画処理"""
        # 背景をクリア
        self.screen.fill(self.color_config['black'])
        
        # 共通の目の描画
        self.render_eyes()
        
        # 状態固有のオーバーレイ描画
        self.state_machine.render(self.screen)
        
        pygame.display.flip()
    
    def render_eyes(self):
        """共通の目の描画"""
        current_time = pygame.time.get_ticks()
        current_state_name = self.state_machine.current_state_name
        
        # 休止状態の場合は円弧を描画
        if current_state_name == "sleeping":
            # 休止状態の場合、呼吸アニメーションのオフセットを取得
            current_state = self.state_machine.get_current_state()
            breathing_offset = 0
            if current_state and hasattr(current_state, 'get_breathing_offset'):
                breathing_offset = current_state.get_breathing_offset()
            
            # 目のオフセット（休止状態では視線移動なし）
            eye_offset = pygame.math.Vector2(0, breathing_offset)
            
            # 両目を円弧で描画
            self.eye_renderer.draw_sleeping_eye(
                self.screen,
                self.left_eye_center,
                eye_offset,
                self.eye_config['width'],
                self.eye_config['height']
            )
            
            self.eye_renderer.draw_sleeping_eye(
                self.screen,
                self.right_eye_center,
                eye_offset,
                self.eye_config['width'],
                self.eye_config['height']
            )
        else:
            # 通常の楕円形の目を描画
            animation_state = self.animation_controller.get_animation_state(current_time)
            
            eye_offset = animation_state['eye_offset']
            blink_ratio = animation_state['blink_ratio']
            
            # 両目を描画
            self.eye_renderer.draw_eye(
                self.screen,
                self.left_eye_center,
                eye_offset,
                self.eye_config['width'],
                self.eye_config['height'],
                blink_ratio
            )
            
            self.eye_renderer.draw_eye(
                self.screen,
                self.right_eye_center,
                eye_offset,
                self.eye_config['width'],
                self.eye_config['height'],
                blink_ratio
            )
    
    def run(self):
        """メインループ"""
        if self.command_interface:
            # asyncioでコマンドサーバーと同時実行
            import asyncio
            asyncio.run(self._run_with_command_interface())
        else:
            # 通常のゲームループ
            self._run_game_loop()
    
    async def _run_with_command_interface(self):
        """コマンドインターフェース付きでの実行"""
        import asyncio
        
        # コマンドサーバータスクを開始
        server_task = asyncio.create_task(self.command_interface.start_server())
        
        # ゲームループタスクを開始
        game_task = asyncio.create_task(self._run_async_game_loop())
        
        try:
            # 両方のタスクを並行実行（どちらかが終了すると両方停止）
            done, pending = await asyncio.wait([server_task, game_task], return_when=asyncio.FIRST_COMPLETED)
            
            # 未完了のタスクをキャンセル
            for task in pending:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                    
        except KeyboardInterrupt:
            print("\nキーボード割り込みで終了します")
        finally:
            # サーバーを停止
            if self.command_interface:
                await self.command_interface.stop_server()
            self.cleanup()
    
    async def _run_async_game_loop(self):
        """非同期ゲームループ"""
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
            
            # 短時間の非同期待機（他のタスクに制御を譲る）
            await asyncio.sleep(0.001)
    
    def _run_game_loop(self):
        """通常のゲームループ"""
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
    
    def cleanup(self):
        """終了処理"""
        print("アプリケーションを終了します...")
        pygame.quit()
        sys.exit()

def main():
    """メイン関数"""
    import argparse
    
    # コマンドライン引数をパース
    parser = argparse.ArgumentParser(description='ロボット顔表示システム')
    parser.add_argument('--no-server', action='store_true', 
                       help='コマンドインターフェースを無効化')
    args = parser.parse_args()
    
    try:
        # コマンドインターフェースの有効/無効を設定
        enable_command_interface = not args.no_server
        app = RobotFaceApp(enable_command_interface=enable_command_interface)
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