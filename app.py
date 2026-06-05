import streamlit as st
import pandas as pd
import plotly.express as px

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="CX Intelligence Platform", layout="wide")

# =========================
# UI HEADER
# =========================
st.title("📊 Customer Experience Intelligence Platform")
st.caption("AI-powered CSAT → NPS Analytics Dashboard")

# =========================
# FILE UPLOAD
# =========================
uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.success("File Loaded Successfully!")
else:
    st.warning("Please upload dataset to continue")
    st.stop()

# =========================
# DATA CLEANING
# =========================
df = df.dropna(subset=["CSAT Score"])

# =========================
# NPS LOGIC
# =========================
def segment(score):
    if score >= 4:
        return "Promoter"
    elif score == 3:
        return "Passive"
    else:
        return "Detractor"

df["Segment"] = df["CSAT Score"].apply(segment)

total = len(df)
promoters = (df["Segment"] == "Promoter").sum()
passives = (df["Segment"] == "Passive").sum()
detractors = (df["Segment"] == "Detractor").sum()

nps = ((promoters - detractors) / total) * 100

# =========================
# KPI METRICS
# =========================
col1, col2, col3, col4 = st.columns(4)

col1.metric("📊 NPS Score", round(nps, 2))
col2.metric("😊 Promoters", promoters)
col3.metric("😐 Passives", passives)
col4.metric("😡 Detractors", detractors)

st.divider()

# =========================
# BUSINESS INSIGHT ENGINE
# =========================
st.subheader("🧠 Business Insights")

if nps > 50:
    st.success("Excellent customer experience. Scale operations 🚀")
elif nps > 0:
    st.warning("Moderate experience. Improvement needed ⚠️")
else:
    st.error("Poor experience. Immediate action required ❌")

# =========================
# SEGMENT CHART
# =========================
st.subheader("📊 Customer Segments")

fig1 = px.pie(df, names="Segment", hole=0.5)
st.plotly_chart(fig1, use_container_width=True)

# =========================
# CSAT DISTRIBUTION
# =========================
st.subheader("📈 CSAT Distribution")

fig2 = px.histogram(df, x="CSAT Score", nbins=5)
st.plotly_chart(fig2, use_container_width=True)

# =========================
# CHANNEL PERFORMANCE
# =========================
if "channel_name" in df.columns:
    st.subheader("📡 Channel Performance")

    channel = df.groupby("channel_name")["CSAT Score"].mean().reset_index()

    fig3 = px.bar(channel, x="channel_name", y="CSAT Score")
    st.plotly_chart(fig3, use_container_width=True)

    best_channel = channel.loc[channel["CSAT Score"].idxmax(), "channel_name"]
    worst_channel = channel.loc[channel["CSAT Score"].idxmin(), "channel_name"]

    st.info(f"🏆 Best Channel: {best_channel}")
    st.warning(f"⚠️ Worst Channel: {worst_channel}")

# =========================
# TOP AGENTS
# =========================
if "Agent_name" in df.columns:
    st.subheader("🏆 Top Agents")

    agents = df.groupby("Agent_name")["CSAT Score"].mean().sort_values(ascending=False).head(10)
    st.bar_chart(agents)

# =========================
# SIMPLE AI CHATBOT
# =========================
st.subheader("🤖 AI Analyst")

if "chat" not in st.session_state:
    st.session_state.chat = []

for msg in st.session_state.chat:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

query = st.chat_input("Ask: NPS, CSAT, agents, channels, insights...")

def ai_engine(q):
    q = q.lower()

    if "nps" in q:
        return f"Current NPS = {round(nps,2)}"

    if "promoter" in q:
        return f"Promoters = {promoters}"

    if "detractor" in q:
        return f"Detractors = {detractors}"

    if "channel" in q and "channel_name" in df.columns:
        best = df.groupby("channel_name")["CSAT Score"].mean().idxmax()
        return f"Best Channel = {best}"

    if "agent" in q and "Agent_name" in df.columns:
        top = df.groupby("Agent_name")["CSAT Score"].mean().idxmax()
        return f"Top Agent = {top}"

    if "summary" in q or "insight" in q:
        return f"Overall experience is {'GOOD 📈' if promoters > detractors else 'NEEDS IMPROVEMENT ⚠️'}"

    return "Ask about NPS, CSAT, agents, channels, or insights."

if query:
    st.session_state.chat.append({"role": "user", "content": query})

    with st.chat_message("user"):
        st.write(query)

    with st.chat_message("assistant"):
        response = ai_engine(query)
        st.write(response)

    st.session_state.chat.append({"role": "assistant", "content": response})

# =========================
# FINAL SUMMARY
# =========================
st.divider()

st.subheader("📌 Executive Summary")

st.info(f"""
NPS Score: {round(nps,2)}

Promoters: {promoters}  
Passives: {passives}  
Detractors: {detractors}

Business Status: {"Healthy Growth 📈" if promoters > detractors else "Needs Attention ⚠️"}
""")

# =========================
# DOWNLOAD REPORT
# =========================
st.download_button(
    "⬇ Download Report",
    df.to_csv(index=False),
    "CX_Report.csv",
    "text/csv"
)