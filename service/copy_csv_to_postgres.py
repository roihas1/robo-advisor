import os
import sys
import pandas as pd
from sqlalchemy import create_engine
import django
from django.conf import settings

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'robo_advisor_project.settings')
    django.setup()
    print("DATABASES setting:", settings.DATABASES)
    # Access Django settings variables
    BASE_SERVICE_DIR = settings.BASE_SERVICE_DIR
    DATASET_LOCATION = settings.DATASET_LOCATION
    MACHINE_LEARNING_LOCATION = settings.MACHINE_LEARNING_LOCATION
    NON_MACHINE_LEARNING_LOCATION = settings.NON_MACHINE_LEARNING_LOCATION
    CLOSING_PRICES_FILE_NAME = settings.CLOSING_PRICES_FILE_NAME
    PCT_CHANGE_FILE_NAME = settings.PCT_CHANGE_FILE_NAME

    # Access Django database settings
    db_settings = settings.DATABASES['default']
    db_name = db_settings['NAME']
    db_user = db_settings['USER']
    db_password = db_settings['PASSWORD']
    db_host = db_settings['HOST']
    db_port = db_settings['PORT']

    # Create a connection to the PostgreSQL database
    engine = create_engine(f'postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')

    # Base directory containing the collections
    base_dir = os.path.join(BASE_SERVICE_DIR, 'dataset')

    # Iterate over each collection folder
    for collection_num in range(1, 5):
        collection_dir = os.path.join(base_dir, f'collection{collection_num}')

        # Iterate over includingMachineLearning and withoutMachineLearning folders
        for ml_type in [MACHINE_LEARNING_LOCATION, NON_MACHINE_LEARNING_LOCATION]:
            ml_dir = os.path.join(collection_dir, ml_type)

            # Iterate over each CSV file in the directory
            for csv_file in os.listdir(ml_dir):
                if csv_file.endswith('.csv'):
                    # Read the CSV file into a DataFrame
                    file_path = os.path.join(ml_dir, csv_file)
                    df = pd.read_csv(file_path)

                    # Create a table name based on the collection and file name
                    table_name = f'{ml_type}_{collection_num}_{os.path.splitext(csv_file)[0]}'.lower()

                    # Copy the DataFrame to the PostgreSQL table
                    df.to_sql(table_name, engine, if_exists='replace', index=False)

                    print(f"Copied {file_path} to table {table_name}")

    print("All CSV files have been copied to PostgreSQL tables.")
