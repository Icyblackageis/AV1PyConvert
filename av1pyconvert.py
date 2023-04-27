import os
from pathlib import Path
import ffmpeg
from vmaf_compare import compare_videos, file_size_compare


def av1pyconvert(orig_folder_path, enc_folder_path, crf_value):
    # Set the paths to the original and output folders
    orig_folder = Path(orig_folder_path)
    enc_folder = Path(enc_folder_path)

    # Create the output folder if it doesn't exist
    enc_folder.mkdir(parents=True, exist_ok=True)

    # Set the codec to use for encoding
    codec = "libsvtav1"

    # Use the passed CRF value
    crf = crf_value

    # Set the encoding parameters
    preset = "6"  # The encoding preset to use. Lower values result in higher quality and smaller files.
    threads = os.cpu_count()  # The number of threads to use for encoding. Use all available CPU cores.

    # Loop through all video files in the original folder and encode them
    for orig_file in orig_folder.glob("**/*.mkv"):
        # Get the input and output file paths
        in_file = str(orig_file)
        out_file = str(enc_folder / orig_file.relative_to(orig_folder))

        # Convert out_file to a Path object and create the output folder if it doesn't exist
        out_file_path = Path(out_file)
        out_file_path.parent.mkdir(parents=True, exist_ok=True)

        # Set the encoding command
        stream = ffmpeg.input(in_file)
        stream = ffmpeg.output(stream, out_file, map='0', acodec='copy', vcodec=codec, preset=preset, crf=crf, threads=threads)

        # Run the encoding process
        ffmpeg.run(stream, cmd='ffmpeg', overwrite_output=True)

    # Call the vmaf_compare.py script to compare the encoded file to the original file
    compare_videos(orig_folder, enc_folder)
    file_size_compare(orig_folder, enc_folder)
