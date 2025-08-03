import json
import numpy as np
import matplotlib.pyplot as plt

def get_shoulder_angle(kp_left, kp_right):
    delta_y = kp_right['y'] - kp_left['y']
    delta_x = kp_right['x'] - kp_left['x']
    angle_rad = np.arctan2(delta_y, delta_x)
    angle_deg = np.degrees(angle_rad)
    return angle_deg

def analyze_shoulder_alignment(json_path):
    with open(json_path, 'r') as f:
        data = json.load(f)

    angles = []
    for frame in data:
        kp = frame['keypoints']
        if 'landmark_11' in kp and 'landmark_12' in kp:
            angle = get_shoulder_angle(kp['landmark_11'], kp['landmark_12'])
            angles.append(angle)

    # Plot over time
    plt.figure(figsize=(10, 4))
    plt.plot(angles, label="Shoulder Angle (°)")
    plt.axhline(y=0, color='gray', linestyle='--', label='Ideal = 0°')
    plt.title("Shoulder Alignment Across Frames")
    plt.xlabel("Frame")
    plt.ylabel("Angle (degrees)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# Run this:
analyze_shoulder_alignment("data/poses/Video-1.json")
