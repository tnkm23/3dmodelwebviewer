'''
DBからカラム1（上位包含）、カラム2（下位包含）のリスト抽出
ドロップダウンでカラム1とカラム２のリストから選択
該当する行のデータを表示

'''

import streamlit as st

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