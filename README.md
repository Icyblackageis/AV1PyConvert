This project aims to use python to convert and compare multiple video files in folders. 

1. This project requires a FFMPEG Binary with libsvtav1 codec.
2. Place FFMPEG Binary in the folder containing AV1PyConvert.
3. Then give it a path to master copy of your media.
4. Pass a new location where you want it to encode your media!
5. Wait for it to finish converting everything in your folder to new AV1 Codec!
6. Read VMAF, PSNR, and SSIM scores the closer to 100 or 1 the better!
7. Profit !!!

This master branch should work as it stands so long you follow the steps above!

Plans
1. Add requirements/setup file to this project ASAP as to make it fully usable no matter what you want to use it for so long as its python 3.10!
2. Will be adding more features such as an ability to choose VMAF, PSNR, and/or SSIM cutoff percentage.
3. Re-encode if file size is larger than a certain percentage by increasing crf value by either a user adjustable amount or 2.
4. Add more encoder support such as H265, VP9, H264, X variants, and anymore widely used encoders.
5. And many more plans!