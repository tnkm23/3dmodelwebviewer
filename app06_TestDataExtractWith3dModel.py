'''
DBからカラム1（上位包含）、カラム2（下位包含）のリスト抽出
ドロップダウンでカラム1とカラム２のリストから選択
該当する行のデータを表示

'''

import streamlit as st
import os
from pathlib import Path
import streamlit.components.v1 as components

st.title("データベース検索")

# Initialize connection.
conn = st.connection("postgresql", type="sql")

# テーブル一覧を取得
st.sidebar.header("データベース情報")
if st.sidebar.checkbox("テーブル一覧を表示"):
    tables_query = """
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public'
    ORDER BY table_name;
    """
    tables_df = conn.query(tables_query, ttl=0)
    st.sidebar.write("**テーブル一覧:**")
    st.sidebar.dataframe(tables_df)

# 主キー・外部キー情報を取得
if st.sidebar.checkbox("キー情報を表示"):
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

# DBにある全リストを一覧取得
df = conn.query('SELECT * FROM "Fan list";', ttl="10m")

# カラム名を取得
columns = df.columns.tolist()

# カラム1は4番目（Producttype）、カラム2は3番目（series）
column1_name = columns[3] if len(columns) >= 4 else None  # Producttype
column2_name = columns[2] if len(columns) >= 3 else None  # series

st.sidebar.header("検索条件")

# カラム1（Producttype）の選択
if column1_name:
    unique_values_col1 = df[column1_name].unique().tolist()
    selected_col1 = st.sidebar.selectbox(
        f"{column1_name} を選択",
        ["すべて"] + unique_values_col1
    )
else:
    st.error("カラムが見つかりません")
    st.stop()

# カラム2（series）の選択
if column2_name:
    # カラム1で絞り込んだ後のカラム2の選択肢を表示
    if selected_col1 != "すべて":
        filtered_df = df[df[column1_name] == selected_col1]
        unique_values_col2 = filtered_df[column2_name].unique().tolist()
    else:
        unique_values_col2 = df[column2_name].unique().tolist()
    
    selected_col2 = st.sidebar.selectbox(
        f"{column2_name} を選択",
        ["すべて"] + unique_values_col2
    )
else:
    selected_col2 = "すべて"

# フィルタリング
filtered_data = df.copy()

if selected_col1 != "すべて":
    filtered_data = filtered_data[filtered_data[column1_name] == selected_col1]

if column2_name and selected_col2 != "すべて":
    filtered_data = filtered_data[filtered_data[column2_name] == selected_col2]

# 結果表示
st.subheader("検索結果")
st.write(f"該当件数: {len(filtered_data)} 件")

if len(filtered_data) > 0:
    st.dataframe(filtered_data, use_container_width=True)
    
    # 詳細表示
    st.subheader("詳細データ")
    for idx, row in filtered_data.iterrows():
        with st.expander(f"行 {idx + 1}: {row[column1_name]} - {row.get(column2_name, '')}"):
            for col in columns:
                st.write(f"**{col}**: {row[col]}")
else:
    st.info("該当するデータがありません")

# 全データ表示オプション
if st.sidebar.checkbox("全データを表示"):
    st.subheader("全データ")
    st.dataframe(df, use_container_width=True)


# 試験データリスト表示
st.subheader("ファン試験データ")
df = conn.query('SELECT * FROM "FanTestData";', ttl="10m")
st.dataframe(df, use_container_width=True)

# 結果プロット
st.subheader("データプロット")

# FanTestDataからプロット用のデータを準備
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
        default=list(range(min(5, len(df))))  # デフォルトで最初の5件を選択
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
        
        st.plotly_chart(fig, use_container_width=True)
        
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
else:
    st.info("試験データが見つかりません")


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
    st.write(f"選択した試験データのファン: {fan_name}")
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

