import streamlit as st
import pandas as pd
import os
from PIL import Image

st.set_page_config(page_title="Archery Analysis Dashboard", layout="wide")
st.title("🏹 Archery AI Analysis Dashboard")

# Paths
summary_csv = "output/reports/summary.csv"
reports_dir = "output/reports"
plots_dir = "output/plots"
videos_dir = "output/annotated_videos"

# Load summary CSV
if not os.path.exists(summary_csv):
    st.error("❌ Summary CSV not found. Run the pipeline first.")
    st.stop()

df = pd.read_csv(summary_csv)
st.dataframe(df, use_container_width=True)

# Strip '.mp4' to match other filenames
video_names = df["Video"].str.replace(".mp4", "", regex=False)
selected_video = st.selectbox("🎯 Select a video for detailed report:", video_names.tolist())

if selected_video:
    st.markdown(f"### 🔍 Details for `{selected_video}`")

    col1, col2 = st.columns(2)

    # ---- Plots ----
    shoulder_plot = os.path.join(plots_dir, f"{selected_video}_shoulder_plot.png")
    elbow_plot = os.path.join(plots_dir, f"{selected_video}_elbow_plot.png")

    if os.path.exists(shoulder_plot):
        col1.image(shoulder_plot, caption="Shoulder Alignment", use_container_width=True)
    else:
        col1.warning("Shoulder plot not found.")

    if os.path.exists(elbow_plot):
        col2.image(elbow_plot, caption="Draw Arm Elbow Angle", use_container_width=True)
    else:
        col2.warning("Elbow plot not found.")

    # ---- Feedback ----
    feedback_file = os.path.join(reports_dir, f"{selected_video}_feedback.txt")
    if os.path.exists(feedback_file):
        with open(feedback_file, "r", encoding="utf-8") as f:
            feedback = f.read()
        st.subheader("📝 Feedback Report")
        st.text(feedback)
    else:
        st.warning("Feedback report not found.")

    # ---- Annotated Video ----
    video_path = os.path.join(videos_dir, f"{selected_video}_fixed.mp4")
    side_by_side_path = os.path.join("output", "side_by_side", f"{selected_video}_side_by_side_fixed.mp4")

    st.subheader("🎥 Annotated Video")
    if os.path.exists(video_path):
        with open(video_path, "rb") as v:
            st.video(v.read())
    else:
        st.warning("Annotated video not found.")

    # ---- Side-by-Side Comparison Video ----
    st.subheader("🆚 Side-by-Side: Before vs Ideal")
    if os.path.exists(side_by_side_path):
        with open(side_by_side_path, "rb") as v:
            st.video(v.read())
    else:
        st.warning("Side-by-side comparison video not found.")



st.markdown("---")
st.caption("Built with ❤️ by Future Sportler Candidate")
