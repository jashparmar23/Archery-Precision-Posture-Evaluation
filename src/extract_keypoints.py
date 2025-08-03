import cv2
import mediapipe as mp
import json
import os
import sys

mp_pose = mp.solutions.pose

def extract_pose_from_video(video_path, output_path):
    cap = cv2.VideoCapture(video_path)
    pose = mp_pose.Pose(static_image_mode=False, model_complexity=2)

    frame_data = []
    frame_id = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image_rgb)

        keypoints = {}
        if results.pose_landmarks:
            for i, lm in enumerate(results.pose_landmarks.landmark):
                keypoints[f'landmark_{i}'] = {
                    'x': lm.x,
                    'y': lm.y,
                    'z': lm.z,
                    'visibility': lm.visibility
                }
        frame_data.append({"frame": frame_id, "keypoints": keypoints})
        frame_id += 1

    with open(output_path, 'w') as f:
        json.dump(frame_data, f, indent=2)

    cap.release()
    pose.close()
    print(f"Saved keypoints to {output_path}")

if __name__ == "__main__":
    video_path = sys.argv[1]
    output_path = sys.argv[2]
    extract_pose_from_video(video_path, output_path)