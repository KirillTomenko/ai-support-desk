import pandas as pd
import streamlit as st
from sqlalchemy import text

from app.db.init_db import init_db
from app.db.session import engine


st.set_page_config(page_title="AI Support Inbox Dashboard", layout="wide")
init_db()

st.title("AI Support Inbox Dashboard")

tickets = pd.read_sql(
    text(
        """
        SELECT
            t.id,
            t.source,
            t.status,
            t.category,
            t.priority,
            t.summary,
            t.created_at,
            c.username,
            c.email
        FROM tickets t
        JOIN customers c ON c.id = t.customer_id
        ORDER BY t.created_at DESC
        """
    ),
    engine,
)

total_tickets = len(tickets)
new_tickets = int((tickets["status"] == "new").sum()) if total_tickets else 0
urgent_tickets = int((tickets["priority"] == "urgent").sum()) if total_tickets else 0
high_tickets = int((tickets["priority"] == "high").sum()) if total_tickets else 0

metric_total, metric_new, metric_urgent, metric_high = st.columns(4)
metric_total.metric("Всего тикетов", total_tickets)
metric_new.metric("Новые", new_tickets)
metric_urgent.metric("Urgent", urgent_tickets)
metric_high.metric("High", high_tickets)

if tickets.empty:
    st.info("Пока нет обращений. Отправьте запрос в API или напишите Telegram-боту.")
    st.stop()

left, right = st.columns(2)

with left:
    st.subheader("Категории")
    st.bar_chart(tickets["category"].value_counts())

with right:
    st.subheader("Приоритеты")
    st.bar_chart(tickets["priority"].value_counts())

st.subheader("Последние обращения")
st.dataframe(
    tickets[
        [
            "id",
            "created_at",
            "source",
            "status",
            "priority",
            "category",
            "summary",
            "username",
            "email",
        ]
    ],
    use_container_width=True,
    hide_index=True,
)
