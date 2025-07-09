# Task 1 Part A: ML Pipeline with MLflow and Flask API

## Overview
This task implements a complete machine learning pipeline for Titanic passenger survival prediction. The pipeline includes data ingestion, model training with MLflow tracking, and deployment as a Flask REST API.

## Architecture

### System Components
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Data          │    │   Model         │    │   Model         │
│   Ingestion     │───▶│   Training      │───▶│   Deployment    │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Titanic       │    │   MLflow        │    │   Flask API     │
│   Dataset       │    │   Tracking      │    │   Service       │
│   (CSV)         │    │                 │    │   (Port 5001)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Data Flow
1. **Data Ingestion** (`data_ingestion.py`): Downloads and processes Titanic dataset
2. **Model Training** (`model_training.py`): Trains RandomForest model with MLflow logging
3. **Model Deployment** (`model_deployment.py`): Validates model deployment readiness
4. **Flask API** (`app.py`): Serves predictions via REST endpoints

## Project Structure
```
Task_1_A/
├── src/
│   ├── data_ingestion.py      # Data loading and preprocessing
│   ├── model_training.py      # ML model training with MLflow
│   ├── model_deployment.py    # Deployment validation
│   └── ml_pipeline_dag.py     # Airflow DAG (future use)
├── app.py                     # Flask API server
├── requirements.txt           # Python dependencies
├── models/                    # Generated model files
│   ├── titanic_data.csv
│   ├── titanic_model.pkl
│   ├── sex_encoder.pkl
│   └── embarked_encoder.pkl
└── README.md
```

## Features

### Machine Learning Pipeline
- **Dataset**: Titanic passenger survival prediction
- **Model**: RandomForest classifier with scikit-learn
- **Features**: Pclass, Sex, Age, SibSp, Parch, Fare, Embarked
- **Target**: Survival prediction (0/1)
- **Accuracy**: ~80% on test set

### MLflow Integration
- Experiment tracking and model versioning
- Parameter and metric logging
- Model registry for deployment
- Web UI for experiment comparison

### Flask API Endpoints
- `GET /health` - Service health check
- `POST /predict` - Passenger survival prediction
- `GET /example` - Sample input format

## Technical Notes

### Spark Integration
Spark was originally intended for distributed preprocessing and feature engineering. However, due to local resource limitations and the scope of this task, the current implementation uses Pandas-based transformations for simplicity and reproducibility in a containerized setup.

### Model Performance
The RandomForest model achieves approximately 80% accuracy on the Titanic dataset using basic feature engineering including:
- Missing value imputation
- Categorical encoding (Sex, Embarked)
- Feature selection and scaling

## Setup Instructions

### Prerequisites
- Python 3.8+
- pip package manager
- Terminal/Command prompt access

### Installation
1. Navigate to project directory:
```bash
cd Task_1_A
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

### Step 1: Execute ML Pipeline
Run the following commands in Terminal 1:
```bash
python src/data_ingestion.py
python src/model_training.py
python src/model_deployment.py
python app.py
```

### Step 2: Start MLflow Server
In Terminal 2:
```bash
cd Task_1_A
mlflow server --host 127.0.0.1 --port 5000
```

### Step 3: Test API
In Terminal 3 (PowerShell):
```powershell
$body = @{
    pclass = 3
    sex = 'male'
    age = 22
    sibsp = 1
    parch = 0
    fare = 7.25
    embarked = 'S'
} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:5001/predict" -Method POST -Body $body -ContentType "application/json"
```

## API Usage

### Health Check
```bash
curl http://localhost:5001/health
```

### Example Input Format
```bash
curl http://localhost:5001/example
```

### Prediction Request
```json
{
    "pclass": 3,
    "sex": "male",
    "age": 22,
    "sibsp": 1,
    "parch": 0,
    "fare": 7.25,
    "embarked": "S"
}
```

### Expected Response
```json
{
    "prediction": 0,
    "survival_status": "Did not survive",
    "survival_probability": "23.45%",
    "death_probability": "76.55%"
}
```

## Accessing MLflow UI
- Open browser: `http://127.0.0.1:5000`
- View experiments, runs, and model metrics
- Compare different model versions
- Download trained models

## Troubleshooting

### Common Issues
1. **Port conflicts**: Ensure ports 5000 and 5001 are available
2. **Module not found**: Run `pip install -r requirements.txt`
3. **Model not loaded**: Execute data_ingestion.py and model_training.py first
4. **MLflow connection**: Verify MLflow server is running on port 5000

### File Dependencies
- Models must be trained before API deployment
- MLflow server should be running for experiment tracking
- All model files are stored in `models/` directory

## Future Enhancements
- Spark integration for distributed processing
- Docker containerization for deployment
- Automated model retraining pipeline
- Enhanced feature engineering
- Model performance monitoring
- A/B testing capabilities