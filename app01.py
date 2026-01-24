import streamlit as st
import os
from pathlib import Path
import streamlit.components.v1 as components


# ページ設定
st.set_page_config(
    page_title="3D Model Viewer",
    layout="wide"
)

st.title("3D Model Viewer with Three.js")
st.markdown("**Streamlit + Three.js を使用した .glb ファイルビューア**")

# .glb ファイルを検索
def find_glb_files(base_path="./models"):
    """指定されたディレクトリから.glbファイルを検索"""
    glb_files = []
    if os.path.exists(base_path):
        for root, dirs, files in os.walk(base_path):
            for file in files:
                if file.endswith('.glb'):
                    file_path = os.path.join(root, file)
                    glb_files.append(file_path)
    return glb_files

# サイドバーでファイル選択
st.sidebar.header("モデル選択")

# .glbファイルのリストを取得
models_dir = "./models"
glb_files = find_glb_files(models_dir)

if not glb_files:
    st.sidebar.warning(f"'{models_dir}' ディレクトリに .glb ファイルが見つかりません")
    st.info("""
    ### 使い方
    1. プロジェクトルートに `models` ディレクトリを作成
    2. .glb ファイルを `models` ディレクトリに配置
    3. このアプリをリロード
    """)
    
    # デモ用のサンプルパス表示
    st.sidebar.info("サンプル: ./models/sample.glb")
    selected_file = None
else:
    # ファイル名のみ表示用リストを作成
    file_names = [os.path.basename(f) for f in glb_files]
    
    # ファイル選択
    selected_index = st.sidebar.selectbox(
        "モデルを選択",
        range(len(file_names)),
        format_func=lambda i: file_names[i]
    )
    
    selected_file = glb_files[selected_index]
    
    # 選択されたファイルのパス表示
    st.sidebar.success(f"選択中: {selected_file}")
    
    # ファイル情報表示
    file_size = os.path.getsize(selected_file)
    st.sidebar.metric("ファイルサイズ", f"{file_size / 1024:.2f} KB")

# ビューア設定
st.sidebar.header("ビューア設定")
width = st.sidebar.slider("幅 (px)", 400, 1200, 800)
height = st.sidebar.slider("高さ (px)", 300, 900, 600)
bg_color = st.sidebar.color_picker("背景色", "#C4C3C3")
show_grid = st.sidebar.checkbox("グリッド表示", True)
auto_rotate = st.sidebar.checkbox("自動回転", False)

# ボタン
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🔄 リセットビュー"):
        st.rerun()
with col2:
    if st.button("📷 スクリーンショット", help="右クリックで画像を保存できます"):
        st.info("ビューア上で右クリック → 画像を保存")
with col3:
    if st.button("🔍 リロード"):
        st.rerun()

# Three.jsビューアの埋め込み
if selected_file:
    # ファイルパスをBase64エンコードして埋め込むか、直接パスを使用
    # ここではシンプルにファイルを読み込んでBase64エンコード
    import base64
    
    with open(selected_file, 'rb') as f:
        glb_data = f.read()
        glb_base64 = base64.b64encode(glb_data).decode()

    # Three.js + GLTFLoader を使用した3Dビューア
    template = Path("three_html/viewer01.html").read_text(encoding="utf-8")
    threejs_html = template.format(
        bg_color=bg_color,
        width=width,
        height=height,
        auto_rotate=str(auto_rotate).lower(),
        show_grid=str(show_grid).lower(),
        glb_base64=glb_base64,
    )
    
    # Streamlitにビューアを埋め込み
    st.subheader("3D ビューア")
    components.html(threejs_html, height=height + 20, scrolling=False)
    
    st.markdown("""
    ### 操作方法
    - **左クリック + ドラッグ**: モデルを回転
    - **右クリック + ドラッグ**: カメラ移動
    - **マウスホイール**: ズームイン/アウト
    """)
else:
    st.warning("モデルファイルを選択してください")

# フッター
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <small>Powered by Streamlit + Three.js | GPU加速レンダリング対応</small>
</div>
""", unsafe_allow_html=True)
