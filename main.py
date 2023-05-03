from av1pyconvert import av1pyconvert
from vmaf_compare import compare_videos, file_size_compare
from pathlib import Path
import json, datetime, os


def store_job_info(orig_file, enc_file, crf_value, preset_value):
    json_file = "jobs.json"
    
    # Load existing data or create a new dictionary
    if os.path.exists(json_file):
        with open(json_file, "r") as infile:
            data = json.load(infile)
    else:
        data = {}
    
    # Update data with the new job information
    data[enc_file] = {
        "crf": crf_value,
        "preset": preset_value,
        "finish_time": str(datetime.datetime.now()),
        "location": str(enc_file),
    }
    
    # Save the updated data to the JSON file
    with open(json_file, "w") as outfile:
        json.dump(data, outfile, indent=4)

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

    for orig_file in orig_files:
        enc_file = enc_folder_path / orig_file.relative_to(orig_folder_path)

        crf = initial_crf  # Reset the CRF value for each file
        crf_count = {}

        while True:
            av1pyconvert(orig_file, enc_file, crf, preset_value)
            vmaf_score = compare_videos(orig_file, enc_file)
            avg_vmaf = sum(vmaf_score) / len(vmaf_score)

            _, percentage = file_size_compare(orig_file, enc_file)

            vmaf_diff = vmaf_threshold - avg_vmaf
            size_diff_percent = size_threshold_percent - percentage

            if percentage >= size_threshold_percent:
                crf += max(1, min(63 - crf, int(abs(size_diff_percent) * 0.5)))
            elif avg_vmaf < vmaf_threshold:
                crf -= max(1, min(crf - 1, int(abs(vmaf_diff) * 0.5)))
            else:
                store_job_info(orig_file, enc_file, crf, preset_value)
                break

            # Update the CRF count dictionary
            if crf in crf_count:
                crf_count[crf] += 1
            else:
                crf_count[crf] = 1

            # If a CRF value has been encountered three times, decrease the preset value
            if preset_value == 6 and crf_count[crf] >=2:
                print(
                    f"Unable to reach set values VAMF {vmaf_threshold} and file min size {size_threshold_percent}!"
                )
                print(
                    f"Please use the preset value of {preset_value + 1} and a CRF of {crf} when you rerun the program!"
                )
                break
            elif crf_count[crf] >= 2 or crf == 63:
                preset_value = max(
                    6, preset_value - 1
                )  # Ensure the preset value does not go below 0
                crf_count = {}  # Reset the CRF count dictionary

    file_size_compare(orig_folder_path, enc_folder_path)


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
vmaf_threshold = float(input("Enter the VMAF threshold: "))
size_threshold_percent = float(input("Enter the file size threshold as a percentage: "))

adaptive_av1pyconvert(
    orig_folder_path,
    enc_folder_path,
    crf_value,
    preset_value,
    vmaf_threshold,
    size_threshold_percent,
)
