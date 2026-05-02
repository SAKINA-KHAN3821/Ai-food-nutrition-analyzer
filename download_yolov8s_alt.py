import os
from ultralytics import YOLO

def download_yolov8s():
    """Download YOLOv8s model using ultralytics package"""
    print("Downloading YOLOv8s model...")
    
    # Create model directory if it doesn't exist
    os.makedirs('ai_model', exist_ok=True)
    model_path = os.path.join('ai_model', 'yolov8s.pt')
    
    try:
        # This will automatically download the model if not found locally
        model = YOLO('yolov8s.pt')
        print(f"\nModel downloaded and loaded successfully!")
        print(f"Model architecture: {model.model}")
        
        # Save the model locally
        model.save(model_path)
        print(f"\nModel saved to: {os.path.abspath(model_path)}")
        return True
        
    except Exception as e:
        print(f"\nError downloading model: {str(e)}")
        return False

if __name__ == "__main__":
    download_yolov8s()
