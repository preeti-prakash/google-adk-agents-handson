import os
from pathlib import Path

from dotenv import load_dotenv
from google.cloud import bigquery

# GOOGLE_CLOUD_PROJECT comes from .env in this folder
load_dotenv(Path(__file__).parent / ".env")

PROJECT_ID = os.environ["GOOGLE_CLOUD_PROJECT"]
DATASET = "employee_mcp"
TABLE = f"{PROJECT_ID}.{DATASET}.employees"


def get_client():
    # Uses your gcloud login (ADC), same as the other Vertex AI agents
    return bigquery.Client(project=PROJECT_ID)


def run_query(sql, params=None):
    """Runs a query with named @parameters and returns the rows as dicts."""

    client = get_client()

    job_config = bigquery.QueryJobConfig(query_parameters=params or [])

    rows = client.query(sql, job_config=job_config).result()

    return [dict(row) for row in rows]


def initialize_database():

    client = get_client()

    # Dataset and table (created only if they don't exist yet)
    client.create_dataset(DATASET, exists_ok=True)

    schema = [
        bigquery.SchemaField("id", "INTEGER", mode="REQUIRED"),
        bigquery.SchemaField("name", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("department", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("role", "STRING", mode="REQUIRED"),
    ]

    client.create_table(bigquery.Table(TABLE, schema=schema), exists_ok=True)

    # Insert demo data only if table is empty
    count = run_query(f"SELECT COUNT(*) AS count FROM `{TABLE}`")[0]["count"]

    if count == 0:

        run_query(f"""
            INSERT INTO `{TABLE}` (id, name, department, role)
            VALUES
                (101, 'Preeti', 'Cloud Engineering', 'Cloud Engineer'),
                (102, 'John', 'Data Engineering', 'Data Engineer'),
                (103, 'Sarah', 'AI Engineering', 'AI Engineer')
        """)


if __name__ == "__main__":
    initialize_database()
    print(f"Database initialized: {TABLE}")
