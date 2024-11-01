import firebase_admin
from firebase_admin import credentials, firestore, storage,auth
import os
from moviepy.editor import VideoFileClip, AudioFileClip
from dotenv import load_dotenv
import pyrebase
# Load environment variables
load_dotenv()


# Firebase configuration from environment variables
firebase_config = {
    'authDomain': os.getenv("FIREBASE_AUTH_DOMAIN"),
    'databaseURL': os.getenv("FIREBASE_DATABASE_URL"),
    'storageBucket': os.getenv("FIREBASE_STORAGE_BUCKET"),
    'projectId': os.getenv("FIREBASE_PROJECT_ID"),
    'appId': os.getenv("FIREBASE_APP_ID")
}

# Path to your Firebase credentials JSON file
cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
cred = credentials.Certificate(cred_path)

# Initialize the Firebase Admin SDK with additional config
firebase_admin.initialize_app(cred, {
    'storageBucket': firebase_config['storageBucket'],
    'databaseURL': firebase_config['databaseURL']
})

# Initialize Firestore and Firebase Storage
db = firestore.client()
bucket = storage.bucket()



"""
# Path to your Firebase credentials JSON file
cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
cred = credentials.Certificate(cred_path)

# Initialize the Firebase Admin SDK
firebase_admin.initialize_app(cred, {
    'storageBucket': os.getenv("FIREBASE_STORAGE_BUCKET")
})

# Initialize Firestore and Firebase Storage
db = firestore.client()
bucket = storage.bucket()


"""

def get_auth():
    config = {
        "apiKey": os.getenv("FIREBASE_API_KEY"),
        "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
        "databaseURL": os.getenv("FIREBASE_DATABASE_URL"),
        "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET")
    }
    firebase = pyrebase.initialize_app(config)
    auth = firebase.auth()
    return auth


def setup_firestore_collections():
    """
    Creates the required Firestore collections: videos, scripts, and music.
    Each collection will have a sample document to initialize the structure.
    """

    # Set up 'videos' collection
    video_data = {
        'duration': 0.0,
        'folder': '',
        'id': '',
        'thumbnail': '',
        'title': '',
        'url': '',
        'uploaded': False,
        'upload_url': {
            'Instagram': '',
            'TikTok': '',
            'YouTube': ''
        }
    }
    db.collection('videos').document('sample_video').set(video_data)
    print("Initialized 'videos' collection with a sample document.")

    # Set up 'scripts' collection
    script_data = {
        'background_audio': '',
        'id': '',
        'text': '',
        'title': '',
        'url': ''
    }
    db.collection('scripts').document('sample_script').set(script_data)
    print("Initialized 'scripts' collection with a sample document.")

    # Set up 'music' collection
    music_data = {
        'duration': 0.0,
        'category': '',
        'id': '',
        'thumbnail': '',
        'title': '',
        'url': ''
    }
    db.collection('music').document('sample_music').set(music_data)
    print("Initialized 'music' collection with a sample document.")

def setup_storage_structure():
    """
    Creates the required folder structure in Firebase Storage:
    - Background/thumbnails, Background/videos
    - CreatedVideos/thumbnails, CreatedVideos/videos
    - Overlay/thumbnails, Overlay/videos
    - Music/music, Music/songs, Music/thumbnails
    - Scripts/scripts
    - VoiceOvers/audio
    """
    folder_structure = [
        "Background/thumbnails", "Background/videos",
        "CreatedVideos/thumbnails", "CreatedVideos/videos",
        "Overlay/thumbnails", "Overlay/videos",
        "Music/music", "Music/songs", "Music/thumbnails",
        "Scripts/scripts",
        "VoiceOvers/audio"
    ]

    # Create a zero-byte file to upload for initializing the folders
    dummy_file_path = "dummy.txt"
    with open(dummy_file_path, "w") as f:
        f.write("This is a placeholder file to initialize the folder structure.")

    # Create each folder in Firebase Storage by uploading a dummy file
    for folder in folder_structure:
        blob = bucket.blob(f"{folder}/placeholder.txt")
        blob.upload_from_filename(dummy_file_path)
        print(f"Initialized folder: {folder}")

    # Remove the local dummy file after upload
    os.remove(dummy_file_path)
    print("Storage structure initialized.")

# Run setup functions
"""
ONLY FOR FIRST USERS
"""
#setup_firestore_collections()
#setup_storage_structure()


def login(self):
    print("loggin in")

def upload_file_to_storage(file_path, file_name, folder_type, file_type):
    """Uploads a file to Firebase Storage (video or thumbnail) and returns its public URL."""
    blob = bucket.blob(f'{folder_type}/{file_type}/{file_name}')
    blob.upload_from_filename(file_path)
    blob.make_public()
    print(f"{file_type.capitalize()} uploaded to: {blob.public_url}")
    return blob.public_url



def add_video_metadata(title, video_url, thumbnail_url, folder_type, duration):
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
    video_list = []

    videos_ref = None
    if folder_type == "Scripts":
        video_list = get_script_metadata()
        return video_list
    elif folder_type == "Music":
        video_list = get_music_metadata()
        return video_list
    else:  
        videos_ref = db.collection('videos')
    query = videos_ref.where('folder', '==', folder_type).stream()

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


def delete_video_from_firebase(video_id, folder_type, file_name, thumbnail_name):
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


def add_song_metadata(title, url, thumbnail_url, folder_type, duration):
    """Adds a new video document to the 'videos' collection in Firestore."""
    
    # Generate a unique ID for the document
    song_id = db.collection('music').document().id

    # Define the video data
    song_data = {
        'title': title,
        'url': url,
        'thumbnail': thumbnail_url,
        'category': folder_type,
        'id': song_id,
        'duration':duration,

    }

    # Add the document to Firestore
    db.collection('music').document(song_id).set(song_data)
    print(f"Metadata for '{title}' saved in Firestore with ID: {song_id}")


def add_script_metadata(title,url,text,backgroundAudio):
    script_id = db.collection('scripts').document().id

    # Define the video data
    script_data = {
        'title': title,
        'text': text,
        'id': script_id,
        'url':url,
        'background_audio':backgroundAudio
    }

    # Add the document to Firestore
    db.collection('scripts').document(script_id).set(script_data)
    print(f"Metadata for '{title}' saved in Firestore with ID: {script_id}")

def check_if_song_exists(title):
    """Checks if a video with the given title already exists in Firestore."""
    videos_ref = db.collection('music')
    query = videos_ref.where('title', '==', title).stream()

    for doc in query:
        return True  # Title already exists
    return False


def delete_song_from_firebase(song_id, folder_type, file_name, thumbnail_name):
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
    

def get_audio_duration(file_path):
    """Get the duration of the video in seconds."""
    try:
        audio = AudioFileClip(file_path)
        duration_in_seconds = audio.duration  # Duration in seconds
        audio.close()  # Close the video file to free up resources
        return duration_in_seconds
    except Exception as e:
        print(f"Error getting video duration: {e}")
        return None
    
    
def get_script_metadata():
    script_ref = db.collection('scripts').stream()  # No 'where' filter
    script_list = []
    for doc in script_ref:
        script_data = doc.to_dict()
        script_data['id'] = doc.id  # Include the document ID
        script_list.append({
            'id': script_data.get('id'),
            'title': script_data.get('title'),
            'url': script_data.get('url'),
            'background_audio': script_data.get('background_audio'),
            'text': script_data.get('text')
        })
    
    return script_list

def get_music_metadata():
    music_ref = db.collection('music').stream()  # No 'where' filter
    music_list = []
    for doc in music_ref:
        music_data = doc.to_dict()
        music_data['id'] = doc.id  # Include the document ID
        music_list.append({
            'id': music_data.get('id'),
            'title': music_data.get('title'),
            'thumbnail': music_data.get('thumbnail'),
            'url': music_data.get('url'),
            'category': music_data.get('category'),
            'duration': music_data.get('duration')
        })
    
    return music_list
