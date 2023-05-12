This project aims to use python to convert and compare multiple video files in folders. 

1. This project requires a FFMPEG Binary with libsvtav1 codec.
2. Place FFMPEG Binary in the folder containing AV1PyConvert.
3. PS or CMD: pip install -r requirements.txt
4. Then give it a path to master copy of your media.
5. Pass a new location where you want it to encode your media!
6. Wait for it to finish converting everything in your folder to new AV1 Codec!
7. Read VMAF, PSNR, and SSIM scores the closer to 100 for VMAF the better the quality!
8. Profit !!!

This master branch should work as it stands so long you follow the steps above!

Requirements
1. Python 3.10.7
2. ffmpeg-python==0.2.0 (pip install ffmpeg-python==0.2.0)
3. ffmpeg-quality-metrics==3.2.1 (pip install ffmpeg-quality-metrics==3.2.1)
4. rich==13.3.5 (pip install rich==13.3.5)


Plans
1. Add support to read other forms of containers such as avi, mov, and MP4.
2. Allow user to choose to convert to any container of choice.
3. Add more encoder support such as H265, VP9, H264, and anymore widely used encoders.
4. And many more plans!
