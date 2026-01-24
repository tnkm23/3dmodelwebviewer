# streamlit_app.py

import streamlit as st

# Initialize connection.
conn = st.connection("postgresql", type="sql")

# Perform query.
df = conn.query('SELECT * FROM "Fan list";', ttl="10m")

# Print results.
st.subheader("データフレーム")
st.dataframe(df)

st.subheader("カラム名")
st.write(df.columns.tolist())

st.subheader("行ごとのデータ")
for idx, row in df.iterrows():
    st.write(f"Row {idx}: {row.to_dict()}")