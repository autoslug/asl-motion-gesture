import torch
import os
from torch.utils.data import Dataset
from torchvision.transforms import ToTensor
from torchvision.io import read_video
import json
        
MAX_FRAMES = 270
    
class MSASLDataset(Dataset):
    def __init__(self, metadata_file, video_dir, transform=None):
        with open(metadata_file, 'r') as f:
            self.metadata = json.load(f)
        self.video_dir = video_dir # base directory for videos
        self.transform = transform
    
    def __len__(self):
        return len(self.metadata)
    
    def _pad_video(video_tensor):
        # C: color channels
        # T: number of frames
        # H: height
        # W: width
        C, T, H, W = video_tensor.shape
        if T < MAX_FRAMES:
            pad = torch.zeros((C, MAX_FRAMES - T, H, W))
            video_tensor = torch.cat([video_tensor, pad], dim=1)
        return video_tensor
    
    def __getitem__(self, idx):
        data = self.metadata[idx]
        file_name = data['file_name']
        video = self.load_video(file_name)
        label = data['label']
        
        if self.transform:
            video = self.transform(video)
            
        sample = {
            'video': video,
            'label': torch.tensor(data['label'], dtype=torch.int16),
            'box': torch.tensor(data['box'], dtype=torch.float32),
            'url': torch.tensor(data['url'], dtype=torch.string)
        }
        return sample
    
    def load_video(self, file_name):
        video_path = os.path.join(self.video_dir, file_name)
        video = read_video(video_path)
        
        padded_video = self._pad_video(video)
        
        return padded_video
        
        
        
# max_frame_length = 0
# with open('./../MS-ASL/MSASL_train.json', 'r') as f:
#     data = json.load(f)
#     # for item in data:
#     max_frame_length = max([item['end'] - item['start'] for item in data])
#     print(max_frame_length)
# with open('./../MS-ASL/MSASL_test.json', 'r') as f:
#     data = json.load(f)
#     max_frame_length = max([item['end'] - item['start'] for item in data])
#     print(max_frame_length)
# with open('./../MS-ASL/MSASL_val.json', 'r') as f:
#     data = json.load(f)
#     max_frame_length = max([item['end'] - item['start'] for item in data])
#     print(max_frame_length)