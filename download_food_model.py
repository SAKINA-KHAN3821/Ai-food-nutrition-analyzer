import os
import urllib.request
from tqdm import tqdm

def download_file(url, filename):
    """Download a file with progress bar"""
    print(f"Downloading {filename}...")
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    # Download with progress bar
    def progress_hook(t):
        last_b = [0]
        def update_to(b=1, bsize=1, tsize=None):
            if tsize is not None:
                t.total = tsize
            t.update((b - last_b[0]) * bsize)
            last_b[0] = b
        return update_to
    
    with tqdm(unit='B', unit_scale=True, miniters=1, desc=filename) as t:
        urllib.request.urlretrieve(url, filename, reporthook=progress_hook(t))

if __name__ == "__main__":
    # Food detection model (YOLOv8s trained on Food-101)
    MODEL_URL = "https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8s-food.pt"
    MODEL_PATH = os.path.join("ai_model", "yolov8s-food.pt")
    
    try:
        download_file(MODEL_URL, MODEL_PATH)
        print("\nModel downloaded successfully!")
        print(f"Saved to: {os.path.abspath(MODEL_PATH)}")
    except Exception as e:
        print(f"Error downloading model: {str(e)}")
        print("\nPlease check your internet connection and try again.")
