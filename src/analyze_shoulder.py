import json
import numpy as np
import matplotlib.pyplot as plt
import os
import sys

def get_shoulder_angle(kp_left, kp_right):
    delta_y = kp_right['y'] - kp_left['y']
    delta_x = kp_right['x'] - kp_left['x']
    angle_rad = np.arctan2(delta_y, delta_x)
    return np.degrees(angle_rad)

def analyze_shoulder_alignment(json_path, save_plot=False, output_dir="output/plots/"):
    with open(json_path, 'r') as f:
        data = json.load(f)

    angles = []
    valid_frames = []

    for frame in data:
        kp = frame['keypoints']

        if 'landmark_11' not in kp or 'landmark_12' not in kp:
            continue

        left = kp['landmark_11']
        right = kp['landmark_12']

        if left['visibility'] < 0.7 or right['visibility'] < 0.7:
            continue

        if left['x'] > right['x']:
            left, right = right, left

        angle = get_shoulder_angle(left, right)
        angles.append(angle)
        valid_frames.append(frame['frame'])

    angles = np.unwrap(np.radians(angles))
    angles = np.degrees(angles)

    plt.figure(figsize=(10, 4))
    plt.plot(valid_frames, angles, label="Shoulder Angle (°)")
    plt.axhline(y=0, color='gray', linestyle='--', label='Ideal = 0°')
    plt.title("Shoulder Alignment Across Frames")
    plt.xlabel("Frame")
    plt.ylabel("Angle (degrees)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    if save_plot:
        os.makedirs(output_dir, exist_ok=True)
        filename = os.path.join(output_dir, os.path.basename(json_path).replace(".json", "_shoulder_plot.png"))
        plt.savefig(filename)
        print(f"Saved plot to {filename}")
    else:
        plt.show()

if __name__ == "__main__":
    json_file = sys.argv[1]
    analyze_shoulder_alignment(json_file, save_plot=True)