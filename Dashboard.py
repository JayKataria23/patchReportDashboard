import streamlit as st
import numpy as np
import pandas as pd
import altair as alt
from datetime import datetime, timedelta
from st_supabase_connection import SupabaseConnection, execute_query
import smtplib
from email.message import EmailMessage

# Page title
st.set_page_config(page_title='Support Ticket Workflow', page_icon='data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABwAAAAcCAMAAABF0y+mAAAAY1BMVEX////9+PjXjI6+P0K/QkXBSErpv8D14+PJZWi6MTS7NTjFVljryMjCT1G6MjW7Njm5LTDTfoDgqaq4Jir67+/ThIbx19fz3d3doqP25+fIYGPReXvdnqDYkpP79PTluLm+QELIVu6CAAAAy0lEQVR4AX2SBQ7DQAwEHc4xlMP//2TpnNJGHbFW2pGBPsjyokxUNf3StEI+EaqBUBvrnvhAQCxkCncRsv3BplDKI4SnVrgnQmV/lAfIsrPjVlFvKLnVmgsqOw59j8q6TEppIyoHkZS2OqKy9zxIu6FU3OrHCcLZcmtZozJfW7sTKtdBxGFPRN/DHAtWuohTRs9KowkIr0FQORnBp9wYRHOrLGcCzju+iDrilKvS9nsIG7UqB0LlwsqixnCQT5zo8CL7sJRlcUd8v9YNS1IRq/svf5IAAAAASUVORK5CYII=')
st.image("https://i0.wp.com/inmac.co.in/wp-content/uploads/2022/09/INMAC-web-logo.png?w=721&ssl=1")
st.title( 'Patch Report Dashboard')

conn = st.connection("supabase",type=SupabaseConnection)


df = execute_query(conn.table("nextgen1").select("*", count="None"), ttl="0")

if len(df.data) > 0:
    df = pd.DataFrame(df.data)
    status_col = st.columns((3,1))
    with status_col[0]:
        st.subheader('Patch Report Analysis')
    with status_col[1]:
        st.write(f'No. of reports: `{len(df)}`')
        st.write(f'No. of patches: `{len(df)}`')

    date_range = st.date_input("Date Range", value=[datetime.today()-timedelta(days=30), datetime.today()])


    df['created_at']= pd.to_datetime(df['created_at']).dt.date
    filtered_df = df

    if len(date_range) == 2:
        start_date = date_range[0]
        end_date = date_range[1]
        if start_date < end_date:
            filtered_df = df.loc[(df['created_at'] > start_date) & (df['created_at'] <= end_date)]
        else:
            st.error("Error: Start date is not less than end date")
    else:
        st.error("Entor complete date range")

    location = st.multiselect("Location", options=df["location"].unique())
    if len(location)!=0:
        filtered_df= filtered_df[filtered_df["location"].isin(location)]

    
    engineer = st.multiselect("Engineer", options=df["engineer_name"].unique())
    if len(engineer)!=0:
        filtered_df= filtered_df[filtered_df["engineer_name"].isin(engineer)]

    
    st.write("### Reports")
    status_plot = (
        alt.Chart(filtered_df)
        .mark_bar()
        .encode(
            x=alt.X("date(created_at):O", axis=alt.Axis(title='Days')) ,
            y="count():Q",
            xOffset="status:N",
            color=alt.Color("status:N", legend=alt.Legend(title="Status")),
        )
        .configure_legend(
            orient="bottom", titleFontSize=14, labelFontSize=14, titlePadding=5
        )
    )
    st.altair_chart(status_plot, use_container_width=True, theme="streamlit")


    emails = st.text_area("Emails", placeholder="Seperate by columns")
    subject = st.text_input("Subject", placeholder="Write the Subject here. . . ")
    content = st.text_area("Content", placeholder="Write your Content here. . . ")
    if st.button("Send Report", type='primary'):
        msg = EmailMessage()
        sender = "imbuzixjay@gmail.com"
        password = "aehl bovs lfaj lybs"
        to = emails
        content = content + "\n\n"
        msg['From'] = sender
        msg['Subject'] = subject
        msg.set_content(content)
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(sender, password)
            msg['to'] = to
            smtp.send_message(msg)
            st.success("Email Sent!")
