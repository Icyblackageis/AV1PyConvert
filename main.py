from av1pyconvert import av1pyconvert
from vmaf_compare import compare_videos, file_size_compare
from pathlib import Path


def check_file_conditions(ref_file, enc_file, vmaf_threshold, size_threshold_percent):
    # Calculate VMAF score, file_sizes, orig_file_sizes for the given files
    vmaf_scores = compare_videos(ref_file, enc_file)

    if len(vmaf_scores) > 0:
        avg_vmaf = sum(vmaf_scores) / len(vmaf_scores)
    else:
        avg_vmaf = 0.0

    size_diff, percentage = file_size_compare(orig_folder_path, enc_folder_path)

    if avg_vmaf >= vmaf_threshold and percentage <= size_threshold_percent:
        return True
    return False



def adaptive_av1pyconvert(orig_folder_path, enc_folder_path, crf_value, preset_value, vmaf_threshold,
                          size_threshold_percent):
    orig_folder_path = Path(orig_folder_path)
    enc_folder_path = Path(enc_folder_path)
    crf = int(crf_value)

    orig_files = [f for f in orig_folder_path.glob("**/*.mkv") if f.is_file()]

    for orig_file in orig_files:
        enc_file = enc_folder_path / orig_file.relative_to(orig_folder_path)

        if enc_file.exists() and check_file_conditions(orig_file, enc_file, vmaf_threshold, size_threshold_percent):
            continue  # Skip this file as it already meets the conditions

        while True:
            av1pyconvert(orig_folder_path, enc_folder_path, crf, preset_value)
            vmaf_score = compare_videos(orig_folder_path, enc_folder_path)
            avg_vmaf = sum(vmaf_score) / len(vmaf_score)

            size_diff, percentage = file_size_compare(orig_folder_path, enc_folder_path)

            if percentage >= size_threshold_percent:
                crf += 2
            elif avg_vmaf < vmaf_threshold:
                crf -= 1
            else:
                break

    file_size_compare(orig_folder_path, enc_folder_path)


orig_folder_path = input("Enter the path to the original videos folder: ").replace("'", "").replace('"', '')
enc_folder_path = input("Enter the path to the output videos folder: ").replace("'", "").replace('"', '')
crf_value = input("Enter the CRF value (recommended range is 35-25): ")
preset_value = int(input("Enter the preset value (recommend range is 10-6): "))
vmaf_threshold = float(input("Enter the VMAF threshold: "))
size_threshold_percent = float(input("Enter the file size threshold as a percentage: "))

adaptive_av1pyconvert(orig_folder_path, enc_folder_path, crf_value, preset_value, vmaf_threshold,
                      size_threshold_percent)
