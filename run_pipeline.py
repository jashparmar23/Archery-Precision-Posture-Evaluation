import os
import subprocess

video_dir = "data/videos"
pose_dir = "data/poses"
plot_dir = "output/plots"
annotated_dir = "output/annotated_videos"

os.makedirs(pose_dir, exist_ok=True)
os.makedirs(plot_dir, exist_ok=True)
os.makedirs(annotated_dir, exist_ok=True)

# List all mp4 videos
video_files = [f for f in os.listdir(video_dir) if f.endswith(".mp4")]
video_files.sort()  # Ensures consistent order

for video_file in video_files:
    name = os.path.splitext(video_file)[0]
    video_path = os.path.join(video_dir, video_file)
    json_path = os.path.join(pose_dir, f"{name}.json")
    annotated_path = os.path.join(annotated_dir, f"{name}_annotated.mp4")

    print(f"\n▶ Processing {video_file}...")

    # 1. Extract pose keypoints if not already done
    if not os.path.exists(json_path):
        print("🧠 Extracting keypoints...")
        subprocess.run(["python", "src/extract_keypoints.py", video_path, json_path])
    else:
        print("✅ Pose data exists.")

    # 2. Analyze Shoulder
    print("📐 Analyzing shoulder...")
    subprocess.run(["python", "src/analyze_shoulder.py", json_path])

    # 3. Analyze Elbow
    print("📐 Analyzing elbow...")
    subprocess.run(["python", "src/analyze_elbow.py", json_path])

    # 4. Analyze Anchor Point
    print("🎯 Analyzing anchor point consistency...")
    subprocess.run(["python", "src/analyze_anchor_point.py", json_path])

    # 5. Annotate video
    print("🎥 Annotating video...")
    subprocess.run(["python", "src/annotate_video.py", video_path, json_path, annotated_path])

    # 5.5 Re-encode for browser compatibility using FFmpeg
    fixed_path = annotated_path.replace("_annotated.mp4", "_fixed.mp4")
    print("🔁 Re-encoding for browser playback...")
    subprocess.run([
        "ffmpeg", "-y", "-i", annotated_path,
        "-vcodec", "libx264", "-acodec", "aac",
        fixed_path
    ])


    # 6. Generate feedback report
    print("📝 Generating feedback report...")
    subprocess.run(["python", "src/generate_feedback.py", json_path])

# 7. Generate summary CSV for all videos
print("\n📊 Generating summary CSV...")
subprocess.run(["python", "src/generate_summary_csv.py"])

# 8. Generate HTML report
print("\n🌐 Generating HTML report...")
subprocess.run(["python", "src/generate_summary_html.py"])


print("\n✅ Batch processing complete!")
