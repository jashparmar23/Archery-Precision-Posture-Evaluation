import json
import numpy as np
import os
from utils import calculate_angle

def generate_feedback(json_path, output_dir="output/reports/"):
    with open(json_path, 'r') as f:
        data = json.load(f)

    elbow_angles = []
    shoulder_angles = []
    anchor_distances = []

    for frame in data:
        kp = frame['keypoints']

        # Elbow
        try:
            shoulder = kp['landmark_12']
            elbow = kp['landmark_14']
            wrist = kp['landmark_16']
            if min(shoulder['visibility'], elbow['visibility'], wrist['visibility']) > 0.7:
                elbow_angles.append(calculate_angle(shoulder, elbow, wrist))
        except:
            pass

        # Shoulder
        try:
            left = kp['landmark_11']
            right = kp['landmark_12']
            if min(left['visibility'], right['visibility']) > 0.7:
                if left['x'] > right['x']:
                    left, right = right, left
                dx = right['x'] - left['x']
                dy = right['y'] - left['y']
                shoulder_angle = np.degrees(np.arctan2(dy, dx))
                shoulder_angles.append(shoulder_angle)
        except:
            pass

        # Anchor point
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

    # Summary Stats
    elbow_extended_ratio = np.mean([angle > 160 for angle in elbow_angles]) if elbow_angles else 0
    shoulder_mean = np.mean(shoulder_angles) if shoulder_angles else 0
    shoulder_std = np.std(shoulder_angles) if shoulder_angles else 0
    anchor_std = np.std(anchor_distances) if anchor_distances else 0

    # Feedback generation
    lines = []
    lines.append(f"File: {os.path.basename(json_path)}")
    lines.append(f"Frames analyzed: {len(data)}\n")

    lines.append(f"[Elbow]")
    lines.append(f"- % of frames with full extension: {elbow_extended_ratio * 100:.1f}%")
    lines.append(f"- Threshold: >160° is considered extended\n")

    lines.append(f"[Shoulder]")
    lines.append(f"- Mean shoulder alignment angle: {shoulder_mean:.2f}°")
    lines.append(f"- Tilt variability (std dev): {shoulder_std:.2f}°\n")

    lines.append(f"[Anchor Point]")
    lines.append(f"- Anchor stability (std dev): {anchor_std:.4f}")
    if anchor_std > 0.025:
        lines.append(f"- ⚠ Inconsistent anchor point! Try to fix draw hand closer to chin.\n")
    else:
        lines.append(f"- ✓ Good anchor consistency.\n")

    # Save
    os.makedirs(output_dir, exist_ok=True)
    report_path = os.path.join(output_dir, os.path.basename(json_path).replace(".json", "_feedback.txt"))
    with open(report_path, 'w', encoding='utf-8') as f:  # <- FIXED HERE
        f.write('\n'.join(lines))

    print(f"[✔] Saved feedback report to: {report_path}")

if __name__ == "__main__":
    import sys
    json_file = sys.argv[1]
    generate_feedback(json_file)
