"""
this file hold a bunch of static functions
that are used in the main script.
they are standalone and can be re-used in different context
when ffmpeg freeze detect is needed.
"""
from datetime import datetime
import itertools
import re
import subprocess


def run_freeze_detect(path, n=0.003, d=2):
    """
    get a path to mp4 file and run ffmpeg freeze detect on it
    args:
        path, str, path to target video
        n, noise tolerance value. defaults to 0.003
        d, freeze duration until notification, defaults to 2
    returns:
        byte_str, output of running ffmpeg freeze detect filter on <path> video
    """
    freeze_cmd = f'ffmpeg -i {path} -vf freezedetect=n={n}:d={d} -map 0:v:0 -f null -'
    out = subprocess.check_output(freeze_cmd.split(' '), stderr=subprocess.STDOUT)
    return out


def extract_duration(ffmpeg_output):
    """
    get ffmpeg output and check for total video duration in it.
    args:
        ffmpeg_output, bytes, output of freeze detect filter on video file
    returns:
        str, H:M:S.ms formatted total duration of video
    """
    duration_regex = r'Duration: (\d+:\d+:\d+.\d+)'
    total_duration = re.findall(duration_regex, ffmpeg_output.decode('utf-8'))
    return total_duration[0]


def extract_timestamps(ffmpeg_output):
    """
    retrieve start and end times of freeze frames from ffmpeg output
    args:
        ffmpeg_output, bytes, output of freeze detect filter on video file
    returns:
        list of tuples, each tuple is (freeze_start|freeze_end|freeze_duration, time_stamp)
        time_stamp is a str type.
    """
    timestamps_regex = r'(freeze_start|freeze_end|freeze_duration): (\d+\.\d+)'
    return re.findall(timestamps_regex, ffmpeg_output.decode('utf-8'))


def convert_duration_to_total_seconds(duration):
    """
    utility to convert string in format "H:M:S.ML"
    into a total seconds float value
    args:
        duration, str, string from ffmepg result
    returns:
        float, total seconds from string format
    """
    breakdown = datetime.strptime(duration,'%H:%M:%S.%f')
    return (breakdown.microsecond/1000000 + breakdown.second + breakdown.minute*60 + breakdown.hour*3600)


def analyze_freeze_frames(stamps, total):
    """
    use the timestamps from output to:
        1. create a list of lists that contains the valid video periods
        2. get the longest period of valid video
        3. total of freeze duration
    args:
        stamps, list of tuples, output of extract_timestamps
        total, float, total duration of video
    returns: (tuple of)
        list of lists, each contains only 2 values, start and end of valid segment
        float, longest period of valid video
    """
    curr = 0
    curr_max = 0
    total_freeze = 0
    all_valids = []
    for item in stamps:
        if item[0] == 'freeze_duration':
            total_freeze += float(item[1])
            continue
        if item[0] == 'freeze_start' and float(item[1]) != 0:
            all_valids.append([curr, float(item[1])])
            if float(item[1]) - curr > curr_max:
                curr_max = float(item[1]) - curr
        else:
            curr = float(item[1])
    if stamps[-1][0] == 'freeze_end' and float(item[1]) != total:
        all_valids.append([curr, total])
        if float(item[1]) - curr > curr_max:
            curr_max = float(item[1]) - curr

    return all_valids, curr_max, total_freeze


def check_if_synced(lists):
    """
    get multiple lists of start and end values and check if they are
    considered synced (diff of up to 0.5 second)
    args:
        lists, list of lists, each item in sublist is two float numbers, start and end
    returns: bool,
        true if lists are synced
        false if at least one comparision result in value bigger then 0.5        
    """
    is_synced = True
    # create a tuple of all first period values (start, end), etc.
    for tup in zip(*lists):
        for i in range(2):
            # get a list of all "starts" from same tuple
            curr = [ l[i] for l in tup]
            # if any pair diff is bigger then 0.5, can't be synced-freeze-wise
            if any([abs(a-b)>0.5 for (a,b) in list(itertools.combinations(curr, 2))]):
                is_synced = False
                break
        if not is_synced:
            break
            
    return is_synced
