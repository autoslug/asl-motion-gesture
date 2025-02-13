apt update && apt upgrade -y && apt install -y git python3 pip ffmpeg tmux
python3 -m pip install -U "yt-dlp[default]"
python3 -m pip install tqdm
# tmux
cd /root/dataset/asl-motion-gesture/
# git pull
cd MS-ASL
python3 MSASL_Download.py -m "test"
python3 MSASL_Download.py -m "train"
python3 MSASL_Download.py -m "val"
