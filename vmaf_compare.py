import argparse
from pathlib import Path
from ffmpeg_quality_metrics import FfmpegQualityMetrics


def compare_videos(ref_file_path, enc_file_path):
    ref_file = Path(ref_file_path)
    enc_file = Path(enc_file_path)

    vmaf_scores = []

    if enc_file.exists():
        # Calculate the SSIM, PSNR, and VMAF metrics for the two videos
        ffqm = FfmpegQualityMetrics(str(enc_file), str(ref_file))
        metrics = ffqm.calculate(["ssim", "psnr", "vmaf"])

        avg_vmaf = sum([frame["vmaf"] for frame in metrics["vmaf"]]) / len(
            metrics["vmaf"]
        )
        vmaf_scores.append(avg_vmaf)

    return vmaf_scores


def file_size_compare(ref_file_path, enc_file_path):
    ref_file = Path(ref_file_path)
    enc_file = Path(enc_file_path)

    size_diff = 0
    percentage = 0

    if enc_file.exists():
        ref_size = ref_file.stat().st_size
        enc_size = enc_file.stat().st_size
        size_diff = ref_size - enc_size
        percentage = (enc_size / ref_size) * 100
        encoded_file_size = int(enc_size)

    return size_diff, percentage, encoded_file_size


if __name__ == "__main__":
    # Parse the command line arguments
    parser = argparse.ArgumentParser(description="Compare two folders of video files.")
    parser.add_argument(
        "ref_folder", type=str, help="the path to the reference videos folder"
    )
    parser.add_argument(
        "enc_folder", type=str, help="the path to the encoded videos folder"
    )
    args = parser.parse_args()
    # Call the compare_videos function with the command line arguments
    compare_videos(args.ref_folder, args.enc_folder)
