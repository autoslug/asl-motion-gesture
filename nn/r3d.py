import torch
import torchvision.models as models
import cv2
import numpy as np
import torchvision.transforms as transforms
import json

model = models.video.r3d_18(pretrained=True)
model.eval()

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

def preprocess_video(video_path, num_frames=16):
    cap = cv2.VideoCapture(video_path)
    frames = []

    transform = transforms.Compose([
        transforms.ToPILImage(),
        transforms.ToTensor()
    ])

    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    step = max(1, frame_count // num_frames)

    for i in range(num_frames):
        cap.set(cv2.CAP_PROP_POS_FRAMES, i * step)
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = transform(frame)
        frames.append(frame)

    cap.release()

    if len(frames) < num_frames:
        for _ in range(num_frames - len(frames)):
            frames.append(frames[-1])  

    video_tensor = torch.stack(frames).permute(1, 10, 640, 640)  # (C, T, H, W)
    return video_tensor.unsqueeze(0)  # Add batch dimension (1, C, T, H, W)

def predict_video(model, video_path, labels_path="MSASL_classes.json"):
    
    with open(labels_path, 'r') as ls:
        labels = json.load(ls)

    video_tensor = preprocess_video(video_path).to(device)

    with torch.no_grad():
        output = model(video_tensor)
    
    probabilities = torch.nn.functional.softmax(output[0], dim=0)
    top3_prob, top3_classes = torch.topk(probabilities, 3)

    print("\nTop 3 Predictions:")
    for i in range(3):
        print(f"{labels[top3_classes[i]]}: {top3_prob[i].item():.4f}")

video_path = "example.mp4"
predict_video(model, video_path)


