import os
import torch
from tqdm import tqdm

def download_yolov8s():
    """Download YOLOv8s model"""
    print("Downloading YOLOv8s model...")
    
    # Create model directory if it doesn't exist
    os.makedirs('ai_model', exist_ok=True)
    model_path = os.path.join('ai_model', 'yolov8s.pt')
    
    try:
        # This will download the model using torch.hub
        model = torch.hub.load('ultralytics/yolov5', 'yolov8s', pretrained=True)
        
        # Save the model locally
        torch.save(model.state_dict(), model_path)
        print(f"\nModel downloaded successfully to: {os.path.abspath(model_path)}")
        return True
        
    except Exception as e:
        print(f"\nError downloading model: {str(e)}")
        print("\nTrying alternative download method...")
        
        try:
            # Alternative method using torch.hub.load_state_dict_from_url
            from torch.hub import load_state_dict_from_url
            
            url = 'https://github.com/ultralytics/yolov5/releases/download/v7.0/yolov8s.pt'
            state_dict = load_state_dict_from_url(url, progress=True)
            torch.save(state_dict, model_path)
            print(f"\nModel downloaded successfully to: {os.path.abspath(model_path)}")
            return True
            
        except Exception as e2:
            print(f"\nAlternative download also failed: {str(e2)}")
            return False

if __name__ == "__main__":
    download_yolov8s()
