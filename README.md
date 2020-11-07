# freeze_detect
## overview
A sample project that uses ffmpeg ability to detect freezes in video.
* Written in python for simplicity over performance
* uses the pytest framework for testing: 
* uses ffmpeg program (build directly after cloning from developers git)

this script logs itself in `freeze.log` in the script folder. use --verbose or -v for more logs

## about ffmpeg:
* [website](https://ffmpeg.org)
* source code taken from: `git clone https://git.ffmpeg.org/ffmpeg.git ffmpeg` and follow readme to install on *nix machine.
* this project specificly the freeze detect filter: https://ffmpeg.org/ffmpeg-filters.html#freezedetect

## installation
1. [python3.6](https://www.python.org/downloads/)
2. [pip - package installer for python](https://pypi.org/project/pip/)
3. clone repo
4. change dir to `src`
5. run `pip install -r requirements.txt` (on folder)

## usage
1. once installation has finish, in `src` folder running `python3 freeze_frame_validator.py -h`
will give the help man:
```
usage: freeze_frame_validator.py [-h] [-n N] [-d D] [-o O] [-v] U [U ...]

find frozen frames in videos from urls

positional arguments:
  U                   url for a video file to analyze

optional arguments:
  -h, --help          show this help message and exit
  -n N, --noise N     value of noise tolerance, between 0 and 1, default 0.001
  -d D, --duration D  freeze duration until notification, default 2
  -o O, --output O    file name to save result json to. if none, will print
                      the json to standard output.
  -v, --verbose       more information in logs
```
example usage:
2. `python3 freeze_frame_validator.py https://storage.googleapis.com/hiring_process_data/freeze_frame_input_a.mp4 https://storage.googleapis.com/hiring_process_data/freeze_frame_input_b.mp4 -n 0.003 --verbose -o freezer.json`
will run the validator on 2 videos, with noise: 0.003 and duration will be default (2). it will also create a verbose log file.
it will save the json result to: `freezer.json` in the script folder.
3. `python3 freeze_frame_validator.py https://storage.googleapis.com/hiring_process_data/freeze_frame_input_c.mp4 https://storage.googleapis.com/hiring_process_data/freeze_frame_input_a.mp4 https://storage.googleapis.com/hiring_process_data/freeze_frame_input_b.mp4 -n 0.003`
will run almost the same, but with 3 videos instead of 2, no verbose log, and the output will be rendered to the cmd output.
in this state it can be used with PIPE in order to chain bash commands.

## testing
the repo comes ready for testing the utility part of this script.
any code that can be used in other context is part of `freeze_utils.py` and is tested in `test_utils.py` using pytest.

to run the test suite:
1. move to `src` folder
2. run `pytest` to run all tests
3. run `pytest -k <name of test>` to run a specific test