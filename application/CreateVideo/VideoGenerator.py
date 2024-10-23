import os
import shutil
from moviepy.editor import VideoFileClip, clips_array, AudioFileClip
import assemblyai as aai
import subprocess
import pysubs2
from datetime import timedelta
import json
import requests
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from backend.firebase import check_if_title_exists, upload_file_to_storage, add_video_metadata  # Import function to fetch videos
# Get the directory where main.py is located

# Setup directories for the project
# Hard-coded path to where you want the output files saved (application/)
output_dir = r"C:/Users/hecto/Desktop/ClipFarmer/application"
  # Save output files directly in the application directory (same as main.py)
subtitle_file = "subtitles.ass"
newsubtitle = os.path.join(output_dir, subtitle_file)
newoutputdir = os.path.join(output_dir, "combined_output_with_subs.mp4")
audioFilePath = os.path.join(output_dir, "output_audio.wav")

os.environ["IMAGEMAGICK_BINARY"] = "C:/Program Files/ImageMagick-7.1.1-Q16-HDRI"

aai.settings.api_key = "60ad7c01d97b488ba098a7e9f5d97936"
config = aai.TranscriptionConfig(auto_highlights=True, speaker_labels=True)
transcriber = aai.Transcriber(config=config)


class VideoGenerator:
    def __init__(self, modifications, first_video_data=None, second_video_data=None):
        self.modifications = modifications
        self.first_video_data = first_video_data
        self.second_video_data = second_video_data
        self.combinedFilePath = ""
        self.subtitle_cache = {}
        self.video_name_cache = []

        # Determine the duration or length for the clip
        self.clip_duration = self.get_clip_duration()

        # Call create_video with modifications and video data
        self.filepath = self.create_video()

    def get_clip_duration(self):
        """Determine whether to use 'length' or 'duration' based on what's provided."""
        length = self.modifications['length']
        duration = self.modifications['duration']

        if length != 0:
            return length
        elif duration != '':
            return float(duration)  # Ensure it's a float for MoviePy
        else:
            raise ValueError("Both 'length' and 'duration' are missing. Provide at least one.")

    def create_video(self):
        outputPath = os.path.join(output_dir, "output_subtitles.mp4")
        print("output path in create video", outputPath)
        ## --- STEP 1. DOWNLOAD VIDEOS --- ##
        first_clip_path = self.download_video(self.first_video_data['url'], "first_video.mp4")
        second_clip_path = None
        if not self.modifications['single_video']:
            second_clip_path = self.download_video(self.second_video_data['url'], "second_video.mp4")

        ## --- STEP 2. FIND AUDIO/SUBTITLE SOURCE --- ##
        audio_source = first_clip_path if self.modifications['audio_top'] else second_clip_path
        subtitle_source = first_clip_path if self.modifications['subtitles_top'] else second_clip_path
        print("AUDIO SOURCE:", audio_source)
        print("SUBTITLE SOURCE", subtitle_source)

        ## --- STEP 3. COMBINE VIDEOS --- ##
        combined_clip = self.combine_videos(first_clip_path, second_clip_path)

        ## --- STEP 4. EXTRACT AUDIO FROM COMBINED VIDEO --- ##
        ass_path = self.speechToText(audioFilePath)

        ## --- STEP 6. ADD SUBTITLES TO VIDEO --- ##
        final_path = self.add_subtitles_with_ffmpeg(combined_clip, ass_path)

        ## --- STEP 7. GENERATE THUMBNAIL --- ##
        output_thumbnail = self.add_thumbnail(final_path)

        print("Final path: ", final_path)
        print("Thumbnail path: ", output_thumbnail)

        self.add_to_library(final_path, output_thumbnail)
        return final_path

    def download_video(self, url, filename):
        """Download video from URL and save it to the output directory."""
        save_path = os.path.join(output_dir, filename)
        try:
            print(f"Downloading video from {url}")
            response = requests.get(url, stream=True)
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    f.write(chunk)
        except Exception as e:
            print(f"Error downloading video: {e}")
        return save_path

    def combine_videos(self, first_video, second_video=None):
        """Combine one or two video clips based on the user's selection."""
        first_clip = VideoFileClip(first_video).subclip(0, self.clip_duration).without_audio()
        second_clip = None
        if second_video:
            second_clip = VideoFileClip(second_video).subclip(0, self.clip_duration)
            combined_clip = clips_array([[second_clip], [first_clip]])  # Place second video on top, first on bottom
        else:
            combined_clip = first_clip  # Single video

        original_audio = second_clip.audio if second_clip else first_clip.audio
        original_audio.write_audiofile(audioFilePath)

        combined_clip = combined_clip.set_audio(original_audio)
        combined_clip.write_videofile(os.path.join(output_dir, "combined_output.mp4"), audio_codec='aac')
        self.combinedFilePath = os.path.join(output_dir, "combined_output.mp4")

        return self.combinedFilePath

    def add_subtitles_with_ffmpeg(self, video_path, subtitle_path):
        """Add subtitles to the video using FFmpeg."""
        
        output_path = "combined_output_with_subs.mp4"
        subtitle_path = "subtitles.ass"
        video_path = "combined_output.mp4"
        # Ensure subtitle file exists
        if not os.path.exists(subtitle_path):
            print(f"Subtitle file not found: {subtitle_path}")
            return

        print("Output path:", output_path)
        print("Subtitle file:", subtitle_path)
        print("Adding subtitles with FFmpeg")

        # Ensure paths are properly formatted and escaped
        subtitle_path = subtitle_path.replace("\\", "/")
        video_path = video_path.replace("\\", "/")
        output_path = output_path.replace("\\", "/")

        # FFmpeg command with double quotes around the subtitle path
        command = [
            "ffmpeg", "-y",  # Overwrite output file if it exists
            "-i", video_path,  # Input video file
            "-vf", f"subtitles={subtitle_path}",  # Apply the .ass subtitle filter
            output_path  # Output file with subtitles burned in
        ]

        print(f"Running FFmpeg command: {' '.join(command)}")

        # Run the FFmpeg command and capture any errors
        result = subprocess.run(command, stderr=subprocess.PIPE, stdout=subprocess.PIPE)

        # Check for errors in FFmpeg processing
        if result.returncode != 0:
            print("FFmpeg failed with error:")
            print(result.stderr.decode())
        else:
            print("Subtitles successfully added to video.")

        return output_path



    def speechToText(self, audioFileName):
        print("-----STEP 3. Speech to Text-----")

        audioFilePath = os.path.join(output_dir, audioFileName)
        print(f"Audio file path: {audioFilePath}")

        # Transcribe the audio to text using AssemblyAI
        try:
            transcript = transcriber.transcribe(audioFilePath)
            words = transcript.words
        except Exception as e:
            print(f"Error during transcription: {e}")
            return

        srt_lines = []
        current_line = []
        current_start_time = None
        prev_end_time = 0
        total = 0
        min_duration_ms = 850

        # Process the transcript words
        for word in words:
            start_time = word.start / 1000
            end_time = word.end / 1000
            word.text = word.text.upper()

            # Determine when to start a new subtitle line
            new_line_conditions = [
                total + len(word.text) + 1 > 15,  # Word count limit for a subtitle line
                (start_time - prev_end_time) * 1000 > min_duration_ms,  # Long pause between words
                word.text.strip().endswith(('.', '?', '!'))  # End of sentence punctuation
            ]

            if not current_start_time:
                current_start_time = start_time

            if any(new_line_conditions):
                if current_line:
                    start = str(timedelta(seconds=current_start_time))
                    end = str(timedelta(seconds=prev_end_time))
                    srt_lines.append((start, end, ' '.join(current_line)))
                    current_line = []
                    total = 0

                current_start_time = max(prev_end_time, start_time)

            current_line.append(word.text)
            total += len(word.text) + 1
            prev_end_time = end_time

            if word.text.strip().endswith(('.', '?', '!')) and current_line:
                start = str(timedelta(seconds=current_start_time))
                end = str(timedelta(seconds=prev_end_time))
                srt_lines.append((start, end, ' '.join(current_line)))
                current_line = []
                total = 0
                current_start_time = None

        # Add the last line if it exists
        if current_line:
            start = str(timedelta(seconds=current_start_time))
            end = str(timedelta(seconds=prev_end_time))
            srt_lines.append((start, end, ' '.join(current_line)))

        # Generate the SRT content
        srt_content = ""
        for index, (start, end, text) in enumerate(srt_lines, 1):
            srt_content += f"{index}\n{start} --> {end}\n{text}\n\n"

        srt_file = os.path.join(output_dir, "subtitles.srt")
        subtitle_fileName = os.path.join(output_dir, "subtitles.ass")  # Always use 'subtitles.ass'

        # Save the SRT file and convert it to ASS using pysubs2
        with open(srt_file, "w") as f:
            f.write(srt_content)

        subs = pysubs2.load(srt_file)
        subs.styles["Default"].alignment = 5  # Set alignment to bottom-center

        subs.save(subtitle_fileName)

        # Apply highlights and animations to the subtitles
        highlights = [result.text.upper() for result in transcript.auto_highlights.results]

        with open(subtitle_fileName, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        modified_lines = []
        for line in lines:
            if line.startswith("Dialogue:"):
                parts = line.split(',', 9)
                text = parts[9]

                # Apply highlight color to specified words
                for highlight in highlights:
                    if highlight in text:
                        colored_highlight = f"{{\\c&H00FFFF&}}{highlight}{{\\c}}"
                        text = text.replace(highlight, colored_highlight)

                # Add animation effects to the text
                animated_text = (
                    "{\\fscx20\\fscy20"  # Start from 20% scale
                    "\\t(0,32,\\fscx120\\fscy120)"  # Quickly scale up to 120%
                    "\\t(32,16,\\fscx100\\fscy100)"  # Then down to 100%
                    "\\t(48,112,\\fscx100\\fscy100)}"  # Stay at 100%
                    + text
                )
                parts[9] = animated_text
                line = ','.join(parts)

            modified_lines.append(line)

        # Write the modified content back to the ASS file (subtitles.ass)
        with open(subtitle_fileName, 'w', encoding='utf-8') as file:
            file.writelines(modified_lines)

        return subtitle_fileName  # Return the path to subtitles.ass


    def add_thumbnail(self, video_path):
        """Generate a thumbnail from the video."""
        output_thumbnail = os.path.join(output_dir, "thumbnail.jpg")
        command = [
            'ffmpeg', '-y', '-i', video_path, '-ss', '2', '-vframes', '1', output_thumbnail
        ]
        subprocess.run(command)
        return output_thumbnail

    def add_to_library(self, filepath, thumbnail):
        folder_type = "CreatedVideos"  # Folder where the videos and thumbnails are stored
        title = self.modifications['title']  # Video title from modifications

        if check_if_title_exists(title):
            print(f"A video with the title '{title}' already exists in Firestore. Please choose a different title.")
            return

        try:
            video_url = upload_file_to_storage(filepath, f"{title}.mp4", folder_type, "videos")
            thumbnail_url = upload_file_to_storage(thumbnail, f"{title}_thumbnail.jpg", folder_type, "thumbnails")
            add_video_metadata(title, video_url, thumbnail_url, folder_type)
        except Exception as e:
            print(f"Error uploading to Firebase: {e}")

        print(f"Video '{title}' successfully uploaded to Firebase Storage and metadata saved in Firestore.")
        self.cleanup_temp_files()

    def cleanup_temp_files(self):
        """Delete all temporary files like .mp4, .wav, .ass, and .srt."""
        temp_files = [
            os.path.join(output_dir, "output_audio.wav"),
            os.path.join(output_dir, "subtitles.ass"),
            os.path.join(output_dir, "subtitles.srt"),
            os.path.join(output_dir, "combined_output.mp4"),
            os.path.join(output_dir, "first_video.mp4"),
            os.path.join(output_dir, "second_video.mp4"),

        ]

        for file in temp_files:
            try:
                if os.path.exists(file):
                    os.remove(file)
                    print(f"Deleted temporary file: {file}")
                else:
                    print(f"File not found, skipping: {file}")
            except Exception as e:
                print(f"Error deleting file {file}: {e}")