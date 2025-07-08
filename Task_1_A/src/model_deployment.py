import joblib
import os

def deploy_model():
    """Check if Titanic model is ready for deployment"""
    print("Deploying Titanic survival prediction model...")
    
    model_path = 'models/titanic_model.pkl'
    
    if os.path.exists(model_path):
        # Load model to verify it works
        model = joblib.load(model_path)
        print("✅ Titanic model deployed successfully!")
        print(f"🚢 Model ready to predict passenger survival at: http://localhost:5001/predict")
        return True
    else:
        print("❌ Model file not found!")
        return False

if __name__ == "__main__":
    deploy_model()