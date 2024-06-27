import streamlit as st
import numpy as np
import pandas as pd
import altair as alt
from datetime import datetime, timedelta
from st_supabase_connection import SupabaseConnection, execute_query

st.set_page_config(page_title='Support Ticket Workflow', page_icon='data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABwAAAAcCAMAAABF0y+mAAAAY1BMVEX////9+PjXjI6+P0K/QkXBSErpv8D14+PJZWi6MTS7NTjFVljryMjCT1G6MjW7Njm5LTDTfoDgqaq4Jir67+/ThIbx19fz3d3doqP25+fIYGPReXvdnqDYkpP79PTluLm+QELIVu6CAAAAy0lEQVR4AX2SBQ7DQAwEHc4xlMP//2TpnNJGHbFW2pGBPsjyokxUNf3StEI+EaqBUBvrnvhAQCxkCncRsv3BplDKI4SnVrgnQmV/lAfIsrPjVlFvKLnVmgsqOw59j8q6TEppIyoHkZS2OqKy9zxIu6FU3OrHCcLZcmtZozJfW7sTKtdBxGFPRN/DHAtWuohTRs9KowkIr0FQORnBp9wYRHOrLGcCzju+iDrilKvS9nsIG7UqB0LlwsqixnCQT5zo8CL7sJRlcUd8v9YNS1IRq/svf5IAAAAASUVORK5CYII=')
st.image("https://i0.wp.com/inmac.co.in/wp-content/uploads/2022/09/INMAC-web-logo.png?w=721&ssl=1")
st.title( 'Support Ticket Workflow')

conn = st.connection("supabase",type=SupabaseConnection)

df = execute_query(conn.table("nextgen1").select("*", count="None"), ttl="0")

if len(df.data) > 0:
    df = pd.DataFrame(df.data)
    df["created_at"]= pd.to_datetime(df["created_at"]).astype(str)
    df["branchAndDateTime"] = df["location"]+" "+df["created_at"]
    select = st.selectbox("Select Patch Report", options=list(df["branchAndDateTime"]))
    if select:
        images = list(df.loc[df["branchAndDateTime"]==select, "images"])[0]
        cpuList = list(df.loc[df["branchAndDateTime"]==select, "cpu"])[0]
        monitorList = list(df.loc[df["branchAndDateTime"]==select, "monitor"])[0]
        id = list(df.loc[df["branchAndDateTime"]==select, "monitor"])[0]
        if images != None:
            for i in images:
                data = conn.download("images" ,source_path=i, ttl=None)
                st.image(data[0])
            with st.form("Patch"):    
                cpu = st.text_area("CPU Serial No.'s", placeholder="Seperate with comma", value=cpuList)
                monitor = st.text_area("Monitor Serial No.'s", placeholder="Seperate with comma", value=monitorList)
                save = st.form_submit_button("Save Changes", use_container_width=True)
            if save:
                execute_query(conn.table('nextgen1').update([{
                                "cpu":cpu,
                                "monitor":monitor,
                        }]).eq("id", id), ttl='0')