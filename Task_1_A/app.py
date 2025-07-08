from flask import Flask, request, jsonify
import joblib
import pandas as pd
import numpy as np

app = Flask(__name__)

# Load model and encoders
try:
    model = joblib.load('models/titanic_model.pkl')
    sex_encoder = joblib.load('models/sex_encoder.pkl')
    embarked_encoder = joblib.load('models/embarked_encoder.pkl')
    print("✅ Titanic model and encoders loaded successfully!")
except:
    model = None
    sex_encoder = None
    embarked_encoder = None
    print("❌ Model not found. Run the pipeline first.")

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy', 
        'model_loaded': model is not None,
        'model_type': 'Titanic Survival Predictor'
    })

@app.route('/predict', methods=['POST'])
def predict():
    if model is None:
        return jsonify({'error': 'Model not loaded'}), 500
    
    try:
        data = request.get_json()
        
        # Expected features: Pclass, Sex, Age, SibSp, Parch, Fare, Embarked
        features = pd.DataFrame([{
            'Pclass': data['pclass'],
            'Sex': sex_encoder.transform([data['sex']])[0],
            'Age': data['age'],
            'SibSp': data['sibsp'],
            'Parch': data['parch'],
            'Fare': data['fare'],
            'Embarked': embarked_encoder.transform([data['embarked']])[0]
        }])
        
        # Make prediction
        prediction = model.predict(features)[0]
        probability = model.predict_proba(features)[0]
        
        survival_status = "Survived" if prediction == 1 else "Did not survive"
        
        return jsonify({
            'prediction': int(prediction),
            'survival_status': survival_status,
            'survival_probability': f"{probability[1]:.2%}",
            'death_probability': f"{probability[0]:.2%}"
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/example', methods=['GET'])
def example():
    return jsonify({
        'example_input': {
            'pclass': 3,
            'sex': 'male',
            'age': 22,
            'sibsp': 1,
            'parch': 0,
            'fare': 7.25,
            'embarked': 'S'
        },
        'description': {
            'pclass': 'Passenger class (1=First, 2=Second, 3=Third)',
            'sex': 'male or female',
            'age': 'Age in years',
            'sibsp': 'Number of siblings/spouses aboard',
            'parch': 'Number of parents/children aboard',
            'fare': 'Ticket fare',
            'embarked': 'Port of embarkation (S=Southampton, C=Cherbourg, Q=Queenstown)'
        },
        'usage': 'POST this JSON to /predict'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)