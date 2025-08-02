# システムアーキテクチャ設計書

## 1. システム概要

本システムは、ステートマシンベースのアーキテクチャを採用し、外部コマンドに応じてロボットの顔の表示状態を動的に変更する。

## 2. アーキテクチャ概要

```
┌─────────────────────────────────────────────────────────┐
│                    External Systems                      │
└────────────────────┬───────────────────┬─────────────────┘
                     │ JSON Commands     │
                     ▼                   ▼
┌─────────────────────────────────────────────────────────┐
│              Command Interface (TCP/IP)                  │
│                  (Async Socket Server)                   │
└────────────────────┬───────────────────┬─────────────────┘
                     │                   │
                     ▼                   ▼
┌─────────────────────────────────────────────────────────┐
│                  Command Processor                       │
│              (Validation & Routing)                      │
└────────────────────┬───────────────────┬─────────────────┘
                     │                   │
                     ▼                   ▼
┌─────────────────────────────────────────────────────────┐
│                   State Machine                          │
│         ┌──────────┬──────────┬──────────┐             │
│         │   Idle   │ Thinking │ Speaking │             │
│         │  State   │  State   │  State   │             │
│         └──────────┴──────────┴──────────┘             │
└────────────────────┬───────────────────┬─────────────────┘
                     │                   │
                     ▼                   ▼
┌─────────────────────────────────────────────────────────┐
│                 Rendering Engine                         │
│  ┌────────────┬────────────┬────────────┬────────────┐ │
│  │ Eye Drawer │ Glow Effect│ Border     │ Animation  │ │
│  │            │ Manager    │ Renderer   │ Controller │ │
│  └────────────┴────────────┴────────────┴────────────┘ │
└─────────────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  Pygame Display                          │
│                  (720x480 @ 60FPS)                      │
└─────────────────────────────────────────────────────────┘
```

## 3. コンポーネント設計

### 3.1 Core Components

#### 3.1.1 Main Application (`main.py`)
- アプリケーションのエントリーポイント
- 各コンポーネントの初期化と起動
- メインループの管理

#### 3.1.2 State Machine (`state_machine.py`)
- 状態遷移の管理
- 現在の状態の保持
- 状態変更の検証

#### 3.1.3 Command Interface (`command_interface.py`)
- TCP/IPソケットサーバー
- 非同期コマンド受信
- JSONパース＆バリデーション

### 3.2 State Implementations

#### 3.2.1 Base State (`states/base_state.py`)
```python
class BaseState(ABC):
    @abstractmethod
    def enter(self):
        """状態開始時の処理"""
        
    @abstractmethod
    def update(self, dt):
        """状態の更新処理"""
        
    @abstractmethod
    def render(self, screen):
        """描画処理"""
        
    @abstractmethod
    def exit(self):
        """状態終了時の処理"""
```

#### 3.2.2 Idle State (`states/idle_state.py`)
- まばたきロジック
- 視線移動ロジック
- 既存の実装を活用

#### 3.2.3 Thinking State (`states/thinking_state.py`)
- 外枠のカラーアニメーション
- パルスエフェクト
- グラデーション処理

#### 3.2.4 Speaking State (`states/speaking_state.py`)
- 外枠の点滅制御
- 音声同期（将来実装）
- 強度調整

### 3.3 Rendering Components

#### 3.3.1 Eye Renderer (`renderers/eye_renderer.py`)
- 目の描画
- グローエフェクト
- キャッシュ管理

#### 3.3.2 Border Renderer (`renderers/border_renderer.py`)
- 外枠の描画
- カラーアニメーション
- 点滅効果

#### 3.3.3 Animation Controller (`animation/controller.py`)
- アニメーションのタイミング管理
- イージング関数
- 補間処理

### 3.4 Utility Components

#### 3.4.1 Config Manager (`utils/config.py`)
- 設定ファイルの読み込み
- パラメータ管理
- 実行時設定変更

#### 3.4.2 Event System (`utils/events.py`)
- イベントの発行・購読
- 状態変更通知
- コンポーネント間通信

## 4. ディレクトリ構造

```
raspi_eye/
├── main.py                 # エントリーポイント
├── requirements.txt        # 依存関係
├── config.yaml            # 設定ファイル
├── REQUIREMENTS.md        # 要件定義書
├── ARCHITECTURE.md        # アーキテクチャ設計書
├── REFACTORING_PLAN.md    # リファクタリング計画
│
├── core/                  # コアコンポーネント
│   ├── __init__.py
│   ├── state_machine.py
│   └── command_interface.py
│
├── states/                # 状態実装
│   ├── __init__.py
│   ├── base_state.py
│   ├── idle_state.py
│   ├── thinking_state.py
│   └── speaking_state.py
│
├── renderers/             # 描画コンポーネント
│   ├── __init__.py
│   ├── eye_renderer.py
│   └── border_renderer.py
│
├── animation/             # アニメーション
│   ├── __init__.py
│   ├── controller.py
│   └── easing.py
│
├── utils/                 # ユーティリティ
│   ├── __init__.py
│   ├── config.py
│   ├── events.py
│   └── constants.py
│
└── tests/                 # テストコード
    ├── __init__.py
    ├── test_state_machine.py
    └── test_commands.py
```

## 5. データフロー

### 5.1 コマンド処理フロー
1. 外部システムからJSONコマンド受信
2. Command Interfaceでパース＆検証
3. Command Processorでルーティング
4. State Machineで状態遷移
5. 新しい状態のenter()メソッド実行

### 5.2 レンダリングフロー
1. メインループでupdate()呼び出し（60 FPS）
2. 現在の状態のupdate()メソッド実行
3. アニメーションの更新
4. render()メソッドで描画
5. Pygame displayの更新

## 6. 設計パターン

### 6.1 State Pattern
- 各状態を独立したクラスとして実装
- 状態遷移ロジックの分離
- 新規状態の追加が容易

### 6.2 Observer Pattern
- イベントシステムによる疎結合
- 状態変更の通知
- コンポーネント間の連携

### 6.3 Strategy Pattern
- 描画アルゴリズムの切り替え
- アニメーション戦略の変更
- 設定による動作変更

## 7. パフォーマンス考慮事項

### 7.1 最適化戦略
- テクスチャキャッシング（既存実装を活用）
- ダーティリージョンの追跡
- 不要な再描画の回避

### 7.2 メモリ管理
- リソースの事前読み込み
- 不要なオブジェクトの解放
- メモリプールの利用

## 8. エラーハンドリング

### 8.1 コマンドエラー
- 不正なJSONフォーマット
- 未知のコマンド
- パラメータ検証エラー

### 8.2 状態遷移エラー
- 不正な状態遷移
- タイムアウト処理
- フォールバック機構

## 9. 拡張ポイント

### 9.1 新規状態の追加
1. BaseStateを継承した新規クラス作成
2. state_machine.pyに登録
3. 必要に応じてレンダラーを追加

### 9.2 新規コマンドの追加
1. コマンドハンドラーの実装
2. JSONスキーマの定義
3. ルーティングの設定