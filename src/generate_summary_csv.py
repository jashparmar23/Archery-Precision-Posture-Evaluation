# generate_summary_csv.py
import os
import json
import numpy as np
import csv
from utils import calculate_angle

def extract_metrics(json_path):
    with open(json_path, 'r') as f:
        data = json.load(f)

    elbow_angles = []
    shoulder_angles = []
    anchor_distances = []

    for frame in data:
        kp = frame['keypoints']

        try:
            a = kp['landmark_12']
            b = kp['landmark_14']
            c = kp['landmark_16']
            if min(a['visibility'], b['visibility'], c['visibility']) > 0.7:
                elbow_angles.append(calculate_angle(a, b, c))
        except:
            pass

        try:
            l = kp['landmark_11']
            r = kp['landmark_12']
            if min(l['visibility'], r['visibility']) > 0.7:
                if l['x'] > r['x']:
                    l, r = r, l
                dx = r['x'] - l['x']
                dy = r['y'] - l['y']
                shoulder_angle = np.degrees(np.arctan2(dy, dx))
                shoulder_angles.append(shoulder_angle)
        except:
            pass

        try:
            nose = kp['landmark_0']
            wrist = kp['landmark_16']
            if min(nose['visibility'], wrist['visibility']) > 0.7:
                dx = wrist['x'] - nose['x']
                dy = wrist['y'] - nose['y']
                dist = np.sqrt(dx**2 + dy**2)
                anchor_distances.append(dist)
        except:
            pass

    elbow_ratio = np.mean([angle > 160 for angle in elbow_angles]) * 100 if elbow_angles else 0
    shoulder_mean = np.mean(shoulder_angles) if shoulder_angles else 0
    shoulder_std = np.std(shoulder_angles) if shoulder_angles else 0
    anchor_std = np.std(anchor_distances) if anchor_distances else 0

    anchor_flag = "Drift Detected" if anchor_std > 0.025 else "Good"

    return [
        elbow_ratio,
        shoulder_mean,
        shoulder_std,
        anchor_std,
        anchor_flag
    ]

def generate_csv_summary(pose_folder="data/poses", output_path="output/reports/summary.csv"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    rows = [["Video", "ElbowExtended%", "ShoulderMean", "ShoulderStd", "AnchorStd", "AnchorFlag"]]

    for file in sorted(os.listdir(pose_folder)):
        if file.endswith(".json"):
            path = os.path.join(pose_folder, file)
            metrics = extract_metrics(path)
            rows.append([file.replace(".json", ".mp4")] + metrics)

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(rows)

    print(f"[✔] Summary CSV saved to: {output_path}")

if __name__ == "__main__":
    generate_csv_summary()