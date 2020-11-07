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

for url in args.urls:
    logging.debug(f'downloading file: {url}')
    file_name = url.split('/')[-1]
    if os.path.exists(download_folder + '/' + file_name):
        logging.debug(f'file already exist on disk, skipping download')
        continue
    r = requests.get(url, allow_redirects=True)  # download
    with open(download_folder + '/' + file_name, 'wb') as download_file:
        download_file.write(r.content)  #save to file
