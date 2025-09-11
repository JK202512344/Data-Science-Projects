import streamlit as st
from add_update import add_update
from analytics import analytics
from analytics_by_month import analytics_months

st.title("Expense Management System")
tab1, tab2, tab3 = st.tabs(["Add Update", "Analytics by Category","Analytics by Month"])

with tab1:
  add_update()
with tab2:
  analytics()
with tab3:
  analytics_months()