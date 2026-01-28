"""
3Dビューアのモジュール化使用例
メインのStreamlitアプリケーションで3Dビューアコンポーネントを使用する方法
"""

import streamlit as st
from pathlib import Path
import pandas as pd

# カスタム3Dビューアコンポーネントをインポート
from viewer_components import (
    render_viewer_sidebar,
    render_viewer_controls, 
    render_model_selector,
    render_threejs_viewer,
    render_viewer_guide,
    render_complete_3d_viewer,
    load_glb_model
)

# モデル識別子解決関数（既存のものを使用）
from app06_TestDataExtractWith3dModel import pick_model_identifier, resolve_glb_path

st.set_page_config(
    page_title="モジュール化3Dビューア例",
    page_icon="🎯",
    layout="wide"
)

st.title("🎯 モジュール化された3Dビューア例")

# =======================
# 使用パターン1: 完全統合版
# =======================
st.header("パターン1: 完全統合版ビューア")
st.write("すべての機能が統合されたビューアコンポーネント")

# サンプル試験データ（実際のDBデータの代わり）
sample_data = pd.DataFrame({
    'id': [1, 2, 3],
    'FanName': ['TestFan-1', 'TestFan-2', 'TestFan-3'],
    'TestDate': ['2026-01-01', '2026-01-02', '2026-01-03']
})

test_options = [f"ID: {row['id']} - {row['FanName']} ({row['TestDate']})" 
                for _, row in sample_data.iterrows()]

# 統合版ビューア使用
success = render_complete_3d_viewer(
    df=sample_data,
    test_options=test_options,
    models_dir="models",
    key_suffix="integrated"
)

st.divider()

# =======================
# 使用パターン2: 個別コンポーネント組み合わせ
# =======================
st.header("パターン2: 個別コンポーネント組み合わせ")
st.write("必要な部分だけを個別に使用するパターン")

# サイドバー設定は別途取得
if st.checkbox("個別コンポーネント表示", key="individual_mode"):
    # モデル選択のみ
    st.subheader("モデル選択")
    selected_path, model_name = render_model_selector("models", "individual")
    
    if selected_path:
        st.success(f"選択されたモデル: {model_name}")
        st.info(f"パス: {selected_path}")
        
        # Three.jsビューア部分のみ
        if st.button("3Dビューアを表示", key="show_individual"):
            glb_base64, file_size = load_glb_model(selected_path)
            
            if glb_base64:
                # 固定設定でビューア表示
                settings = {
                    'width': 800,
                    'height': 600,
                    'bg_color': "#FFFFFF",
                    'show_grid': True,
                    'auto_rotate': False
                }
                
                success = render_threejs_viewer(glb_base64, settings)
                if success:
                    render_viewer_guide()

st.divider()

# =======================
# 使用パターン3: カスタムレイアウト
# =======================
st.header("パターン3: カスタムレイアウト")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("設定パネル")
    
    # カスタム設定UI
    custom_settings = {
        'width': st.slider("ビューア幅", 400, 1200, 700, key="custom_width"),
        'height': st.slider("ビューア高さ", 300, 800, 500, key="custom_height"),
        'bg_color': st.color_picker("背景色", "#F0F0F0", key="custom_bg"),
        'show_grid': st.checkbox("グリッド", True, key="custom_grid"),
        'auto_rotate': st.checkbox("回転", False, key="custom_rotate")
    }
    
    # モデル選択
    custom_path, custom_name = render_model_selector("models", "custom")

with col2:
    st.subheader("カスタム3Dビューア")
    
    if custom_path:
        glb_base64, file_size = load_glb_model(custom_path)
        
        if glb_base64:
            st.write(f"**表示中**: {custom_name}")
            st.write(f"**サイズ**: {file_size / 1024:.1f} KB")
            
            success = render_threejs_viewer(glb_base64, custom_settings)

# =======================
# フッター
# =======================
st.markdown("---")
st.markdown("""
### モジュール化のメリット

1. **再利用性**: 他のStreamlitアプリでも同じビューアコンポーネントを使用可能
2. **保守性**: 3Dビューア機能の修正は`viewer_components.py`のみで済む
3. **テスト性**: 個別コンポーネントのテストが容易
4. **柔軟性**: 必要な機能のみを組み合わせて使用可能

### 注意点

- **サイドバー要素**: 各コンポーネント内で`st.sidebar`を呼び出す必要がある
- **状態管理**: Streamlitの状態管理機能を適切に使用する必要がある
- **キーの重複**: 複数箇所で使用する場合は一意のkeyを設定すること
""")