import subprocess
import os

# Define the file paths
video_file = "video.mp4"  # Your input video file
subtitle_file = "subtitles.ass"  # Your subtitle file
output_file = "output_with_subtitles.mp4"  # The output video file with burned subtitles

# Ensure paths are in the correct format for FFmpeg (using forward slashes for Windows)
video_file = video_file.replace("\\", "/")
subtitle_file = subtitle_file.replace("\\", "/")
output_file = output_file.replace("\\", "/")

# FFmpeg command to burn the subtitles onto the video
command = [
    "ffmpeg", "-y",  # Overwrite output file if it exists
    "-i", video_file,  # Input video file
    "-vf", f"subtitles={subtitle_file}",  # Apply the .ass subtitle filter
    output_file  # Output file with subtitles burned in
]

# Run the command and capture any output or errors
print(f"Running command: {' '.join(command)}")
result = subprocess.run(command, stderr=subprocess.PIPE)

# Print the FFmpeg output or error logs
if result.returncode == 0:
    print(f"Subtitles successfully burned into {output_file}")
else:
    print(f"Error burning subtitles: {result.stderr.decode()}")
