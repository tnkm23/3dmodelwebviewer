"""
Supabaseデータベースにサンプルデータを追加するスクリプト
"""

import streamlit as st
import uuid
from datetime import date, timedelta

# Initialize connection
conn = st.connection("postgresql", type="sql")

st.title("サンプルデータ追加ツール")

# 現在のFan listのレコード数を確認
current_count = conn.query('SELECT COUNT(*) as count FROM "Fan list";', ttl=0)
st.write(f"現在のFan listレコード数: {current_count['count'][0]}")

# データ追加ボタン
if st.button("サンプルデータを20件追加"):
    try:
        # Fan listに20件のサンプルデータを追加
        series_list = ["Series-A", "Series-B", "Series-C", "Series-D"]
        product_types = ["Axial", "Centrifugal", "Mixed Flow"]
        inner_outer = ["Inner", "Outer"]
        diameters = [100, 120, 150, 200, 250]
        
        insert_query = """
        INSERT INTO "Fan list" (series, product_type, innerouter, diameter, year, fan_type)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING fanID, id;
        """
        
        with st.spinner("データを追加中..."):
            inserted_fans = []
            
            # SQLAlchemyのexecute経由で挿入
            for i in range(20):
                series = series_list[i % len(series_list)]
                product_type = product_types[i % len(product_types)]
                io = inner_outer[i % len(inner_outer)]
                diameter = diameters[i % len(diameters)]
                year = 2020 + (i % 5)
                fan_type = "axial" if i % 2 == 0 else "centrifugal"
                
                # conn.sessionを使って直接実行
                result = conn.session.execute(
                    insert_query,
                    (series, product_type, io, diameter, year, fan_type)
                )
                conn.session.commit()
                
                row = result.fetchone()
                inserted_fans.append({
                    'fanID': row[0],
                    'id': row[1],
                    'series': series,
                    'product_type': product_type
                })
                
            st.success(f"{len(inserted_fans)}件のデータを追加しました！")
            
            # 追加されたデータを表示
            st.subheader("追加されたデータ")
            import pandas as pd
            st.dataframe(pd.DataFrame(inserted_fans))
            
            # 更新後のレコード数を表示
            new_count = conn.query('SELECT COUNT(*) as count FROM "Fan list";', ttl=0)
            st.write(f"更新後のレコード数: {new_count['count'][0]}")
            
    except Exception as e:
        st.error(f"エラーが発生しました: {str(e)}")
        conn.session.rollback()

# 現在のデータを表示
if st.checkbox("現在のデータを表示"):
    df = conn.query('SELECT * FROM "Fan list" ORDER BY id DESC LIMIT 50;', ttl=0)
    st.dataframe(df, use_container_width=True)
