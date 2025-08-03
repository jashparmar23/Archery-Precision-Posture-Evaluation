# analyze_anchor_point.py
import json
import numpy as np
import matplotlib.pyplot as plt
import os
import sys

def analyze_anchor_point(json_path, save_plot=False, output_dir="output/plots/"):
    with open(json_path, 'r') as f:
        data = json.load(f)

    distances = []
    valid_frames = []

    for frame in data:
        kp = frame['keypoints']

        try:
            right_hand = kp['landmark_16']  # Right wrist
            nose = kp['landmark_0']         # Nose (approximate head center)
        except KeyError:
            continue

        if right_hand['visibility'] < 0.7 or nose['visibility'] < 0.7:
            continue

        dx = right_hand['x'] - nose['x']
        dy = right_hand['y'] - nose['y']
        distance = np.sqrt(dx**2 + dy**2)

        distances.append(distance)
        valid_frames.append(frame['frame'])

    if not distances:
        print(f"No valid data in {json_path}")
        return

    mean_dist = np.mean(distances)
    std_dev = np.std(distances)

    # Plot
    plt.figure(figsize=(10, 4))
    plt.plot(valid_frames, distances, label="Anchor Point Distance (normalized units)")
    plt.axhline(y=mean_dist, color='gray', linestyle='--', label=f"Mean = {mean_dist:.4f}")
    plt.title("Anchor Point Consistency (Wrist-to-Nose Distance)")
    plt.xlabel("Frame")
    plt.ylabel("Distance")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    if save_plot:
        os.makedirs(output_dir, exist_ok=True)
        filename = os.path.join(output_dir, os.path.basename(json_path).replace(".json", "_anchor_plot.png"))
        plt.savefig(filename)
        print(f"Saved anchor plot to {filename}")
    else:
        plt.show()

    print(f"Anchor consistency: mean distance = {mean_dist:.4f}, std deviation = {std_dev:.4f}")

if __name__ == "__main__":
    json_file = sys.argv[1]
    analyze_anchor_point(json_file, save_plot=True)
