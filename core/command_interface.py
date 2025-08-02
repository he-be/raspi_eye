import asyncio
import json
import logging
from typing import Dict, Any, Callable, Optional
from utils.config import config
from utils.events import event_system, EventType

class CommandInterface:
    """外部コマンドを受信するTCP/IPインターフェース"""
    
    def __init__(self):
        self.command_config = config.get_command_interface_config()
        self.host = self.command_config.get('host', 'localhost')
        self.port = self.command_config.get('port', 8888)
        self.buffer_size = self.command_config.get('buffer_size', 1024)
        
        # サーバー管理
        self.server = None
        self.is_running = False
        self.clients = set()
        
        # コマンドハンドラー
        self.command_handlers: Dict[str, Callable] = {}
        self.setup_default_handlers()
        
        # ログ設定
        self.logger = logging.getLogger(__name__)
        
    def setup_default_handlers(self):
        """デフォルトのコマンドハンドラーを設定"""
        self.command_handlers = {
            'change_state': self._handle_change_state,
            'set_parameter': self._handle_set_parameter,
            'get_status': self._handle_get_status,
            'shutdown': self._handle_shutdown,
            'ping': self._handle_ping
        }
    
    async def start_server(self):
        """コマンドサーバーを開始"""
        try:
            self.server = await asyncio.start_server(
                self._handle_client,
                self.host,
                self.port
            )
            self.is_running = True
            
            addr = self.server.sockets[0].getsockname()
            self.logger.info(f"コマンドサーバーを開始しました: {addr[0]}:{addr[1]}")
            print(f"コマンドサーバーを開始しました: {addr[0]}:{addr[1]}")
            
            async with self.server:
                await self.server.serve_forever()
                
        except Exception as e:
            self.logger.error(f"サーバー開始エラー: {e}")
            print(f"サーバー開始エラー: {e}")
            self.is_running = False
    
    async def stop_server(self):
        """コマンドサーバーを停止"""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            self.is_running = False
            self.logger.info("コマンドサーバーを停止しました")
            print("コマンドサーバーを停止しました")
    
    async def _handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """クライアント接続を処理"""
        client_addr = writer.get_extra_info('peername')
        self.logger.info(f"クライアント接続: {client_addr}")
        print(f"クライアント接続: {client_addr}")
        
        self.clients.add(writer)
        
        try:
            while True:
                # データ受信
                data = await reader.read(self.buffer_size)
                if not data:
                    break
                
                try:
                    # JSONデコード
                    message = data.decode('utf-8').strip()
                    if not message:
                        continue
                        
                    command_data = json.loads(message)
                    self.logger.debug(f"受信コマンド: {command_data}")
                    
                    # コマンド処理
                    response = await self._process_command(command_data)
                    
                    # レスポンス送信
                    if response:
                        response_json = json.dumps(response, ensure_ascii=False)
                        writer.write(f"{response_json}\n".encode('utf-8'))
                        await writer.drain()
                        
                except json.JSONDecodeError as e:
                    error_response = {
                        'error': 'invalid_json',
                        'message': f'JSONフォーマットエラー: {str(e)}'
                    }
                    writer.write(f"{json.dumps(error_response)}\n".encode('utf-8'))
                    await writer.drain()
                    
                except Exception as e:
                    self.logger.error(f"コマンド処理エラー: {e}")
                    error_response = {
                        'error': 'processing_error',
                        'message': f'処理エラー: {str(e)}'
                    }
                    writer.write(f"{json.dumps(error_response)}\n".encode('utf-8'))
                    await writer.drain()
                    
        except asyncio.CancelledError:
            pass
        except Exception as e:
            self.logger.error(f"クライアント処理エラー: {e}")
        finally:
            self.clients.discard(writer)
            writer.close()
            await writer.wait_closed()
            self.logger.info(f"クライアント切断: {client_addr}")
            print(f"クライアント切断: {client_addr}")
    
    async def _process_command(self, command_data: Dict[str, Any]) -> Dict[str, Any]:
        """コマンドを処理"""
        # コマンド検証
        if 'command' not in command_data:
            return {
                'error': 'missing_command',
                'message': 'コマンドが指定されていません'
            }
        
        command_name = command_data['command']
        
        # ハンドラー検索
        if command_name not in self.command_handlers:
            return {
                'error': 'unknown_command',
                'message': f'未知のコマンド: {command_name}'
            }
        
        # ハンドラー実行
        try:
            handler = self.command_handlers[command_name]
            result = await handler(command_data)
            return result
        except Exception as e:
            return {
                'error': 'handler_error',
                'message': f'ハンドラーエラー: {str(e)}'
            }
    
    async def _handle_change_state(self, command_data: Dict[str, Any]) -> Dict[str, Any]:
        """状態変更コマンドを処理"""
        if 'state' not in command_data:
            return {
                'error': 'missing_state',
                'message': '状態が指定されていません'
            }
        
        state_name = command_data['state']
        parameters = command_data.get('parameters', {})
        
        # 状態変更イベントを発行
        event_system.emit(EventType.COMMAND_RECEIVED, {
            'command': 'change_state',
            'state': state_name,
            'parameters': parameters
        })
        
        return {
            'success': True,
            'message': f'状態を{state_name}に変更しました',
            'state': state_name,
            'parameters': parameters
        }
    
    async def _handle_set_parameter(self, command_data: Dict[str, Any]) -> Dict[str, Any]:
        """パラメータ設定コマンドを処理"""
        if 'parameters' not in command_data:
            return {
                'error': 'missing_parameters',
                'message': 'パラメータが指定されていません'
            }
        
        parameters = command_data['parameters']
        
        # パラメータ設定イベントを発行
        event_system.emit(EventType.COMMAND_RECEIVED, {
            'command': 'set_parameter',
            'parameters': parameters
        })
        
        return {
            'success': True,
            'message': 'パラメータを設定しました',
            'parameters': parameters
        }
    
    async def _handle_get_status(self, command_data: Dict[str, Any]) -> Dict[str, Any]:
        """ステータス取得コマンドを処理"""
        # ステータス取得イベントを発行
        event_system.emit(EventType.COMMAND_RECEIVED, {
            'command': 'get_status'
        })
        
        # TODO: 実際のステータス情報を取得する仕組みを後で実装
        return {
            'success': True,
            'status': {
                'server_running': self.is_running,
                'clients_connected': len(self.clients),
                'server_address': f"{self.host}:{self.port}"
            }
        }
    
    async def _handle_shutdown(self, command_data: Dict[str, Any]) -> Dict[str, Any]:
        """シャットダウンコマンドを処理"""
        # シャットダウンイベントを発行
        event_system.emit(EventType.COMMAND_RECEIVED, {
            'command': 'shutdown'
        })
        
        return {
            'success': True,
            'message': 'シャットダウンを開始します'
        }
    
    async def _handle_ping(self, command_data: Dict[str, Any]) -> Dict[str, Any]:
        """Pingコマンドを処理"""
        return {
            'success': True,
            'message': 'pong',
            'timestamp': asyncio.get_event_loop().time()
        }
    
    def add_command_handler(self, command_name: str, handler: Callable):
        """カスタムコマンドハンドラーを追加"""
        self.command_handlers[command_name] = handler
        self.logger.info(f"コマンドハンドラーを追加: {command_name}")
    
    def remove_command_handler(self, command_name: str):
        """コマンドハンドラーを削除"""
        if command_name in self.command_handlers:
            del self.command_handlers[command_name]
            self.logger.info(f"コマンドハンドラーを削除: {command_name}")
    
    async def broadcast_message(self, message: Dict[str, Any]):
        """全クライアントにメッセージをブロードキャスト"""
        if not self.clients:
            return
        
        message_json = json.dumps(message, ensure_ascii=False)
        
        # 無効なクライアントを除去するためのセット
        clients_to_remove = set()
        
        for writer in self.clients:
            try:
                writer.write(f"{message_json}\n".encode('utf-8'))
                await writer.drain()
            except Exception as e:
                self.logger.warning(f"ブロードキャスト送信エラー: {e}")
                clients_to_remove.add(writer)
        
        # 無効なクライアントを除去
        self.clients -= clients_to_remove