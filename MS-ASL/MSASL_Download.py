import json
import os
import subprocess
import argparse

parser = argparse.ArgumentParser(
    prog='MSASL_Download.py',
    description='Download and preprocess the MS-ASL dataset'
)
parser.add_argument('-m', '--mode', required=True, choices=['train', 'test', 'val'], help='Mode of the dataset to download (train/test/val)')
mode = parser.parse_args().mode

# default value
# mode = 'test'

# Load the JSON data
with open(f'MSASL_{mode}.json', 'r') as file:
    data = json.load(file)

# get list of failed downloads, skip if failed
with open(f'failed_downloads_{mode}.json', 'r') as file:
    failed_videos = json.load(file)
    
failed_urls = set([video['url'] for video in failed_videos])

failed_downloads = [{'url': item['url'], 'label': item['label']} for item in failed_videos]

filtered_data = [item for item in data if item['url'] not in failed_urls]
# print(filtered_data[::10])


# Create a directory to store the downloaded videos
os.makedirs(f'data/{mode}', exist_ok=True)
dir = f'data/{mode}'
# failed_downloads = []

# completed downloads: to avoid repeated downloads

completed_downloads = set()
with os.scandir("temp/") as entries:
    for entry in entries:
        if entry.is_file():
            completed_downloads.add(entry.name.split('.')[0])

# Function to download and preprocess video
def download_and_preprocess(video_info, dir):
    url = video_info['url']
    start_time = video_info['start_time']
    end_time = video_info['end_time']
    label = video_info['label']
    video_id = url.split('=')[-1]
    output_filename = f"temp/{video_id}"
    # print(output_filename)
    # Download the video using yt-dlp
    # downloads the file only once to avoid repeated downloads
    if video_id not in completed_downloads:
            # '--cookies-from-browser', 'firefox',
        download_command = [
            'yt-dlp',
            '-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',
            '-o', output_filename,
            url
        ]
        try:
            subprocess.run(download_command, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Failed to download {url}: {e}")
            failed_downloads.append({'url': url, 'label': label})
            return
    else:
        print(video_id, end=' ')
        print("already downloaded, skipping.")
    completed_downloads.add(video_id)

    # Trim and preprocess the video
    trim_command = [
        'ffmpeg',
        '-hide_banner', '-loglevel', 'panic',
        '-n',
        '-i', output_filename + '.mp4',
        '-ss', str(start_time),
        '-to', str(end_time),
        '-vf', 'scale=480:-1,fps=30',
        '-c:v', 'libx264',
        '-preset', 'fast',
        '-crf', '22',
        '-c:a', 'aac',
        '-b:a', '128k',
        '-threads', '10',
        f'{dir}/{label}_{video_id}_{start_time}.mp4'
    ]
    subprocess.run(trim_command)

    # Remove the original downloaded video
    # os.remove(output_filename + '.mp4')

# Load existing failed downloads
if os.path.exists(f'failed_downloads_{mode}.json'):
    # with open('failed_downloads.json', 'r') as file:
        # try:
        #     existing_failed_downloads = json.load(file)
        # except json.JSONDecodeError:
        #     existing_failed_downloads = []
    # Iterate over each video info in the JSON data
    counter = 0
    try:
        for video_info in filtered_data:
            download_and_preprocess(video_info, dir)
            counter += 1
            if(counter % 20 == 0):
                with open(f'failed_downloads_{mode}.json', 'w') as file:
                    json.dump(failed_downloads, file, indent=4)
    except:
        print("Interrupted, cleaning. writing data.")
        with open(f'failed_downloads_{mode}.json', 'w') as file:
                json.dump(failed_downloads, file, indent=4)