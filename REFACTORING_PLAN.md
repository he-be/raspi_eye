# リファクタリング計画書

## 1. リファクタリング概要

現在の単一ファイル（`eye_test4.py`）を、モジュール化されたコミュニケーションロボット顔表示システムにリファクタリングする。

## 2. 段階的リファクタリング戦略

### Phase 1: 基盤の構築
**目標**: 最小限の機能でアーキテクチャを確立

#### Step 1.1: プロジェクト構造の構築
- [ ] ディレクトリ構造の作成
- [ ] `__init__.py` ファイルの配置
- [ ] 基本設定ファイル（`config.yaml`）の作成
- [ ] `requirements.txt` の作成

#### Step 1.2: 定数とユーティリティの分離
- [ ] `utils/constants.py` に定数を移動
- [ ] `utils/config.py` で設定管理機能を実装
- [ ] 既存の定数を新しいモジュールから参照

#### Step 1.3: ベースクラスの実装
- [ ] `states/base_state.py` で抽象基底クラスを作成
- [ ] `core/state_machine.py` で状態管理機能を実装
- [ ] 基本的なイベントシステム（`utils/events.py`）を実装

### Phase 2: 既存機能の移植
**目標**: 現在のアイドル状態機能を新しいアーキテクチャに移植

#### Step 2.1: 描画機能の分離
- [ ] `renderers/eye_renderer.py` に目の描画機能を移動
  - `create_radial_gradient_surface()`
  - `generate_glow_layers()`
  - `create_glow_texture()`
  - `get_or_create_glow_texture()`
  - `draw_smooth_glow_ellipse()`
  - `draw_eye()`
- [ ] キャッシュ機能も同時に移動
- [ ] テクスチャ生成関数群を整理

#### Step 2.2: アニメーション機能の分離
- [ ] `animation/controller.py` にアニメーション管理機能を移動
  - まばたき制御（`update_blink()`, `get_blink_ratio()`）
  - 視線移動制御（`get_new_target()`）
- [ ] `animation/easing.py` にイージング関数を実装

#### Step 2.3: アイドル状態の実装
- [ ] `states/idle_state.py` を実装
  - 既存のまばたき＋視線移動ロジックを移植
  - BaseStateインターフェースに準拠
- [ ] 動作テストを実施

### Phase 3: 新機能の実装
**目標**: 思考中・発話中状態を実装

#### Step 3.1: 外枠描画機能の実装
- [ ] `renderers/border_renderer.py` を実装
  - 矩形外枠の描画
  - カラーアニメーション
  - 点滅効果

#### Step 3.2: 思考中状態の実装
- [ ] `states/thinking_state.py` を実装
  - ランダムカラーアニメーション
  - パルス効果
  - グラデーション変化

#### Step 3.3: 発話中状態の実装
- [ ] `states/speaking_state.py` を実装
  - 白色点滅効果
  - 強度調整機能
  - 疑似リップシンク

### Phase 4: 外部インターフェースの実装
**目標**: 外部からのコマンド受付機能を実装

#### Step 4.1: コマンドインターフェースの実装
- [ ] `core/command_interface.py` を実装
  - TCP/IPソケットサーバー
  - 非同期処理
  - JSONパース機能

#### Step 4.2: コマンド処理の実装
- [ ] コマンドバリデーション
- [ ] 状態遷移制御
- [ ] エラーハンドリング

#### Step 4.3: メインアプリケーションの実装
- [ ] `main.py` で全体の統合
- [ ] 初期化シーケンス
- [ ] メインループの実装

### Phase 5: テストと最適化
**目標**: 品質向上と性能最適化

#### Step 5.1: テストの実装
- [ ] 単体テストの作成
- [ ] 統合テストの実装
- [ ] 動作確認用スクリプト

#### Step 5.2: パフォーマンス最適化
- [ ] プロファイリング実施
- [ ] ボトルネックの特定と修正
- [ ] メモリ使用量の最適化

#### Step 5.3: ドキュメント整備
- [ ] API仕様書の作成
- [ ] 使用方法ドキュメント
- [ ] トラブルシューティングガイド

## 3. コード移行マップ

### 3.1 既存関数の移行先

| 既存関数 | 移行先 | 備考 |
|---------|--------|------|
| `ensure_cache_dir()` | `renderers/eye_renderer.py` | キャッシュ管理 |
| `get_cache_filename()` | `renderers/eye_renderer.py` | キャッシュ管理 |
| `load_cached_texture()` | `renderers/eye_renderer.py` | キャッシュ管理 |
| `save_texture_cache()` | `renderers/eye_renderer.py` | キャッシュ管理 |
| `create_radial_gradient_surface()` | `renderers/eye_renderer.py` | グラフィックス |
| `generate_glow_layers()` | `renderers/eye_renderer.py` | グラフィックス |
| `create_glow_texture()` | `renderers/eye_renderer.py` | グラフィックス |
| `get_or_create_glow_texture()` | `renderers/eye_renderer.py` | グラフィックス |
| `draw_smooth_glow_ellipse()` | `renderers/eye_renderer.py` | 描画 |
| `draw_eye()` | `renderers/eye_renderer.py` | 描画 |
| `get_new_target()` | `animation/controller.py` | アニメーション |
| `update_blink()` | `animation/controller.py` | アニメーション |
| `get_blink_ratio()` | `animation/controller.py` | アニメーション |

### 3.2 定数の移行先

| 既存定数 | 移行先 | 備考 |
|---------|--------|------|
| 画面関連定数 | `utils/constants.py` | `SCREEN_WIDTH`, `SCREEN_HEIGHT`, `FPS` |
| 色定数 | `utils/constants.py` | `BLACK`, `WHITE`, `CYAN_GLOW` |
| 目の設定 | `utils/constants.py` | `EYE_WIDTH`, `EYE_HEIGHT` など |
| アニメーション設定 | `utils/constants.py` | `LOOK_INTERVAL_*`, `BLINK_*` |

### 3.3 グローバル変数の処理

| 既存変数 | 処理方法 | 備考 |
|---------|----------|------|
| `eye_offset`, `target_offset` | `IdleState`のインスタンス変数 | 状態内部で管理 |
| `last_look_time`, `next_look_interval` | `IdleState`のインスタンス変数 | 状態内部で管理 |
| `blink_*` 変数 | `IdleState`のインスタンス変数 | 状態内部で管理 |
| `glow_cache` | `EyeRenderer`のクラス変数 | レンダラーで管理 |

## 4. リスク管理

### 4.1 技術的リスク

| リスク | 影響度 | 対策 |
|-------|--------|------|
| パフォーマンス劣化 | 高 | 段階的移行、プロファイリング |
| 既存機能の動作不具合 | 高 | 十分なテスト、比較検証 |
| メモリリーク | 中 | リソース管理の徹底 |
| 状態遷移の複雑化 | 中 | シンプルな状態設計 |

### 4.2 スケジュールリスク

| リスク | 対策 |
|-------|------|
| 想定以上の工数 | MVP（最小実行可能製品）を先に完成 |
| 技術的課題の発生 | プロトタイプでの事前検証 |
| テスト工数の増大 | 自動テストの活用 |

## 5. 成功指標

### 5.1 機能指標
- [ ] 既存のアイドル状態機能が完全に動作
- [ ] 思考中・発話中状態が仕様通りに動作
- [ ] 外部コマンドでの状態遷移が正常動作
- [ ] 60 FPSでの安定動作

### 5.2 品質指標
- [ ] テストカバレッジ80%以上
- [ ] メモリ使用量が既存実装の120%以下
- [ ] CPU使用率が既存実装と同等以下
- [ ] コードの可読性・保守性の向上

### 5.3 拡張性指標
- [ ] 新しい状態を1時間以内で追加可能
- [ ] 新しいアニメーション効果を30分以内で追加可能
- [ ] 設定変更が再起動なしで反映

## 6. 移行スケジュール

| フェーズ | 期間 | 主要成果物 |
|---------|------|-----------|
| Phase 1 | 2日 | 基盤構築完了 |
| Phase 2 | 3日 | アイドル状態移植完了 |
| Phase 3 | 3日 | 新状態実装完了 |
| Phase 4 | 2日 | 外部インターフェース完了 |
| Phase 5 | 2日 | テスト・最適化完了 |
| **総計** | **12日** | **完全なシステム** |

## 7. 後方互換性

### 7.1 一時的な並行実行
- リファクタリング期間中は `eye_test4.py` を残存
- 新システム完成後に `eye_test4_legacy.py` にリネーム
- 動作比較・検証用として活用

### 7.2 設定ファイルの移行
- 既存の定数をYAML設定ファイルに移行
- デフォルト値は既存と同一に設定
- 設定変更による動作調整を可能に