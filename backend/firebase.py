import firebase_admin
from firebase_admin import credentials, firestore, storage
import os
from moviepy.editor import VideoFileClip

# Path to your Firebase credentials JSON file
cred = credentials.Certificate(os.path.join(os.path.dirname(__file__), "../firebase_credentials.json"))

# Initialize the Firebase Admin SDK
firebase_admin.initialize_app(cred, {
    'storageBucket': 'clipfarmer-f8a79.appspot.com'
})

# Initialize Firestore and Firebase Storage
db = firestore.client()
bucket = storage.bucket()

def upload_file_to_storage(self,file_path, file_name, folder_type, file_type):
    """Uploads a file to Firebase Storage (video or thumbnail) and returns its public URL."""
    blob = bucket.blob(f'{folder_type}/{file_type}/{file_name}')
    blob.upload_from_filename(file_path)
    blob.make_public()
    print(f"{file_type.capitalize()} uploaded to: {blob.public_url}")
    return blob.public_url



def add_video_metadata(self,title, video_url, thumbnail_url, folder_type, duration):
    """Adds a new video document to the 'videos' collection in Firestore."""
    
    # Generate a unique ID for the document
    video_id = db.collection('videos').document().id

    # Define the video data
    video_data = {
        'title': title,
        'url': video_url,
        'thumbnail': thumbnail_url,
        'folder': folder_type,
        'id': video_id,
        'uploaded':  False,
        'upload_url': {      # The upload URL map starts empty
            'Instagram': '',
            'TikTok': '',
            'YouTube': ''
        },
        'duration':duration

    }

    # Add the document to Firestore
    db.collection('videos').document(video_id).set(video_data)
    print(f"Metadata for '{title}' saved in Firestore with ID: {video_id}")

def check_if_title_exists(title):
    """Checks if a video with the given title already exists in Firestore."""
    videos_ref = db.collection('videos')
    query = videos_ref.where('title', '==', title).stream()

    for doc in query:
        return True  # Title already exists
    return False

def list_folders_in_bucket():
        """List the folders in the Firebase Storage bucket."""
        blobs = bucket.list_blobs()  # List all blobs in the bucket
        folders = set()  # Use a set to avoid duplicate folder names
        
        for blob in blobs:
            # Get the folder name by splitting the blob's name
            folder_name = blob.name.split('/')[0]
            folders.add(folder_name)

        return list(folders)    

def get_videos_from_folder(folder_type):
    """Fetches videos from a specified folder (Background, Overlay, CreatedVideos) in Firestore."""
    videos_ref = db.collection('videos')
    query = videos_ref.where('folder', '==', folder_type).stream()

    video_list = []
    for doc in query:
        video_data = doc.to_dict()
        video_data['id'] = doc.id  # Include the document ID
        video_list.append({
            'id': video_data.get('id'),
            'title': video_data.get('title'),
            'thumbnail': video_data.get('thumbnail'),
            'url': video_data.get('url'),
            'uploaded': video_data.get('uploaded'),
            'upload_url': video_data.get('upload_url'),
            'duration': video_data.get('duration')
        })
    
    return video_list


def update_upload_status(video_id, platform, url):
    """
    Updates the uploaded status and upload_url for a specific platform
    after the video is uploaded.
    
    Parameters:
    video_id: The document ID of the video.
    platform: The platform to update (e.g., 'YouTube', 'Instagram', 'TikTok').
    url: The URL of the uploaded video on the platform.
    """
    video_ref = db.collection('videos').document(video_id)
    video_data = video_ref.get().to_dict()

    if video_data:
        # Set the uploaded field to True
        video_data['uploaded'] = True
        
        # Update the upload URL for the specific platform
        video_data['upload_url'][platform] = url

        # Update the document in Firestore
        video_ref.update({
            'uploaded': video_data['uploaded'],
            'upload_url': video_data['upload_url']
        })
        
        print(f"Updated upload status for video ID: {video_id} on platform {platform}")
    else:
        print(f"Video with ID {video_id} not found.")


def delete_video_from_firebase(self,video_id, folder_type, file_name, thumbnail_name):
    """Deletes a video from both Firestore and Firebase Storage."""
    # Delete video from Firestore
    db.collection('videos').document(video_id).delete()
    print(f"Deleted video metadata from Firestore with ID: {video_id}")

    # Delete video file from Firebase Storage
    video_blob = bucket.blob(f'{folder_type}/videos/{file_name}')
    thumbnail_blob = bucket.blob(f'{folder_type}/thumbnails/{thumbnail_name}')
    
    video_blob.delete()
    thumbnail_blob.delete()
    print(f"Deleted video and thumbnail from Firebase Storage: {file_name} and {thumbnail_name}")


def add_song_metadata(self,title, url, thumbnail_url, folder_type, duration):
    """Adds a new video document to the 'videos' collection in Firestore."""
    
    # Generate a unique ID for the document
    song_id = db.collection('music').document().id

    # Define the video data
    song_data = {
        'title': title,
        'url': url,
        'thumbnail': thumbnail_url,
        'folder': folder_type,
        'id': song_id,
        'duration':duration
    }

    # Add the document to Firestore
    db.collection('music').document(song_id).set(song_data)
    print(f"Metadata for '{title}' saved in Firestore with ID: {song_id}")


def check_if_song_exists(self,title):
    """Checks if a video with the given title already exists in Firestore."""
    videos_ref = db.collection('music')
    query = videos_ref.where('title', '==', title).stream()

    for doc in query:
        return True  # Title already exists
    return False


def delete_song_from_firebase(self,song_id, folder_type, file_name, thumbnail_name):
    """Deletes a video from both Firestore and Firebase Storage."""
    # Delete video from Firestore
    db.collection('music').document(song_id).delete()
    print(f"Deleted video metadata from Firestore with ID: {song_id}")

    # Delete video file from Firebase Storage
    video_blob = bucket.blob(f'{folder_type}/songs/{file_name}')
    thumbnail_blob = bucket.blob(f'{folder_type}/thumbnails/{thumbnail_name}')
    
    video_blob.delete()
    thumbnail_blob.delete()
    print(f"Deleted video and thumbnail from Firebase Storage: {file_name} and {thumbnail_name}")


def get_video_duration(file_path):
    """Get the duration of the video in seconds."""
    try:
        video = VideoFileClip(file_path)
        duration_in_seconds = video.duration  # Duration in seconds
        video.close()  # Close the video file to free up resources
        return duration_in_seconds
    except Exception as e:
        print(f"Error getting video duration: {e}")
        return None