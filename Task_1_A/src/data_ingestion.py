import pandas as pd
import numpy as np
import os

def ingest_data():
    """Download and load Titanic dataset from Kaggle"""
    print("Loading Titanic dataset from Kaggle...")
    print("Dataset info: Predict passenger survival on Titanic")
    
    # Create models directory
    os.makedirs('models', exist_ok=True)
    
    # Download Titanic dataset (simplified version)
    url = "https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv"
    
    try:
        # Load dataset from GitHub (mirror of Kaggle Titanic dataset)
        df = pd.read_csv(url)
        print("✅ Titanic dataset loaded successfully!")
    except:
        print("❌ Could not download dataset, creating sample data...")
        # Fallback: create sample Titanic-like data
        np.random.seed(42)
        n_samples = 891
        
        df = pd.DataFrame({
            'PassengerId': range(1, n_samples + 1),
            'Pclass': np.random.choice([1, 2, 3], n_samples, p=[0.2, 0.2, 0.6]),
            'Sex': np.random.choice(['male', 'female'], n_samples, p=[0.65, 0.35]),
            'Age': np.random.normal(30, 12, n_samples).clip(1, 80),
            'SibSp': np.random.poisson(0.5, n_samples),
            'Parch': np.random.poisson(0.4, n_samples),
            'Fare': np.random.exponential(30, n_samples),
            'Embarked': np.random.choice(['S', 'C', 'Q'], n_samples, p=[0.7, 0.2, 0.1])
        })
        
        # Create realistic survival based on features
        survival_prob = (
            0.2 +  # base survival rate
            0.5 * (df['Sex'] == 'female') +  # women more likely to survive
            0.3 * (df['Pclass'] == 1) +  # first class more likely
            0.1 * (df['Pclass'] == 2) -  # second class slight advantage
            0.01 * (df['Age'] - 30)  # age factor
        ).clip(0, 1)
        
        df['Survived'] = np.random.binomial(1, survival_prob)
    
    print(f"Features: {list(df.columns)}")
    print(f"Dataset shape: {df.shape}")
    print(f"Survival rate: {df['Survived'].mean():.2%}")
    
    # Save to CSV
    df.to_csv('models/titanic_data.csv', index=False)
    
    print(f"Dataset saved: {df.shape[0]} passengers")
    return df

if __name__ == "__main__":
    ingest_data()