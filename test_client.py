#!/usr/bin/env python3

import socket
import json
import time
import sys

class RobotFaceClient:
    """ロボット顔表示システムのテストクライアント"""
    
    def __init__(self, host='192.168.0.198', port=8888):
        self.host = host
        self.port = port
        self.socket = None
    
    def connect(self):
        """サーバーに接続"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            print(f"サーバーに接続しました: {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"接続エラー: {e}")
            return False
    
    def disconnect(self):
        """サーバーから切断"""
        if self.socket:
            self.socket.close()
            self.socket = None
            print("サーバーから切断しました")
    
    def send_command(self, command_data):
        """コマンドを送信"""
        if not self.socket:
            print("サーバーに接続されていません")
            return None
        
        try:
            # JSONにエンコードして送信
            message = json.dumps(command_data, ensure_ascii=False)
            self.socket.send(f"{message}\n".encode('utf-8'))
            
            # レスポンスを受信
            response = self.socket.recv(1024).decode('utf-8').strip()
            if response:
                return json.loads(response)
            return None
            
        except Exception as e:
            print(f"コマンド送信エラー: {e}")
            return None
    
    def change_state(self, state, **parameters):
        """状態変更コマンドを送信"""
        command = {
            'command': 'change_state',
            'state': state
        }
        if parameters:
            command['parameters'] = parameters
        
        response = self.send_command(command)
        if response:
            print(f"状態変更レスポンス: {response}")
        return response
    
    def set_parameter(self, **parameters):
        """パラメータ設定コマンドを送信"""
        command = {
            'command': 'set_parameter',
            'parameters': parameters
        }
        
        response = self.send_command(command)
        if response:
            print(f"パラメータ設定レスポンス: {response}")
        return response
    
    def get_status(self):
        """ステータス取得コマンドを送信"""
        command = {'command': 'get_status'}
        
        response = self.send_command(command)
        if response:
            print(f"ステータス: {response}")
        return response
    
    def ping(self):
        """Pingコマンドを送信"""
        command = {'command': 'ping'}
        
        response = self.send_command(command)
        if response:
            print(f"Ping応答: {response}")
        return response
    
    def shutdown(self):
        """シャットダウンコマンドを送信"""
        command = {'command': 'shutdown'}
        
        response = self.send_command(command)
        if response:
            print(f"シャットダウンレスポンス: {response}")
        return response

def interactive_mode():
    """対話モードでテスト"""
    client = RobotFaceClient()
    
    if not client.connect():
        return
    
    try:
        print("\n=== ロボット顔表示システム テストクライアント ===")
        print("使用可能なコマンド:")
        print("  1: アイドル状態に変更")
        print("  2: 思考中状態に変更")
        print("  3: 発話中状態に変更")
        print("  s: ステータス取得")
        print("  p: Ping送信")
        print("  q: 終了")
        print("  x: シャットダウン送信")
        print("=====================================\n")
        
        while True:
            try:
                cmd = input("コマンドを入力してください: ").strip().lower()
                
                if cmd == '1':
                    client.change_state('idle')
                elif cmd == '2':
                    client.change_state('thinking', intensity=1.0)
                elif cmd == '3':
                    client.change_state('speaking', intensity=1.0)
                elif cmd == 's':
                    client.get_status()
                elif cmd == 'p':
                    client.ping()
                elif cmd == 'q':
                    break
                elif cmd == 'x':
                    client.shutdown()
                    break
                else:
                    print("無効なコマンドです")
                    
            except KeyboardInterrupt:
                break
    
    finally:
        client.disconnect()

def automated_demo():
    """自動デモシーケンス"""
    client = RobotFaceClient()
    
    if not client.connect():
        return
    
    try:
        print("\n=== 自動デモを開始します ===")
        
        # Ping テスト
        print("1. Ping テスト")
        client.ping()
        time.sleep(1)
        
        # ステータス取得
        print("2. ステータス取得")
        client.get_status()
        time.sleep(1)
        
        # 状態変更デモ
        states = [
            ('idle', {}),
            ('thinking', {'intensity': 1.2}),
            ('speaking', {'intensity': 0.8}),
            ('idle', {})
        ]
        
        for i, (state, params) in enumerate(states, 3):
            print(f"{i}. {state}状態に変更")
            client.change_state(state, **params)
            time.sleep(3)  # 3秒待機
        
        print("デモ完了")
        
    finally:
        client.disconnect()

def main():
    """メイン関数"""
    if len(sys.argv) > 1 and sys.argv[1] == 'demo':
        automated_demo()
    else:
        interactive_mode()

if __name__ == '__main__':
    main()