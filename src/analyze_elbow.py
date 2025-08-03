import json
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
from utils import calculate_angle

def analyze_elbow_angle(json_path, save_plot=False, output_dir="output/plots/"):
    with open(json_path, 'r') as f:
        data = json.load(f)

    angles = []
    valid_frames = []

    for frame in data:
        kp = frame['keypoints']

        try:
            shoulder = kp['landmark_12']
            elbow = kp['landmark_14']
            wrist = kp['landmark_16']
        except KeyError:
            continue

        if min(shoulder['visibility'], elbow['visibility'], wrist['visibility']) < 0.7:
            continue

        angle = calculate_angle(shoulder, elbow, wrist)
        angles.append(angle)
        valid_frames.append(frame['frame'])

    plt.figure(figsize=(10, 4))
    plt.plot(valid_frames, angles, label="Elbow Angle (°)")
    plt.axhline(y=180, color='gray', linestyle='--', label='Ideal = 180° (fully extended)')
    plt.title("Draw Arm Elbow Angle Across Frames")
    plt.xlabel("Frame")
    plt.ylabel("Angle (degrees)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    if save_plot:
        os.makedirs(output_dir, exist_ok=True)
        filename = os.path.join(output_dir, os.path.basename(json_path).replace(".json", "_elbow_plot.png"))
        plt.savefig(filename)
        print(f"Saved plot to {filename}")
    else:
        plt.show()

if __name__ == "__main__":
    json_file = sys.argv[1]
    analyze_elbow_angle(json_file, save_plot=True)