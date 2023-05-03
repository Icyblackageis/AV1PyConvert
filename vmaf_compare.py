import argparse
from pathlib import Path
from ffmpeg_quality_metrics import FfmpegQualityMetrics


def compare_videos(ref_file_path, enc_file_path):
    ref_file = Path(ref_file_path)
    enc_file = Path(enc_file_path)

    vmaf_scores = []

    if enc_file.exists():
        print(f"Comparing Ref {ref_file.name} and Enc {enc_file.name}")
        # Calculate the SSIM, PSNR, and VMAF metrics for the two videos
        ffqm = FfmpegQualityMetrics(str(enc_file), str(ref_file))
        metrics = ffqm.calculate(["ssim", "psnr", "vmaf"])

        avg_vmaf = sum([frame["vmaf"] for frame in metrics["vmaf"]]) / len(
            metrics["vmaf"]
        )
        vmaf_scores.append(avg_vmaf)

        # Print the average metrics for the two videos
        print(
            f"Average SSIM_Y: {sum([frame['ssim_y'] for frame in metrics['ssim']]) / len(metrics['ssim']):.2f}"
        )
        print(
            f"Average PSNR_Y: {sum([frame['psnr_y'] for frame in metrics['psnr']]) / len(metrics['psnr']):.2f}"
        )
        print(
            f"Average VMAF: {sum([frame['vmaf'] for frame in metrics['vmaf']]) / len(metrics['vmaf']):.2f}"
        )
        print()
    else:
        print(f"No matching encoded video found for {ref_file.name}")

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

    print(f"Size Difference: {size_diff / 1024:.2f} MegaBytes")
    print(f"Relative File Size Percentage: {percentage:.2f}%")

    return size_diff, percentage


if __name__ == "__main__":
    # Parse the command line arguments
    parser = argparse.ArgumentParser(description="Compare two folders of video files.")
    parser.add_argument("ref_folder", type=str, help="the path to the reference videos folder")
    parser.add_argument("enc_folder", type=str, help="the path to the encoded videos folder")
    args = parser.parse_args()
    # Call the compare_videos function with the command line arguments
    compare_videos(args.ref_folder, args.enc_folder)
