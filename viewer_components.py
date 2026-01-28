"""
3Dビューアコンポーネントモジュール
StreamlitアプリケーションのThree.js 3Dビューア機能をモジュール化
"""

import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
import base64


def render_viewer_sidebar():
    """
    ビューア設定のサイドバー要素を生成
    戻り値: 設定値の辞書
    """
    st.sidebar.header("ビューア設定")
    
    settings = {
        'width': st.sidebar.slider("幅 (px)", 400, 1200, 800),
        'height': st.sidebar.slider("高さ (px)", 300, 900, 600),
        'bg_color': st.sidebar.color_picker("背景色", "#C4C3C3"),
        'show_grid': st.sidebar.checkbox("グリッド表示", True),
        'auto_rotate': st.sidebar.checkbox("自動回転", False)
    }
    
    return settings


def render_viewer_controls():
    """
    ビューアコントロールボタンを生成
    戻り値: ボタンが押されたかの状態
    """
    col1, col2, col3 = st.columns(3)
    controls = {}
    
    with col1:
        controls['reset'] = st.button("🔄 リセットビュー")
    with col2:
        if st.button("📷 スクリーンショット", help="右クリックで画像を保存できます"):
            st.info("ビューア上で右クリック → 画像を保存")
            controls['screenshot'] = True
    with col3:
        controls['reload'] = st.button("🔍 リロード")
    
    return controls


def render_model_selector(models_dir="models", key_suffix=""):
    """
    モデル選択UI
    
    Args:
        models_dir: モデルファイルディレクトリ
        key_suffix: Streamlit要素のkey識別用サフィックス
    
    戻り値: (selected_model_path, model_display_name)
    """
    models_path = Path(models_dir)
    
    if not models_path.exists():
        st.error(f"{models_dir}ディレクトリが見つかりません")
        return None, "No Model"
    
    glb_files = list(models_path.glob("*.glb"))
    
    if not glb_files:
        st.error(f"{models_dir}ディレクトリに.glbファイルがありません")
        return None, "No Model"
    
    model_index = st.selectbox(
        "利用可能なモデルから選択",
        options=range(len(glb_files)),
        format_func=lambda i: glb_files[i].name,
        key=f"model_selector_{key_suffix}"
    )
    
    selected_path = glb_files[model_index]
    display_name = f"Manual: {selected_path.stem}"
    
    return selected_path, display_name


def render_test_data_selector(df, test_options, key_suffix=""):
    """
    試験データ選択UI
    
    Args:
        df: 試験データDataFrame
        test_options: 表示用オプションリスト
        key_suffix: Streamlit要素のkey識別用サフィックス
    
    戻り値: (selected_index, target_row)
    """
    if len(df) == 0:
        st.info("表示可能な試験データがありません。")
        return None, None
    
    viewer_index = st.selectbox(
        "3Dビューで表示する試験データ",
        options=range(len(df)),
        format_func=lambda i: test_options[i] if i < len(test_options) else f"Test-{i}",
        key=f"test_selector_{key_suffix}"
    )
    
    return viewer_index, df.iloc[viewer_index]


def load_glb_model(model_path):
    """
    GLBモデルファイルを読み込みBase64エンコード
    
    Args:
        model_path: GLBファイルのパス
    
    戻り値: (glb_base64_data, file_size_bytes)
    """
    try:
        with open(model_path, 'rb') as f:
            glb_data = f.read()
            glb_base64 = base64.b64encode(glb_data).decode()
        return glb_base64, len(glb_data)
    except Exception as e:
        st.error(f"モデルファイルの読み込みエラー: {str(e)}")
        return None, 0


def render_threejs_viewer(glb_base64, settings, template_path="three_html/viewer01.html"):
    """
    Three.js 3Dビューアを描画
    
    Args:
        glb_base64: Base64エンコードされたGLBデータ
        settings: ビューア設定辞書
        template_path: Three.jsテンプレートファイルのパス
    
    戻り値: 描画成功/失敗のブール値
    """
    template_file = Path(template_path)
    
    if not template_file.exists():
        st.error(f"Three.jsテンプレートファイル '{template_path}' が見つかりません。")
        return False
    
    try:
        template = template_file.read_text(encoding="utf-8")
        threejs_html = template.format(
            bg_color=settings['bg_color'],
            width=settings['width'],
            height=settings['height'],
            auto_rotate=str(settings['auto_rotate']).lower(),
            show_grid=str(settings['show_grid']).lower(),
            glb_base64=glb_base64,
        )
        
        # Three.js ビューア埋め込み
        components.html(threejs_html, height=settings['height'] + 20, scrolling=False)
        return True
        
    except Exception as e:
        st.error(f"Three.jsビューアの描画エラー: {str(e)}")
        st.exception(e)
        return False


def render_viewer_guide():
    """
    ビューア操作ガイドを表示
    """
    with st.expander("🕹️ ビューア操作方法", expanded=False):
        st.markdown("""
        ### マウス操作
        - **左クリック + ドラッグ**: モデルを回転
        - **右クリック + ドラッグ**: カメラ移動（パン）
        - **マウスホイール**: ズームイン/アウト
        
        ### 表示設定
        - **グリッド表示**: 基準となるグリッドの表示/非表示
        - **自動回転**: モデルの自動回転機能
        - **背景色**: ビューアの背景色変更
        
        ### パフォーマンス
        - GPU加速レンダリング対応（WebGL 2.0）
        - リアルタイム照明とシャドウ
        - 高解像度モデル表示対応
        """)


def render_complete_3d_viewer(df=None, test_options=None, models_dir="models", key_suffix="default"):
    """
    完全な3Dビューア（統合版）
    
    Args:
        df: 試験データDataFrame（Noneの場合は直接モデル選択のみ）
        test_options: 試験データ表示オプション
        models_dir: モデルディレクトリ
        key_suffix: Streamlit要素識別用サフィックス
    
    戻り値: 描画成功/失敗のブール値
    """
    # サイドバー設定を取得
    settings = render_viewer_sidebar()
    
    # コントロールボタン
    controls = render_viewer_controls()
    
    # リセット・リロード処理
    if controls.get('reset') or controls.get('reload'):
        st.rerun()
    
    # タブ形式のモデル選択
    if df is not None and len(df) > 0:
        viewer_tab1, viewer_tab2 = st.tabs(["📊 試験データから選択", "🎛️ 直接モデル選択"])
        
        with viewer_tab1:
            viewer_index, target_row = render_test_data_selector(df, test_options, key_suffix + "_test")
            if target_row is not None:
                # モデル識別子の解決処理をここに実装
                # （元のpick_model_identifier、resolve_glb_path関数を使用）
                pass
        
        with viewer_tab2:
            viewer_model_path, fan_name = render_model_selector(models_dir, key_suffix + "_manual")
    else:
        # データベースなしモード
        st.info("データベースが利用できないため、直接モデル選択機能のみ利用可能です。")
        viewer_model_path, fan_name = render_model_selector(models_dir, key_suffix + "_direct")
    
    # 3Dビューア表示
    if 'viewer_model_path' in locals() and viewer_model_path and Path(viewer_model_path).exists():
        glb_base64, file_size = load_glb_model(viewer_model_path)
        
        if glb_base64:
            # ビューア情報表示
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**表示モデル**: {fan_name}")
            with col2:
                st.write(f"**ファイルサイズ**: {file_size / 1024:.1f} KB")
            
            # Three.jsビューア描画
            success = render_threejs_viewer(glb_base64, settings)
            
            if success:
                render_viewer_guide()
                st.caption(f"📁 使用モデル: `{viewer_model_path}`")
                return True
    
    else:
        st.info("表示する3Dモデルを選択してください。")
    
    return False