from av1pyconvert import av1pyconvert
from vmaf_compare import compare_videos, file_size_compare
from pathlib import Path
from rich.progress import Progress, Text
from rich.progress import ProgressColumn, BarColumn, TimeElapsedColumn
import json, datetime, os, time


class TotalFilesColumn(ProgressColumn):
    def __init__(self, total_files, completed_files_ref):
        self.total_files = total_files
        self.completed_files_ref = completed_files_ref
        super().__init__()

    def render(self, task):
        completed_files = self.completed_files_ref[0]
        return Text(f"{completed_files}/{self.total_files} files", justify="right")


class ETAColumn(ProgressColumn):
    def __init__(self, start_time):
        self.start_time = start_time
        super().__init__()

    def render(self, task):
        completed_files = task.completed
        if completed_files == 0:
            return Text("ETA: --:--:--", justify="right")
        elapsed_time = time.time() - self.start_time
        avg_time_per_file = elapsed_time / completed_files
        remaining_files = task.total - completed_files
        eta_seconds = int(avg_time_per_file * remaining_files)
        eta_time = str(datetime.timedelta(seconds=eta_seconds))
        return Text(f"ETA: {eta_time}", justify="right")


start_time = time.time()


def store_job_info(orig_file, enc_file, encoded_file_size, crf_value, preset_value):
    # Get the file name from the original file path
    orig_file_name = os.path.basename(orig_file)

    # Normalize the encoded file path to remove double slashes
    enc_file_path = os.path.normpath(enc_file)
    # Get the current datetime and format it without the decimal after the seconds
    current_datetime = datetime.datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

    job_info = {
        "crf": crf_value,
        "preset": preset_value,
        "file_size": encoded_file_size,
        "finish_time": formatted_datetime,
        "location": enc_file_path,
    }

    json_file = "jobs.json"

    if not os.path.exists(json_file):
        with open(json_file, "w") as outfile:
            json.dump({}, outfile)

    try:
        with open(json_file, "r") as infile:
            stored_jobs = json.load(infile)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON in {json_file}: {e}")
        print("Creating new jobs file...")
        stored_jobs = {}

    # Store the job info using the original file name as the key
    stored_jobs[orig_file_name] = job_info

    json_string = json.dumps(stored_jobs)
    json_string = json_string.replace("},", "},\n")

    with open(json_file, "w") as outfile:
        outfile.write(json_string)


def adaptive_av1pyconvert(
    orig_folder_path,
    enc_folder_path,
    crf_value,
    preset_value,
    vmaf_threshold,
    size_threshold_percent,
):
    orig_folder_path = Path(orig_folder_path)
    enc_folder_path = Path(enc_folder_path)
    initial_crf = int(crf_value)

    orig_files = [f for f in orig_folder_path.glob("**/*.mkv") if f.is_file()]

    start_time = time.time()
    completed_files_ref = [0]

    total_files_column = TotalFilesColumn(len(orig_files), completed_files_ref)

    # Initialize progress bars
    with Progress(
        "[progress.description]{task.description}",
        " ",
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.0f}%",
        " ",
        TimeElapsedColumn(),
        " ",
        ETAColumn(start_time),
        " ",
        total_files_column,
    ) as progress:
        overall_task_id = progress.add_task(
            "[green]Overall Progress...",
            total=len(orig_files),
            completed=0,
        )

        for index, orig_file in enumerate(orig_files, start=1):
            enc_file = enc_folder_path / orig_file.relative_to(orig_folder_path)

            crf = initial_crf  # Reset the CRF value for each file
            crf_count = {}

            while True:
                av1pyconvert(orig_file, enc_file, crf, preset_value, progress)

                vmaf_score = compare_videos(orig_file, enc_file)
                avg_vmaf = sum(vmaf_score) / len(vmaf_score)

                size_diff, percentage, encoded_file_size = file_size_compare(
                    orig_file, enc_file
                )
                encoded_file_size = encoded_file_size
                vmaf_diff = vmaf_threshold - avg_vmaf
                size_diff_percent = size_threshold_percent - percentage

                if percentage >= size_threshold_percent:
                    crf += max(1, min(63 - crf, int(abs(size_diff_percent) * 0.5)))
                elif avg_vmaf < vmaf_threshold:
                    crf -= max(1, min(crf - 1, int(abs(vmaf_diff) * 0.5)))
                else:
                    # Call store_job_info to store the completed encoded files inside of the parameters requested
                    store_job_info(
                        orig_file, enc_file, encoded_file_size, crf, preset_value
                    )
                    print(
                        f"VMAF Score: {avg_vmaf:.2f}%, File Size Difference: {size_diff:.2f} MB, Percentage Of Orignal File Size: {percentage:.2f}%"
                    )
                    # Update the overall progress bar
                    progress.update(
                        overall_task_id,
                        advance=1,
                        description=f"[green]Overall Progress ({index}/{len(orig_files)}):",
                    )
                    completed_files_ref[0] = index
                    break

                # Clamp CRF value to be within 0 and 63 (inclusive)
                crf = max(0, min(crf, 63))

                # Update the CRF count dictionary
                if crf in crf_count:
                    crf_count[crf] += 1
                else:
                    crf_count[crf] = 1

                # If a CRF value has been encountered two times or reached the maximum, decrease the preset value or stop the program
                if preset_value == 6 and (crf_count[crf] >= 2 or crf == 63):
                    msg1 = f"Unable to reach set values VAMF {vmaf_threshold} and file min percent {size_threshold_percent}!"
                    msg2 = f"Please use the preset value of {preset_value + 1} and a CRF of {crf} when you rerun the program!"
                    raise RuntimeError(f"{msg1}\n{msg2}")
                elif crf_count[crf] >= 2 or crf == 63:
                    preset_value = max(
                        6, preset_value - 1
                    )  # Ensure the preset value does not go below 6
                    crf_count = {}  # Reset the CRF count dictionary


orig_folder_path = (
    input("Enter the path to the original videos folder: ")
    .replace("'", "")
    .replace('"', "")
)
enc_folder_path = (
    input("Enter the path to the output videos folder: ")
    .replace("'", "")
    .replace('"', "")
)

crf_value = input("Enter the CRF value (recommended range is 35-25): ")
preset_value = int(input("Enter the preset value (recommend range is 10-6): "))
vmaf_threshold = float(input("Enter the VMAF threshold Max 98: "))
size_threshold_percent = float(
    input("Enter the file size threshold as a percentage 15-99: ")
)


vmaf_threshold = max(0, min(vmaf_threshold, 98))
size_threshold_percent = max(15, min(size_threshold_percent, 99))

adaptive_av1pyconvert(
    orig_folder_path,
    enc_folder_path,
    crf_value,
    preset_value,
    vmaf_threshold,
    size_threshold_percent,
)
