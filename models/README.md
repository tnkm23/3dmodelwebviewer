# Models Directory

このディレクトリに .glb ファイルを配置してください。

## .glb ファイルの入手方法

無料の .glb ファイルは以下のサイトから入手できます:

- [Sketchfab](https://sketchfab.com/features/gltf) - Free 3D models
- [Poly Haven](https://polyhaven.com/) - CC0 3D assets
- [glTF Sample Models](https://github.com/KhronosGroup/glTF-Sample-Models) - Official glTF samples

## 使い方

1. .glb ファイルをこのディレクトリに配置
2. Streamlit アプリ (app.py) を起動
3. サイドバーでモデルを選択

## サンプルコマンド

```bash
# サンプルモデルをダウンロード（例）
wget https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Models/master/2.0/Box/glTF-Binary/Box.glb -O models/Box.glb
```

## 注意事項

- .glb ファイル形式のみ対応
- ファイルサイズが大きいと読み込みに時間がかかる場合があります
- このディレクトリはGit追跡されません（.gitignore に含まれています）
