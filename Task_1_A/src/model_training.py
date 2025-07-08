import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
import mlflow
import mlflow.sklearn
import joblib

def train_model():
    """Train Titanic survival prediction model"""
    print("Training Titanic survival model...")
    
    # Load data
    df = pd.read_csv('models/titanic_data.csv')
    
    # Basic feature engineering
    # Fill missing values
    df['Age'] = df['Age'].fillna(df['Age'].median())
    df['Embarked'] = df['Embarked'].fillna('S')
    df['Fare'] = df['Fare'].fillna(df['Fare'].median())
    
    # Select features for prediction
    features = ['Pclass', 'Sex', 'Age', 'SibSp', 'Parch', 'Fare', 'Embarked']
    X = df[features].copy()
    y = df['Survived']
    
    # Encode categorical variables
    le_sex = LabelEncoder()
    le_embarked = LabelEncoder()
    
    X['Sex'] = le_sex.fit_transform(X['Sex'])
    X['Embarked'] = le_embarked.fit_transform(X['Embarked'])
    
    # Save encoders for later use
    joblib.dump(le_sex, 'models/sex_encoder.pkl')
    joblib.dump(le_embarked, 'models/embarked_encoder.pkl')
    
    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train model (intentionally simple to get realistic accuracy)
    model = RandomForestClassifier(n_estimators=50, max_depth=5, random_state=42)
    model.fit(X_train, y_train)
    
    # Test model
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"Training samples: {len(X_train)}")
    print(f"Test samples: {len(X_test)}")
    print(f"Features used: {features}")
    print(f"Accuracy: {accuracy:.3f}")
    
    # Save model
    joblib.dump(model, 'models/titanic_model.pkl')
    
    # Log with MLflow
    try:
        mlflow.set_tracking_uri("http://127.0.0.1:5000")
        with mlflow.start_run():
            mlflow.log_param("n_estimators", 50)
            mlflow.log_param("max_depth", 5)
            mlflow.log_param("features", str(features))
            mlflow.log_metric("accuracy", accuracy)
            mlflow.sklearn.log_model(model, "model")
        print("✅ MLflow logging successful!")
    except:
        print("⚠️ MLflow not running, skipping logging (model still works!)")
    
    print(f"🎯 Model trained! Predicts Titanic passenger survival with {accuracy:.1%} accuracy")
    return accuracy

if __name__ == "__main__":
    train_model()