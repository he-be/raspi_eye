# コミュニケーションロボット顔表示システム (raspi_eye)

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Pygame](https://img.shields.io/badge/pygame-2.0%2B-green)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

## 概要

コミュニケーションロボットの顔（目）を表示するシステムです。外部からのコマンドに応じて、ロボットの感情や状態を視覚的に表現します。Raspberry Pi 4での動作を想定し、60FPSでリアルタイム描画を行います。

## 特徴

- **4つの状態管理**
  - **アイドル状態**: まばたきとランダムな視線移動
  - **思考中状態**: 最外周にカラフルなアニメーション外枠
  - **発話中状態**: 最外周に白い点滅外枠（疑似リップシンク）
  - **休止状態**: 漫画風の寝ている目（1/4円弧）と呼吸アニメーション

- **外部コマンドインターフェース**
  - TCP/IPソケット通信
  - JSONフォーマットでのコマンド送受信
  - 非同期処理対応

- **高性能描画**
  - 60FPS安定動作
  - テクスチャキャッシング
  - 最適化されたレンダリング

## 動作環境

- Python 3.8以上
- Pygame 2.0以上
- 解像度: 720x480
- 推奨: Raspberry Pi 4

## インストール

```bash
# リポジトリのクローン
git clone https://github.com/yourusername/raspi_eye.git
cd raspi_eye

# 仮想環境の作成（推奨）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 依存関係のインストール
pip install -r requirements.txt
```

## 使用方法

### 基本的な起動

```bash
# 通常起動（コマンドインターフェース有効）
python main.py

# コマンドインターフェースなしで起動
python main.py --no-server
```

### キーボード操作

- `ESC`: 終了
- `F11`: フルスクリーン切り替え
- `1`: アイドル状態
- `2`: 思考中状態
- `3`: 発話中状態
- `4`: 休止状態
- `R`: アイドル状態にリセット
- `SPACE`: まばたき
- `↑/↓`: 強度調整（思考中・発話中状態で）
- `ENTER`: 発話停止/再開（発話中状態で）

### 外部コマンド制御

テストクライアントを使用した例：

```bash
# 別ターミナルでテストクライアントを起動
python test_client.py

# 自動デモモード
python test_client.py demo
```

### コマンドフォーマット

```json
{
  "command": "change_state",
  "state": "thinking",
  "parameters": {
    "intensity": 1.2
  }
}
```

利用可能なコマンド:
- `change_state`: 状態変更
- `set_parameter`: パラメータ設定
- `get_status`: ステータス取得
- `ping`: 接続確認
- `shutdown`: シャットダウン

## プロジェクト構成

```
raspi_eye/
├── main.py                # メインアプリケーション
├── config.yaml           # 設定ファイル
├── requirements.txt      # Python依存関係
├── test_client.py        # テストクライアント
│
├── core/                 # コアコンポーネント
│   ├── state_machine.py  # 状態管理
│   └── command_interface.py # コマンドインターフェース
│
├── states/               # 状態実装
│   ├── base_state.py     # 基底クラス
│   ├── idle_state.py     # アイドル状態
│   ├── thinking_state.py # 思考中状態
│   └── speaking_state.py # 発話中状態
│
├── renderers/            # 描画コンポーネント
│   ├── eye_renderer.py   # 目の描画
│   └── border_renderer.py # 外枠描画
│
├── animation/            # アニメーション
│   ├── controller.py     # アニメーション制御
│   └── easing.py        # イージング関数
│
└── utils/                # ユーティリティ
    ├── config.py        # 設定管理
    ├── events.py        # イベントシステム
    └── constants.py     # 定数定義
```

## 設定

`config.yaml`で各種パラメータを調整できます：

```yaml
# 画面設定
display:
  width: 720
  height: 480
  fps: 60
  fullscreen: true

# コマンドインターフェース設定
command_interface:
  host: "localhost"
  port: 8888
```

## 開発

### アーキテクチャ

- **State Machine Pattern**: 状態管理
- **Observer Pattern**: イベントシステム
- **Strategy Pattern**: 描画アルゴリズム

### 拡張方法

新しい状態を追加する場合：

1. `states/`ディレクトリに新しい状態クラスを作成
2. `BaseState`を継承
3. `main.py`の`setup_states()`に登録

## トラブルシューティング

### フルスクリーンモードで起動できない
```bash
# ウィンドウモードで起動
python main.py
# F11キーでフルスクリーン切り替え
```

### コマンドインターフェースに接続できない
```bash
# ポートを確認
netstat -an | grep 8888

# ファイアウォール設定を確認
```

## ライセンス

MIT License

## 貢献

プルリクエストを歓迎します。大きな変更の場合は、まずissueを作成して変更内容を議論してください。

## 作者

[Your Name]

## 謝辞

このプロジェクトは、コミュニケーションロボットの研究開発の一環として作成されました。