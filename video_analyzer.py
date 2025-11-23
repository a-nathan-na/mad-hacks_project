"""
Video Analyzer Module

Analyzes video files using YOLOv8 to detect people, cars, and weapons.
Returns statistics about detected objects and annotated frames.
"""

from typing import Dict, Any, List
import numpy as np
import cv2
from ultralytics import YOLO
import os


def analyze_video(video_path: str, frame_rate: int = 1) -> Dict[str, Any]:
    """
    Analyze a video file to detect people, cars, and weapons.
    
    Args:
        video_path: Path to the video file
        frame_rate: Number of frames per second to sample (default: 1 fps)
    
    Returns:
        Dictionary containing:
        - people: Maximum number of people detected across all frames
        - cars: Maximum number of cars/vehicles detected across all frames
        - weapon_present: True if any weapon-like object found in any frame
        - frames: List of annotated frames (numpy arrays) with detections drawn
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
    
    # Initialize YOLOv8 model with pretrained weights
    # This will download weights automatically on first run
    model = YOLO('yolov8n.pt')  # Using nano version for speed; can use 'yolov8s.pt' or 'yolov8m.pt' for better accuracy
    
    # Open video file
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Could not open video file: {video_path}")
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    if fps <= 0:
        raise ValueError("Invalid video: unable to determine FPS")
    
    # Calculate frame interval based on desired frame_rate
    frame_interval = max(1, int(fps / frame_rate))
    
    # Track maximum counts across all frames
    max_people = 0
    max_cars = 0
    weapon_present = False
    
    # Store annotated frames for visualization (limit to 3 frames)
    annotated_frames = []
    
    frame_count = 0
    processed_count = 0
    frames_to_save = []
    
    # YOLO COCO class IDs:
    # person = 0
    # car = 2, motorcycle = 3, bus = 5, truck = 7
    # knife = 76 (if present in model)
    # gun/firearm detection may need custom model, but we'll try knife as proxy
    
    person_class_ids = [0]
    vehicle_class_ids = [2, 3, 5, 7]  # car, motorcycle, bus, truck
    
    # Note: Standard YOLOv8 doesn't detect guns reliably. We'll check for knife (76) 
    # and look for suspicious objects. For MVP, this is a limitation.
    weapon_class_ids = [76]  # knife - main weapon class in COCO
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Process frame at specified interval
        if frame_count % frame_interval == 0:
            # Run YOLO detection
            results = model(frame, verbose=False)
            
            # Get detections from first result (single frame)
            detections = results[0]
            
            # Count objects
            people_count = 0
            cars_count = 0
            has_weapon = False
            
            # Process detections
            if detections.boxes is not None:
                for box in detections.boxes:
                    cls_id = int(box.cls[0])
                    conf = float(box.conf[0])
                    
                    # Only count high-confidence detections (>0.5)
                    if conf < 0.5:
                        continue
                    
                    if cls_id in person_class_ids:
                        people_count += 1
                    elif cls_id in vehicle_class_ids:
                        cars_count += 1
                    elif cls_id in weapon_class_ids:
                        has_weapon = True
            
            # Update maximum counts
            max_people = max(max_people, people_count)
            max_cars = max(max_cars, cars_count)
            if has_weapon:
                weapon_present = True
            
            # Store annotated frame for later selection
            annotated_frame = detections.plot()
            frames_to_save.append(annotated_frame)
            
            processed_count += 1
        
        frame_count += 1
    
    cap.release()
    
    # Select up to 3 frames evenly spaced from processed frames
    if len(frames_to_save) > 0:
        if len(frames_to_save) <= 3:
            annotated_frames = frames_to_save
        else:
            # Select evenly spaced frames (first, middle, last)
            step = len(frames_to_save) // 3
            annotated_frames = [
                frames_to_save[0],
                frames_to_save[len(frames_to_save) // 2],
                frames_to_save[-1]
            ]
    else:
        # Fallback: re-analyze first frame if no frames were processed
        cap = cv2.VideoCapture(video_path)
        ret, frame = cap.read()
        if ret:
            results = model(frame, verbose=False)
            annotated_frame = results[0].plot()
            annotated_frames.append(annotated_frame)
        cap.release()
    
    return {
        "people": max_people,
        "cars": max_cars,
        "weapon_present": weapon_present,
        "frames": annotated_frames
    }

