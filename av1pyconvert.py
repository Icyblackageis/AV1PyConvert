import os
from pathlib import Path

import ffmpeg

from vmaf_compare import compare_videos, file_size_compare


def av1pyconvert(orig_file_path, enc_file_path, crf_value, preset_value):
    # Convert input paths to Path objects
    orig_file = Path(orig_file_path)
    enc_file = Path(enc_file_path)

    # Create the output folder if it doesn't exist
    enc_file.parent.mkdir(parents=True, exist_ok=True)

    # Set the codec to use for encoding
    codec = "libsvtav1"
    # Use the passed CRF value
    crf = crf_value

    # Set the encoding parameters
    preset = preset_value  # The encoding preset to use. Lower values result in higher quality and smaller files.
    threads = (
        os.cpu_count()
    )  # The number of threads to use for encoding. Use all available CPU cores.

    # Set the encoding command
    stream = ffmpeg.input(str(orig_file))
    stream = ffmpeg.output(
        stream,
        str(enc_file),
        acodec="copy",
        vcodec=codec,
        preset=preset,
        crf=crf,
        threads=threads,
    ).global_args("-map", "0:v", "-map", "0:a?", "-loglevel", "quiet", "-stats")

    # Run the encoding process
    ffmpeg.run(stream, cmd="ffmpeg", overwrite_output=True)
    

