import os, ffmpeg, subprocess, threading
from pathlib import Path


def av1pyconvert(orig_file_path, enc_file_path, crf_value, preset_value, progress):
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

    # Get the total duration of the input video
    total_duration = float(ffmpeg.probe(str(orig_file))["format"]["duration"])

    svtav1_params = "tune=0:fast-decode=1"

    # Initialize progress bar
    task_id = progress.add_task("[blue]Encoding... ", total=total_duration)

    # Set up the FFmpeg command
    cmd = (
        ffmpeg.input(str(orig_file))
        .output(
            str(enc_file),
            acodec="copy",
            vcodec=codec,
            preset=preset,
            crf=crf,
            threads=threads,
            **{"svtav1-params": svtav1_params},
        )
        .global_args(
            "-map",
            "0:v",
            "-map",
            "0:a?",
            "-loglevel",
            "quiet",
            "-progress",
            "pipe:1",
        )
        .overwrite_output()
        .compile()
    )

    # Function to parse progress output
    def parse_progress(progress_output):
        progress_dict = {}
        for line in progress_output.splitlines():
            if "=" in line:
                key, value = line.split("=", 1)  # Split only once
                progress_dict[key.strip()] = value.strip()
        return progress_dict

    # Function to read the FFmpeg output in a separate thread
    def read_ffmpeg_output(proc, progress, task_id):
        while True:
            # Read a line from stdout
            stdout_line = proc.stdout.readline()

            # Break the loop if the line is empty, which means the process has finished
            if not stdout_line:
                break

            # Parse the progress output and update the progress bar
            progress_data = parse_progress(stdout_line)
            if "out_time_ms" in progress_data:
                time = round(float(progress_data["out_time_ms"]) / 1000000.0, 2)
                progress.update(task_id, completed=time)

    # Run the FFmpeg command
    with subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        bufsize=1,
    ) as proc:
        # Create a separate thread to read the FFmpeg output
        output_thread = threading.Thread(
            target=read_ffmpeg_output, args=(proc, progress, task_id)
        )
        output_thread.start()

        # Wait for the output thread to finish
        output_thread.join()

    progress.update(task_id, advance=1)
    progress.remove_task(task_id)

    return task_id
