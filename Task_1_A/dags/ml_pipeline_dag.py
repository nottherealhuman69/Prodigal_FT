from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import sys
sys.path.append('src')

from data_ingestion import ingest_data
from model_training import train_model
from model_deployment import deploy_model

default_args = {
    'owner': 'ml-team',
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'simple_ml_pipeline',
    default_args=default_args,
    description='Simple ML Pipeline for Iris Classification',
    schedule_interval=timedelta(days=1),
    catchup=False,
)

# Define tasks
ingest_task = PythonOperator(
    task_id='ingest_data',
    python_callable=ingest_data,
    dag=dag,
)

train_task = PythonOperator(
    task_id='train_model',
    python_callable=train_model,
    dag=dag,
)

deploy_task = PythonOperator(
    task_id='deploy_model',
    python_callable=deploy_model,
    dag=dag,
)

# Set dependencies
ingest_task >> train_task >> deploy_task