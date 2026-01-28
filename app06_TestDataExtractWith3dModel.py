'''
ファンモデル検索・閲覧ダッシュボード
- メーカー別、スペック値（数値範囲）によるモデル絞り込み機能
- Three.js 3Dビューア連動表示
- 試験データ可視化とフィルタリング

'''

import streamlit as st
from pathlib import Path
import streamlit.components.v1 as components
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="ファンモデル検索ダッシュボード",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🔍 ファンモデル検索・閲覧ダッシュボード")

# Initialize connection.
try:
    conn = st.connection("postgresql", type="sql")
    DB_CONNECTED = True
except Exception as e:
    st.error(f"データベース接続エラー: {str(e)}")
    st.info("DBなしモードで動作します。モデルファイルの直接表示のみ利用可能です。")
    DB_CONNECTED = False

# テーブル一覧を取得
if DB_CONNECTED:
    st.sidebar.header("データベース情報")
    if st.sidebar.checkbox("テーブル一覧を表示"):
        try:
            tables_query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
            """
            tables_df = conn.query(tables_query, ttl=0)
            st.sidebar.write("**テーブル一覧:**")
            st.sidebar.dataframe(tables_df)
        except Exception as e:
            st.sidebar.error(f"テーブル情報取得エラー: {str(e)}")

    # 主キー・外部キー情報を取得
    if st.sidebar.checkbox("キー情報を表示"):
        try:
            # 主キー取得
            pk_query = """
            SELECT 
                tc.table_name,
                kcu.column_name,
                'PRIMARY KEY' as key_type
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu 
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
            WHERE tc.constraint_type = 'PRIMARY KEY'
                AND tc.table_schema = 'public'
            ORDER BY tc.table_name, kcu.ordinal_position;
            """
            pk_df = conn.query(pk_query, ttl=0)
            
            # 外部キー取得
            fk_query = """
            SELECT 
                tc.table_name,
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name,
                'FOREIGN KEY' as key_type
            FROM information_schema.table_constraints AS tc 
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
                AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
                AND tc.table_schema = 'public'
            ORDER BY tc.table_name;
            """
            fk_df = conn.query(fk_query, ttl=0)
            
            st.sidebar.write("**主キー:**")
            st.sidebar.dataframe(pk_df)
            
            st.sidebar.write("**外部キー:**")
            st.sidebar.dataframe(fk_df)
        except Exception as e:
            st.sidebar.error(f"キー情報取得エラー: {str(e)}")

# =======================
# データ取得とキャッシュ
# =======================
if DB_CONNECTED:
    @st.cache_data(ttl=600)  # 10分キャッシュ
    def load_fan_data():
        try:
            return conn.query('SELECT * FROM "Fan list";', ttl="10m")
        except Exception as e:
            st.error(f"Fan listテーブルの読み込みエラー: {str(e)}")
            return pd.DataFrame()

    @st.cache_data(ttl=600)
    def load_test_data():
        try:
            return conn.query('SELECT * FROM "FanTestData";', ttl="10m")
        except Exception as e:
            st.error(f"FanTestDataテーブルの読み込みエラー: {str(e)}")
            return pd.DataFrame()

    fan_df = load_fan_data()
    test_df = load_test_data()
else:
    # DBなしモードではダミーデータ
    fan_df = pd.DataFrame()
    test_df = pd.DataFrame()
    st.warning("データベース未接続のため、検索機能は利用できません。3Dビューア（直接モデル選択）のみ利用可能です。")

# =======================
# 高度な検索フィルター UI
# =======================
if DB_CONNECTED and len(fan_df) > 0:
    st.sidebar.header("🔍 検索フィルター")
    
    # フィルター状態の初期化
    filtered_fans = fan_df.copy()

    # 1. テキスト検索
    with st.sidebar.expander("📝 テキスト検索", expanded=True):
        search_text = st.text_input(
            "キーワード検索",
            placeholder="シリーズ名、製品タイプなどを入力...",
            help="すべての文字列カラムから検索します"
        )
        if search_text:
            text_columns = fan_df.select_dtypes(include=['object']).columns
            mask = pd.Series([False] * len(fan_df))
            for col in text_columns:
                mask |= fan_df[col].astype(str).str.contains(search_text, case=False, na=False)
            filtered_fans = filtered_fans[mask]

    # 2. カテゴリフィルター
    with st.sidebar.expander("📂 カテゴリフィルター", expanded=True):
        # メーカー・シリーズフィルター
        if 'series' in fan_df.columns:
            series_options = ['すべて'] + sorted(fan_df['series'].dropna().unique().tolist())
            selected_series = st.selectbox("シリーズ", series_options)
            if selected_series != 'すべて':
                filtered_fans = filtered_fans[filtered_fans['series'] == selected_series]
        
        # 製品タイプフィルター
        if 'product_type' in fan_df.columns:
            product_options = ['すべて'] + sorted(fan_df['product_type'].dropna().unique().tolist())
            selected_product = st.selectbox("製品タイプ", product_options)
            if selected_product != 'すべて':
                filtered_fans = filtered_fans[filtered_fans['product_type'] == selected_product]
        
        # 内部・外部フィルター
        if 'innerouter' in fan_df.columns:
            innerouter_options = ['すべて'] + sorted(fan_df['innerouter'].dropna().unique().tolist())
            selected_innerouter = st.selectbox("内部/外部", innerouter_options)
            if selected_innerouter != 'すべて':
                filtered_fans = filtered_fans[filtered_fans['innerouter'] == selected_innerouter]

    # 3. 数値範囲フィルター
    with st.sidebar.expander("📊 スペック範囲フィルター", expanded=False):
        # 直径フィルター
        if 'diameter' in fan_df.columns:
            diameter_values = fan_df['diameter'].dropna()
            if len(diameter_values) > 0:
                min_diameter = int(diameter_values.min())
                max_diameter = int(diameter_values.max())
                diameter_range = st.slider(
                    "直径範囲 (mm)",
                    min_value=min_diameter,
                    max_value=max_diameter,
                    value=(min_diameter, max_diameter)
                )
                filtered_fans = filtered_fans[
                    (filtered_fans['diameter'] >= diameter_range[0]) &
                    (filtered_fans['diameter'] <= diameter_range[1])
                ]
        
        # 年式フィルター
        if 'year' in fan_df.columns:
            year_values = fan_df['year'].dropna()
            if len(year_values) > 0:
                min_year = int(year_values.min())
                max_year = int(year_values.max())
                year_range = st.slider(
                    "年式範囲",
                    min_value=min_year,
                    max_value=max_year,
                    value=(min_year, max_year)
                )
                filtered_fans = filtered_fans[
                    (filtered_fans['year'] >= year_range[0]) &
                    (filtered_fans['year'] <= year_range[1])
                ]

    # 4. フィルターリセットボタン
    if st.sidebar.button("🔄 フィルターリセット"):
        st.rerun()
else:
    filtered_fans = pd.DataFrame()  # DBが利用できない場合は空のDataFrame

# =======================
# 検索結果表示エリア
# =======================
if DB_CONNECTED and len(fan_df) > 0:
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📋 ファンモデル検索結果")
        
    with col2:
        st.metric(
            "該当モデル数", 
            len(filtered_fans),
            delta=len(filtered_fans) - len(fan_df) if len(fan_df) > 0 else 0
        )

    if len(filtered_fans) > 0:
        # ソート機能
        sort_col1, sort_col2 = st.columns(2)
        with sort_col1:
            sortable_columns = ['id', 'series', 'product_type', 'diameter', 'year']
            available_sort_cols = [col for col in sortable_columns if col in filtered_fans.columns]
            sort_by = st.selectbox("ソート基準", available_sort_cols, index=0)
        
        with sort_col2:
            sort_ascending = st.checkbox("昇順", value=True)
        
        # データソート
        if sort_by in filtered_fans.columns:
            filtered_fans_sorted = filtered_fans.sort_values(sort_by, ascending=sort_ascending)
        else:
            filtered_fans_sorted = filtered_fans
        
        # データテーブル表示
        st.dataframe(
            filtered_fans_sorted, 
            use_container_width=True,
            hide_index=True,
            column_config={
                "diameter": st.column_config.NumberColumn(
                    "直径 (mm)",
                    help="ファン直径（ミリメートル）",
                    format="%d mm"
                ),
                "year": st.column_config.NumberColumn(
                    "年式",
                    help="製造年",
                    format="%d年"
                ),
            }
        )
        
        # 統計情報表示
        with st.expander("📊 検索結果統計", expanded=False):
            stat_col1, stat_col2, stat_col3 = st.columns(3)
            
            with stat_col1:
                if 'product_type' in filtered_fans.columns:
                    st.write("**製品タイプ分布**")
                    product_counts = filtered_fans['product_type'].value_counts()
                    st.bar_chart(product_counts)
            
            with stat_col2:
                if 'diameter' in filtered_fans.columns:
                    st.write("**直径分布**")
                    diameter_data = filtered_fans['diameter'].dropna()
                    if len(diameter_data) > 0:
                        import plotly.express as px
                        fig = px.histogram(x=diameter_data, title="直径分布", labels={'x': '直径 (mm)', 'y': '件数'})
                        fig.update_layout(height=300, showlegend=False)
                        st.plotly_chart(fig, use_container_width=True, key="diameter_histogram")
            
            with stat_col3:
                if 'series' in filtered_fans.columns:
                    st.write("**シリーズ分布**")
                    series_counts = filtered_fans['series'].value_counts()
                    st.bar_chart(series_counts)
        
        # 詳細表示セクション
        st.subheader("📝 詳細情報")
        
        # モデル選択
        selected_model_index = st.selectbox(
            "詳細を表示するモデルを選択",
            options=range(len(filtered_fans_sorted)),
            format_func=lambda i: f"{filtered_fans_sorted.iloc[i].get('series', 'N/A')} - {filtered_fans_sorted.iloc[i].get('product_type', 'N/A')} (ID: {filtered_fans_sorted.iloc[i].get('id', 'N/A')})"
        )
        
        if selected_model_index is not None:
            selected_model = filtered_fans_sorted.iloc[selected_model_index]
            
            # 詳細情報を3列で表示
            detail_col1, detail_col2, detail_col3 = st.columns(3)
            
            with detail_col1:
                st.write("**基本情報**")
                for col in ['id', 'series', 'product_type']:
                    if col in selected_model.index:
                        st.write(f"**{col}**: {selected_model[col]}")
            
            with detail_col2:
                st.write("**仕様**")
                for col in ['diameter', 'innerouter', 'fan_type']:
                    if col in selected_model.index:
                        st.write(f"**{col}**: {selected_model[col]}")
            
            with detail_col3:
                st.write("**その他**")
                for col in ['year', 'fanID', 'created_at']:
                    if col in selected_model.index:
                        st.write(f"**{col}**: {selected_model[col]}")

    else:
        st.info("🔍 検索条件に一致するファンモデルが見つかりません。フィルター条件を調整してください。")
elif DB_CONNECTED:
    st.info("データベースは接続されていますが、ファンデータが見つかりません。")
else:
    st.info("データベースに接続されていません。3Dビューア（直接モデル選択）をご利用ください。")


# =======================
# 試験データセクション
# =======================
if DB_CONNECTED and len(test_df) > 0:
    st.divider()
    st.header("🧪 ファン試験データ")

    # 選択されたファンモデルに関連する試験データのフィルタリング
    if len(filtered_fans) > 0:
        # ファンIDでの関連試験データ抽出
        related_test_data = test_df.copy()
        
        # 試験データフィルター
        test_filter_col1, test_filter_col2 = st.columns(2)
        
        with test_filter_col1:
            show_related_only = st.checkbox(
                "選択モデル関連データのみ表示", 
                value=False,
                help="選択されたファンモデルに関連する試験データのみを表示"
            )
        
        with test_filter_col2:
            if 'TestDate' in test_df.columns:
                date_filter = st.checkbox("日付範囲でフィルター", value=False)
        
        if show_related_only and len(filtered_fans) > 0:
            # 選択されたファンモデルのIDを取得
            selected_fan_ids = filtered_fans['fanID'].dropna().tolist()
            if selected_fan_ids:
                related_test_data = test_df[test_df['fanID'].isin(selected_fan_ids)]
        
        df = related_test_data  # グローバル変数を更新（後続の処理で使用）
        
        # 試験データ統計
        test_stat_col1, test_stat_col2, test_stat_col3 = st.columns(3)
        
        with test_stat_col1:
            st.metric("総試験データ数", len(test_df))
        
        with test_stat_col2:
            st.metric("表示中データ数", len(df))
        
        with test_stat_col3:
            if len(df) > 0 and 'TestDate' in df.columns:
                latest_test = df['TestDate'].max()
                st.metric("最新試験日", str(latest_test))
        
        # 試験データテーブル表示
        if len(df) > 0:
            st.dataframe(
                df, 
                use_container_width=True,
                hide_index=True,
                column_config={
                    "TestDate": st.column_config.DateColumn(
                        "試験日",
                        help="試験実施日"
                    ),
                    "temp_o_[degC]": st.column_config.NumberColumn(
                        "吐出温度 (°C)",
                        help="吐出側温度",
                        format="%.1f°C"
                    ),
                    "temp_c_[defC]": st.column_config.NumberColumn(
                        "吸込温度 (°C)", 
                        help="吸込側温度",
                        format="%.1f°C"
                    ),
                }
            )
            
            # プロット機能
            st.subheader("📈 データプロット")
            if len(df) > 0:
                import plotly.graph_objects as go
                import json
                
                # プロット対象の試験データを選択
                test_options = [f"ID: {row['id']} - {row.get('FanName', 'N/A')} ({row.get('TestDate', 'N/A')})" 
                                for idx, row in df.iterrows()]
                
                selected_tests = st.multiselect(
                    "表示する試験データを選択（複数選択可）",
                    options=range(len(df)),
                    format_func=lambda x: test_options[x],
                    default=list(range(min(5, len(df)))),  # デフォルトで最初の5件を選択
                    key="db_connected_multiselect"
                )
                
                if selected_tests:
                    fig = go.Figure()
                    
                    for idx in selected_tests:
                        row = df.iloc[idx]
                        
                        # JSONB配列をPythonリストに変換
                        try:
                            # PostgreSQLから返されるJSONBは文字列またはリストの可能性がある
                            q_data = row['Q_[m3min]']
                            ps_data = row['Ps_[Pa]']
                            
                            # 文字列の場合はJSON解析
                            if isinstance(q_data, str):
                                q_values = json.loads(q_data)
                            else:
                                q_values = q_data
                            
                            if isinstance(ps_data, str):
                                ps_values = json.loads(ps_data)
                            else:
                                ps_values = ps_data
                            
                            # プロット追加
                            fig.add_trace(go.Scatter(
                                x=q_values,
                                y=ps_values,
                                mode='lines+markers',
                                name=row.get('FanName', f"Test-{row['id']}"),
                                hovertemplate='Q: %{x:.2f} m³/min<br>Ps: %{y:.2f} Pa<extra></extra>'
                            ))
                        except Exception as e:
                            st.warning(f"データID {row['id']} の解析エラー: {str(e)}")
                    
                    # グラフレイアウト設定
                    fig.update_layout(
                        title="ファンP-Q特性曲線",
                        xaxis_title="風量 Q [m³/min]",
                        yaxis_title="静圧 Ps [Pa]",
                        hovermode='closest',
                        template="plotly_white",
                        height=600,
                        showlegend=True,
                        legend=dict(
                            yanchor="top",
                            y=0.99,
                            xanchor="left",
                            x=0.01
                        )
                    )
                    
                    st.plotly_chart(fig, use_container_width=True, key="db_connected_pq_chart")
                    
                    # データテーブル表示
                    with st.expander("選択した試験データの詳細"):
                        for idx in selected_tests:
                            row = df.iloc[idx]
                            fan_name = row.get('FanName') or f"Test-{row['id']}"
                            st.write(f"**{fan_name}**")
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.write(f"試験日: {row.get('TestDate', 'N/A')}")
                                st.write(f"温度(吐出): {row.get('temp_o_[degC]', 'N/A')} °C")
                            with col2:
                                st.write(f"Single Fan Test: {row.get('SingleFanTest', 'N/A')}")
                                st.write(f"温度(吸込): {row.get('temp_c_[defC]', 'N/A')} °C")
                            with col3:
                                st.write(f"Bellmouth: {row.get('bellmouth', 'N/A')}")
                                st.write(f"コメント: {row.get('comment', 'N/A')}")
                            st.divider()
                else:
                    st.info("プロットする試験データを選択してください")
                    selected_tests = []  # プロットが選択されていない場合の初期化
        else:
            st.info("選択条件に該当する試験データがありません。")
            selected_tests = []  # データがない場合の初期化
    else:
        df = test_df
        selected_tests = []  # データがない場合の初期化
        st.info("試験データを読み込み中...")
else:
    df = pd.DataFrame()
    selected_tests = []  # DBが利用できない場合の初期化

def pick_model_identifier(row):
    keys = [
        "model",
        "Model",
        "model_name",
        "ModelName",
        "model_path",
        "model_glb",
        "FanModel",
        "fan_model",
        "fan_model_name",
        "FanName",
        "fanID",
        "id",
    ]
    for key in keys:
        if key in row and row.get(key):
            return str(row.get(key))
    return None


def resolve_glb_path(model_identifier, base_dir="models"):
    base_path = Path(base_dir)
    if not base_path.exists():
        raise FileNotFoundError(f"モデルディレクトリ {base_path} が見つかりません。")

    raw = Path(model_identifier)
    candidates = []

    if raw.is_absolute() and raw.exists():
        return raw

    if raw.suffix.lower() == ".glb":
        candidates.append(base_path / raw.name)
        candidates.append(base_path / raw.name.lower())
    else:
        candidates.append(base_path / f"{raw.stem}.glb")
        candidates.append(base_path / f"{raw.name}.glb")

    candidates.extend(base_path.glob(f"{raw.stem}*.glb"))

    for candidate in candidates:
        if candidate.exists():
            return candidate

    raise FileNotFoundError(f"モデル {model_identifier} の.glbが {base_path} に見つかりません。")


# =======================
# 3D ビューアセクション
# =======================
st.divider()
st.header("🎯 3D ファンモデルビューア")

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

# 3Dビューア表示処理
if DB_CONNECTED and len(df) > 0:
    # ビューア用データ選択
    viewer_tab1, viewer_tab2 = st.tabs(["📊 選択からビューア", "🎛️ 直接モデル選択"])
    
    with viewer_tab1:
        # 試験データベースの3Dビューア表示
        if 'selected_tests' in locals() and selected_tests:
            viewer_candidates = selected_tests
        else:
            viewer_candidates = list(range(len(df)))
        
        if viewer_candidates:
            # test_optionsを定義
            test_options = [f"ID: {df.iloc[i]['id']} - {df.iloc[i].get('FanName', 'N/A')} ({df.iloc[i].get('TestDate', 'N/A')})" 
                            for i in range(len(df))]
            
            viewer_index = st.selectbox(
                "3Dビューで表示する試験データ",
                options=viewer_candidates,
                format_func=lambda i: test_options[i] if i < len(test_options) else f"Test-{i}"
            )
            
            target_row = df.iloc[viewer_index]
            fan_name = target_row.get('FanName') or target_row.get('fanID') or f"Test-{target_row.get('id', viewer_index)}"
            model_identifier = pick_model_identifier(target_row)
            
            viewer_model_path = None
            
            if not model_identifier:
                st.warning("試験データにモデル識別子が見つかりません。代替モデルから選択してください。")
            else:
                try:
                    viewer_model_path = resolve_glb_path(model_identifier, base_dir="models")
                    st.success(f"モデルを自動解決: {model_identifier}")
                except FileNotFoundError as exc:
                    st.warning(f"自動解決失敗: {str(exc)}")
        else:
            st.info("表示可能な試験データがありません。")
    
    with viewer_tab2:
        # 直接モデルファイル選択
        models_dir = Path("models")
        if models_dir.exists():
            glb_files = list(models_dir.glob("*.glb"))
            if glb_files:
                manual_model_index = st.selectbox(
                    "利用可能なモデルから選択",
                    options=range(len(glb_files)),
                    format_func=lambda i: glb_files[i].name
                )
                viewer_model_path = glb_files[manual_model_index]
                fan_name = f"Manual: {glb_files[manual_model_index].stem}"
            else:
                st.error("modelsディレクトリに.glbファイルがありません")
        else:
            st.error("modelsディレクトリが見つかりません")

else:
    # DB未接続または試験データなしの場合は直接モデル選択のみ
    st.info("データベースが利用できないため、直接モデル選択機能のみ利用可能です。")
    
    models_dir = Path("models")
    if models_dir.exists():
        glb_files = list(models_dir.glob("*.glb"))
        if glb_files:
            manual_model_index = st.selectbox(
                "利用可能なモデルから選択",
                options=range(len(glb_files)),
                format_func=lambda i: glb_files[i].name,
                key="direct_model_select"
            )
            viewer_model_path = glb_files[manual_model_index]
            fan_name = f"Manual: {glb_files[manual_model_index].stem}"
        else:
            st.error("modelsディレクトリに.glbファイルがありません")
            viewer_model_path = None
            fan_name = "No Model"
    else:
        st.error("modelsディレクトリが見つかりません")
        viewer_model_path = None
        fan_name = "No Model"

# 3Dビューア表示
if 'viewer_model_path' in locals() and viewer_model_path and Path(viewer_model_path).exists():
    try:
        import base64
        
        with open(viewer_model_path, 'rb') as f:
            glb_data = f.read()
            glb_base64 = base64.b64encode(glb_data).decode()
        
        # Three.jsテンプレートファイルの確認
        template_path = Path("three_html/viewer01.html")
        if not template_path.exists():
            st.error(f"Three.jsテンプレートファイル '{template_path}' が見つかりません。")
        else:
            template = template_path.read_text(encoding="utf-8")
            threejs_html = template.format(
                bg_color=bg_color,
                width=width,
                height=height,
                auto_rotate=str(auto_rotate).lower(),
                show_grid=str(show_grid).lower(),
                glb_base64=glb_base64,
            )
            
            # ビューア情報表示
            viewer_info_col1, viewer_info_col2 = st.columns([3, 1])
            with viewer_info_col1:
                st.write(f"**表示モデル**: {fan_name}")
            with viewer_info_col2:
                st.write(f"**ファイルサイズ**: {len(glb_data) / 1024:.1f} KB")
            
            # Three.js ビューア埋め込み
            components.html(threejs_html, height=height + 20, scrolling=False)
            
            # 操作ガイド
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
            
            st.caption(f"📁 使用モデル: `{viewer_model_path}`")
            
    except Exception as e:
        st.error(f"3Dモデルの読み込みエラー: {str(e)}")
        st.exception(e)
else:
    st.info("表示する3Dモデルを選択してください。")

# フッター
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <small>Powered by Streamlit + Three.js | GPU加速レンダリング対応</small>
</div>
""", unsafe_allow_html=True)

