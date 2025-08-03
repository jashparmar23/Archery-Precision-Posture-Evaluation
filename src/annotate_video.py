import cv2
import json
import numpy as np
import os
import sys
from utils import calculate_angle

POSE_PAIRS = [
    (11, 12), (12, 14), (14, 16),
    (11, 13), (13, 15),
    (11, 23), (12, 24),
]

def draw_skeleton(frame, landmarks, width, height):
    for a, b in POSE_PAIRS:
        if f'landmark_{a}' in landmarks and f'landmark_{b}' in landmarks:
            pt1 = landmarks[f'landmark_{a}']
            pt2 = landmarks[f'landmark_{b}']
            if pt1['visibility'] > 0.7 and pt2['visibility'] > 0.7:
                x1, y1 = int(pt1['x'] * width), int(pt1['y'] * height)
                x2, y2 = int(pt2['x'] * width), int(pt2['y'] * height)
                cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
    return frame

def annotate_video(video_path, json_path, output_path):
    cap = cv2.VideoCapture(video_path)
    with open(json_path, 'r') as f:
        pose_data = json.load(f)

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # fallback that always works locally


    width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps    = cap.get(cv2.CAP_PROP_FPS)

    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    # Estimate anchor point mean distance
    anchor_distances = []
    for frame_data in pose_data:
        kp = frame_data['keypoints']
        if 'landmark_0' in kp and 'landmark_16' in kp:
            nose = kp['landmark_0']
            wrist = kp['landmark_16']
            if nose['visibility'] > 0.7 and wrist['visibility'] > 0.7:
                dx = wrist['x'] - nose['x']
                dy = wrist['y'] - nose['y']
                anchor_distances.append(np.sqrt(dx**2 + dy**2))

    anchor_mean = np.mean(anchor_distances) if anchor_distances else 0
    anchor_std = np.std(anchor_distances) if anchor_distances else 0

    for frame_data in pose_data:
        ret, frame = cap.read()
        if not ret:
            break

        kp = frame_data['keypoints']
        frame_id = frame_data['frame']

        frame = draw_skeleton(frame, kp, width, height)

        try:
            a = kp['landmark_12']
            b = kp['landmark_14']
            c = kp['landmark_16']
            if min(a['visibility'], b['visibility'], c['visibility']) > 0.7:
                elbow_angle = int(calculate_angle(a, b, c))
                cv2.putText(frame, f"Elbow: {elbow_angle}°", (30, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
                if elbow_angle < 160:
                    cv2.putText(frame, "Extend Draw Arm!", (30, 80),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
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
                shoulder_angle = int(np.degrees(np.arctan2(dy, dx)))
                cv2.putText(frame, f"Shoulder: {shoulder_angle}°", (30, 110),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
                if abs(shoulder_angle) > 10:
                    cv2.putText(frame, "Shoulder Tilt!", (30, 140),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        except:
            pass

        # Anchor point drift detection
        try:
            nose = kp['landmark_0']
            wrist = kp['landmark_16']
            if nose['visibility'] > 0.7 and wrist['visibility'] > 0.7:
                dx = wrist['x'] - nose['x']
                dy = wrist['y'] - nose['y']
                dist = np.sqrt(dx**2 + dy**2)
                if abs(dist - anchor_mean) > (1.5 * anchor_std):
                    cv2.putText(frame, "Anchor Drift!", (30, 170),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        except:
            pass

        out.write(frame)

    cap.release()
    out.release()
    print(f"[✔] Saved annotated video to: {output_path}")

if __name__ == "__main__":
    video_file = sys.argv[1]
    json_file = sys.argv[2]
    output_file = sys.argv[3]
    annotate_video(video_file, json_file, output_file)