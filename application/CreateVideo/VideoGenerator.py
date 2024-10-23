import os
import shutil
from moviepy.editor import VideoFileClip, clips_array, CompositeAudioClip, AudioFileClip
import assemblyai as aai
import requests
import subprocess
import pysubs2
from datetime import timedelta
import json


# Setup directories for the project
output_dir = r"C:/Users/hecto/Desktop/Clip_Farmer/output"
os.makedirs(output_dir, exist_ok=True)
aai.settings.api_key="60ad7c01d97b488ba098a7e9f5d97936"
config = aai.TranscriptionConfig(auto_highlights=True, speaker_labels=True)
transcriber = aai.Transcriber(config=config)

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from backend.firebase import check_if_title_exists, upload_file_to_storage, add_video_metadata  # Import function to fetch videos



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
        first_clip_path = self.download_video(self.first_video_data['url'], "first_video.mp4")
        second_clip_path = None
        if not self.modifications['single_video']:
            second_clip_path = self.download_video(self.second_video_data['url'], "second_video.mp4")

        # Determine which audio and subtitles to use based on modifications
        audio_source = first_clip_path if self.modifications['audio_top'] else second_clip_path
        subtitle_source = first_clip_path if self.modifications['subtitles_top'] else second_clip_path

        # Combine the video clips based on the user's selection
        combined_clip = self.combine_videos(first_clip_path, second_clip_path)

        # Generate subtitles
        self.speechToText(audio_source)

        # Apply subtitles
        final_path = self.add_subtitles_with_ffmpeg(combined_clip, subtitle_source)

        # Add thumbnail
        output_thumbnail = self.add_thumbnail(final_path)

        print("Final path ", final_path)
        print("Thumbnail path ", output_thumbnail)

        self.add_to_library(final_path,output_thumbnail)

        # Cleanup
        #self.clean_up_temp_files(final_path)

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
        # Load and create subclips based on the clip duration
        first_clip = VideoFileClip(first_video).subclip(0, self.clip_duration).without_audio()
        if second_video:
            second_clip = VideoFileClip(second_video).subclip(0, self.clip_duration).without_audio()
            combined_clip = clips_array([[second_clip], [first_clip]])  # Place second video on top, first on bottom
        else:
            combined_clip = first_clip  # Single video

        # Handle audio
        audio_clip = AudioFileClip(first_video if self.modifications['audio_top'] else second_video).subclip(0, self.clip_duration)
        combined_clip = combined_clip.set_audio(audio_clip)

        # Save the combined video
        combined_clip_path = os.path.join(output_dir, "combined_output.mp4")
        combined_clip.write_videofile(combined_clip_path, audio_codec='aac')
        self.combinedFilePath = combined_clip_path

        return combined_clip_path

    def add_subtitles_with_ffmpeg(self, video_path, subtitle_path):
        """Add subtitles to the video using FFmpeg."""
        output_path = os.path.join(output_dir, "final_output.mp4")
        subtitle_file = os.path.join(output_dir, "subtitles.ass")
        
        command = [
            'ffmpeg', '-y', '-i', video_path,
            '-vf', f"subtitles={subtitle_file}:fontsdir={output_dir}/fonts",
            output_path
        ]
        subprocess.run(command)
        return output_path

    def speechToText(self, audio_file):
        """Convert speech to text and generate subtitles."""
        audio_path = os.path.join(output_dir, audio_file)
        transcript = transcriber.transcribe(audio_path)
        subtitles = transcript.export_subtitles_srt()
        
        with open(os.path.join(output_dir, "subtitles.srt"), 'w') as f:
            f.write(subtitles)
        
        # Generate ASS subtitles from SRT
        subs = pysubs2.load(os.path.join(output_dir, "subtitles.srt"))
        subs.save(os.path.join(output_dir, "subtitles.ass"))

    def add_thumbnail(self, video_path):
        """Generate a thumbnail from the video."""
        output_thumbnail = os.path.join(output_dir, "thumbnail.jpg")
        command = [
            'ffmpeg', '-y', '-i', video_path, '-ss', '2', '-vframes', '1', output_thumbnail
        ]
        subprocess.run(command)
        return output_thumbnail

    def clean_up_temp_files(self):
        """Clean up temporary files after processing."""
        temp_files = ['first_video.mp4', 'second_video.mp4', 'combined_output.mp4', 'subtitles.srt', 'subtitles.ass']
        for temp_file in temp_files:
            try:
                os.remove(os.path.join(output_dir, temp_file))
            except FileNotFoundError:
                pass

    def add_to_library(self, filepath, thumbnail):
        """Uploads the generated video and thumbnail to Firebase Storage and adds metadata to Firestore."""
        folder_type = "CreatedVideos"  # Folder where the videos and thumbnails are stored
        title = self.modifications['title']  # Video title from modifications

        # Check if the video title already exists in Firestore
        if check_if_title_exists(title):
            print(f"A video with the title '{title}' already exists in Firestore. Please choose a different title.")
            return

        # Upload video to Firebase Storage
        video_url = upload_file_to_storage(filepath, f"{title}.mp4", folder_type, "videos")

        # Upload thumbnail to Firebase Storage
        thumbnail_url = upload_file_to_storage(thumbnail, f"{title}_thumbnail.jpg", folder_type, "thumbnails")

        # Add metadata (title, video URL, thumbnail URL) to Firestore
        add_video_metadata(title, video_url, thumbnail_url, folder_type)

        print(f"Video '{title}' successfully uploaded to Firebase Storage and metadata saved in Firestore.")
