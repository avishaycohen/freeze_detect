"""
unit tests for the utility functions in
freeze_utils.py.

to run test stand in folder and run
    pytest
to run specific test run:
    pytest -k "<name of test"
"""
import freeze_utils
import pytest
import subprocess

def test_run_freeze_detect():
    """
    test that freeze detect passes
    """
    assert (isinstance(freeze_utils.run_freeze_detect(path="../examples/freeze_frame_input_a.mp4"),bytes))
    assert (isinstance(freeze_utils.run_freeze_detect(path="../examples/freeze_frame_input_a.mp4", n=0.9),bytes))
    assert (isinstance(freeze_utils.run_freeze_detect(path="../examples/freeze_frame_input_a.mp4", d=3),bytes))

    # this is not valid noise value
    with pytest.raises(subprocess.CalledProcessError):
        assert (isinstance(freeze_utils.run_freeze_detect(path="examples/freeze_frame_input_a.mp4", n=1.1),bytes))


def test_extract_duration():
    """
    test the duration string extraction util
    """
    assert (freeze_utils.extract_duration(b"Duration: 00:01:00.0") == "00:01:00.0")
    # without Duration prefix, extract fails to find values
    with pytest.raises(IndexError):
        assert (freeze_utils.extract_duration(b"00:01:00.0") == "00:01:00.0")


def test_extract_timestamps():
    """
    test the duration string extraction util
    """
    input = b"""
          encoder         : Lavc58.112.101 wrapped_avframe
[freezedetect @ 0x2f9b340] lavfi.freezedetect.freeze_start: 4.5045peed=4.68x
[freezedetect @ 0x2f9b340] lavfi.freezedetect.freeze_duration: 5.92258=5.23x
[freezedetect @ 0x2f9b340] lavfi.freezedetect.freeze_end: 10.4271
[freezedetect @ 0x2f9b340] lavfi.freezedetect.freeze_start: 12.012peed=5.33x
[freezedetect @ 0x2f9b340] lavfi.freezedetect.freeze_duration: 2.23557
[freezedetect @ 0x2f9b340] lavfi.freezedetect.freeze_end: 14.2476
[freezedetect @ 0x2f9b340] lavfi.freezedetect.freeze_start: 18.018peed=5.02x
[freezedetect @ 0x2f9b340] lavfi.freezedetect.freeze_duration: 7.37403=5.17x
[freezedetect @ 0x2f9b340] lavfi.freezedetect.freeze_end: 25.392
frame= 1742 fps=294 q=-0.0 Lsize=N/A time=00:00:29.06 bitrate=N/A speed=4.91x
    """
    expected_output = [('freeze_start', '4.5045'), ('freeze_duration', '5.92258'), ('freeze_end', '10.4271'), ('freeze_start', '12.012'), ('freeze_duration', '2.23557'), ('freeze_end', '14.2476'), ('freeze_start', '18.018'), ('freeze_duration', '7.37403'), ('freeze_end', '25.392')]
    assert (freeze_utils.extract_timestamps(input) == expected_output)


def test_inverter_stamps():
    """
    test the inverter function
    """
    stamps = [('freeze_start', '4.5045'), ('freeze_duration', '5.92258'), ('freeze_end', '10.4271'), ('freeze_start', '12.012'), ('freeze_duration', '2.23557'), ('freeze_end', '14.2476'), ('freeze_start', '18.018'), ('freeze_duration', '7.37403'), ('freeze_end', '25.392')]
    total_time = 29.06
    expected_error = ([[0, 4.5045], [10.4271, 12.012], [14.2476, 18.018], [25.392, 25.392]], 4.5045, 11)
    expected_output = ([[0, 4.5045], [10.4271, 12.012], [14.2476, 18.018], [25.392, 29.06]], 4.5045, 15.53218)
    output = freeze_utils.analyze_freeze_frames(stamps, total_time)
    assert(output != expected_error)
    assert(output == expected_output)