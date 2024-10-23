import firebase_admin
from firebase_admin import credentials, firestore, storage
import os

# Path to your Firebase credentials JSON file
cred = credentials.Certificate(os.path.join(os.path.dirname(__file__), "../firebase_credentials.json"))

# Initialize the Firebase Admin SDK
firebase_admin.initialize_app(cred, {
    'storageBucket': 'clipfarmer-f8a79.appspot.com'
})

# Initialize Firestore and Firebase Storage
db = firestore.client()
bucket = storage.bucket()

def upload_file_to_storage(file_path, file_name, folder_type, file_type):
    """Uploads a file to Firebase Storage (video or thumbnail) and returns its public URL."""
    blob = bucket.blob(f'{folder_type}/{file_type}/{file_name}')
    blob.upload_from_filename(file_path)
    blob.make_public()
    print(f"{file_type.capitalize()} uploaded to: {blob.public_url}")
    return blob.public_url

def add_video_metadata(title, video_url, thumbnail_url, folder_type):
    """Adds a new video document to the 'videos' collection in Firestore."""
    
    # Generate a unique ID for the document
    video_id = db.collection('videos').document().id

    # Define the video data
    video_data = {
        'title': title,
        'url': video_url,
        'thumbnail': thumbnail_url,
        'folder': folder_type,
        'id': video_id
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



def get_videos_from_folder(folder_type):
    """Fetches videos from a specified folder (Background or Overlay) in Firestore."""
    print("getting videos from", folder_type)
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
            'url': video_data.get('url')
        })
    print("RETURNING")
    return video_list



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
        'folder': folder_type,
        'id': song_id,
        'duration':duration
    }

    # Add the document to Firestore
    db.collection('music').document(song_id).set(song_data)
    print(f"Metadata for '{title}' saved in Firestore with ID: {song_id}")


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