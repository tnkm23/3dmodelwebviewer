# 3D Model Viewer

Streamlit + Three.js を使用した GPU 加速 3D モデルビューア

## 概要

このプロジェクトは、Streamlit (Python) と Three.js (JavaScript) を組み合わせて、ブラウザ上で .glb ファイルを表示する 3D モデルビューアです。

### 主な機能

- **サーバー上の .glb ファイル自動検出**: `models/` ディレクトリ内の .glb ファイルを自動的に検出
- **インタラクティブ UI**: Streamlit によるファイル選択、ビューア設定、各種ボタン
- **GPU 加速レンダリング**: Three.js を使用し、ブラウザの GPU (Iris Xe 等) をフル活用
- **高度な 3D 機能**: 
  - OrbitControls による直感的な操作
  - 自動回転、グリッド表示などのオプション
  - シャドウ、ライティング
  - 自動カメラ位置調整

## アーキテクチャ

```
┌─────────────────────────────────────────┐
│  Streamlit (Python)                     │
│  - .glb ファイルパス取得                │
│  - UI (ボタン、スライダー等) 表示      │
│  - ファイル読み込み & Base64 エンコード │
└──────────────┬──────────────────────────┘
               │
               │ components.html()
               ↓
┌─────────────────────────────────────────┐
│  Three.js (JavaScript)                  │
│  - GLTFLoader で .glb 読み込み          │
│  - WebGLRenderer (GPU 活用)             │
│  - OrbitControls                        │
│  - リアルタイムレンダリング             │
└─────────────────────────────────────────┘
```

## セットアップ

### 必要要件

- Python 3.8 以上
- pip

### インストール

1. リポジトリをクローン:

```bash
git clone https://github.com/tnkm23/3dmodelwebviewer.git
cd 3dmodelwebviewer
```

2. 依存関係をインストール:

```bash
pip install -r requirements.txt
```

3. `models/` ディレクトリに .glb ファイルを配置:

```bash
mkdir -p models
# .glb ファイルを models/ ディレクトリにコピー
cp /path/to/your/model.glb models/
```

### .glb ファイルのサンプル入手方法

無料の .glb ファイルは以下のサイトから入手できます:

- [Sketchfab](https://sketchfab.com/features/gltf) - Free 3D models
- [Poly Haven](https://polyhaven.com/) - CC0 3D assets
- [glTF Sample Models](https://github.com/KhronosGroup/glTF-Sample-Models) - Official glTF samples

## 使い方

### アプリケーションの起動

```bash
streamlit run app.py
```

ブラウザが自動的に開き、アプリケーションが表示されます（通常 http://localhost:8501）。

### 操作方法

#### サイドバー
- **モデル選択**: ドロップダウンから表示したい .glb ファイルを選択
- **ビューア設定**: 
  - 幅・高さの調整
  - 背景色の変更
  - グリッド表示の ON/OFF
  - 自動回転の ON/OFF

#### メインエリア
- **🔄 リセットビュー**: ビューアを初期状態にリセット
- **📷 スクリーンショット**: ビューア上で右クリックして画像を保存
- **🔍 リロード**: アプリケーションをリロード

#### 3D ビューアの操作
- **左クリック + ドラッグ**: モデルを回転
- **右クリック + ドラッグ**: カメラを平行移動
- **マウスホイール**: ズームイン/ズームアウト

## 技術仕様

### Python 側 (Streamlit)
- ファイルシステムから .glb ファイルを検索
- ファイルを読み込み Base64 エンコード
- `streamlit.components.v1.html()` で Three.js コードを埋め込み

### JavaScript 側 (Three.js)
- **Three.js 0.160.0** をCDNから読み込み
- **GLTFLoader**: .glb ファイルのロード
- **WebGLRenderer**: GPU 加速レンダリング
  - `powerPreference: 'high-performance'` で GPU 優先
  - アンチエイリアシング有効
  - シャドウマッピング
- **OrbitControls**: カメラ操作
- **自動カメラ調整**: モデルのバウンディングボックスから最適な視点を計算

## プロジェクト構造

```
3dmodelwebviewer/
├── app.py              # メインの Streamlit アプリケーション
├── requirements.txt    # Python 依存関係
├── models/             # .glb ファイルを配置するディレクトリ
├── .gitignore         # Git 除外設定
└── README.md          # このファイル
```

## カスタマイズ

### モデルディレクトリの変更

`app.py` の 17 行目を編集:

```python
models_dir = "./your_custom_directory"
```

### レンダリング設定の変更

`app.py` 内の Three.js 部分で以下を調整可能:

- **カメラ視野角**: `const camera = new THREE.PerspectiveCamera(45, ...)` の第1引数
- **ライトの強度・位置**: `ambientLight`, `directionalLight`, `pointLight` の設定
- **トーンマッピング**: `renderer.toneMapping` と `toneMappingExposure`

## トラブルシューティング

### モデルが表示されない

1. ブラウザのコンソール (F12) でエラーを確認
2. .glb ファイルが正しい形式か確認
3. ファイルサイズが大きすぎる場合、読み込みに時間がかかる可能性があります

### パフォーマンスが悪い

- ファイルサイズを小さくする（最適化ツールを使用）
- ブラウザのハードウェアアクセラレーションを有効化
- グリッド表示やシャドウを無効化

## ライセンス

このプロジェクトは自由に使用できます。

## 貢献

プルリクエストを歓迎します！

## 参考リンク

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Three.js Documentation](https://threejs.org/docs/)
- [glTF Format Specification](https://www.khronos.org/gltf/)
