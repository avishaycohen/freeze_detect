"""
small script to evalute freeze frames in a set of videos
get meta data from those videos and check if there is a sync
between the videos freeze-wise, which means the videos
have the same freeze frames in them.
"""
import argparse
import logging
from urllib.parse import urlparse
import requests
import sys
import os

# local imports
import freeze_utils

# setup options for script
parser = argparse.ArgumentParser(description='find frozen frames in videos from urls')

# urls we want to download and evalute
parser.add_argument('urls', metavar='U', type=str, nargs='+',
                   help='url for a video file to analyze')

# freeze detect specific options
parser.add_argument('-n' ,'--noise', type=float, metavar='N',
                    help='value of noise tolerance, between 0 and 1, default 0.001',
                    default=0.001)
parser.add_argument('-d' ,'--duration', type=int, metavar='D',
                    help='freeze duration until notification, default 2',
                    default=2)

# log level option
parser.add_argument('-v', '--verbose', help='more information in logs',
                    action='store_true')

args = parser.parse_args()

# setup logger options
log_level = logging.DEBUG if args.verbose else logging.INFO
logging.basicConfig(format='%(asctime)s %(message)s', level=log_level)

logging.info(f'user input arguments: {args}')

# verify actual mp4 urls
for url in args.urls:
    check = urlparse(url)
    if (check.scheme == '' and check.netloc == '') or url[-4:] != '.mp4':
        logging.error(f'url {url} is not valid, exiting vlaidator')
        sys.exit()

# create folder where we store the downloaded files
download_folder = '../videos'
if not os.path.exists(download_folder):
    os.makedirs(download_folder)

target_files = []

for url in args.urls:
    logging.debug(f'downloading file: {url}')
    file_name = url.split('/')[-1]
    # add to list of files
    target_files.append(download_folder + '/' + file_name)
    if os.path.exists(download_folder + '/' + file_name):
        logging.debug(f'file already exist on disk, skipping download')
        continue
    r = requests.get(url, allow_redirects=True)  # download
    with open(download_folder + '/' + file_name, 'wb') as download_file:
        download_file.write(r.content)  #save to file

logging.debug(f'total file paths: {target_files}')

metadata = {
    "all_videos_freeze_frame_synced": False,
    "videos": []
}

# start analyzing each file
for path in target_files:
    # run freeze detect
    output = freeze_utils.run_freeze_detect(path, args.noise, args.duration)
    logging.debug(output)
    # get video duration
    video_dur = freeze_utils.extract_duration(output)
    total_duration = freeze_utils.convert_duration_to_total_seconds(video_dur)
    logging.debug(f'total video duration: {total_duration}')
    # get start/lenght/end values of freezes
    video_stamps = freeze_utils.extract_timestamps(output)
    logging.debug(f'list of timestamps: {video_stamps}')
    list_of_valids, max_valid_period, total_freeze_time = freeze_utils.analyze_freeze_frames(video_stamps, total_duration)
    
    vid_metadata = {
        "longest_valid_period": max_valid_period,
        "valid_video_percentage": (total_duration - total_freeze_time) / total_duration * 100,
        "valid_periods": list_of_valids
    }

    logging.debug(f'video: {path} metadata: {vid_metadata}')