# Databricks notebook source
# MAGIC %pip install -U -qqqq mlflow mlflow-skinny

# COMMAND ----------

import mlflow

# COMMAND ----------

# MAGIC %md
# MAGIC ## Application configuration
# MAGIC
# MAGIC To begin with, we simply need to configure the following:
# MAGIC 1. `RAG_APP_NAME`: The name of the RAG application.  Used to name the app's Unity Catalog model and is prepended to the output Delta Tables + Vector Indexes
# MAGIC 2. `UC_CATALOG` & `UC_SCHEMA`: [Create a Unity Catalog](https://docs.databricks.com/en/data-governance/unity-catalog/create-catalogs.html#create-a-catalog) and a Schema where the output Delta Tables with the parsed/chunked documents and Vector Search indexes are stored
# MAGIC 3. `UC_MODEL_NAME`: Unity Catalog location to log and store the chain's model
# MAGIC 4. `VECTOR_SEARCH_ENDPOINT`: [Create a Vector Search Endpoint](https://docs.databricks.com/en/generative-ai/create-query-vector-search.html#create-a-vector-search-endpoint) to host the resulting vector index
# MAGIC 5. `SOURCE_PATH`: A [UC Volume](https://docs.databricks.com/en/connect/unity-catalog/volumes.html#create-and-work-with-volumes) that contains the source documents for your application.
# MAGIC 6. `MLFLOW_EXPERIMENT_NAME`: MLflow Experiment to track all experiments for this application.  Using the same experiment allows you to track runs across Notebooks and have unified lineage and governance for your application.
# MAGIC 7. `EVALUATION_SET_FQN`: Delta Table where your evaluation set will be stored.  In the POC, we will seed the evaluation set with feedback you collect from your stakeholders.
# MAGIC
# MAGIC After finalizing your configuration, optionally run `01_validate_config` to check that all locations exist. 

# COMMAND ----------

class GlobalConfig:
    def __init__(self):
        self.user_email = "juan_tello@epam.com"
        self.user_name = self.user_email.split("@")[0].replace(".", "").lower()[:35]
        
        self.RAG_APP_NAME = 'deepseek_rag'
        self.UC_CATALOG = 'main'
        self.UC_SCHEMA = 'test_lt'
        self.UC_MODEL_NAME = f"{self.UC_CATALOG}.{self.UC_SCHEMA}.{self.RAG_APP_NAME}"
        self.VECTOR_SEARCH_ENDPOINT = f'{self.user_name}_vector_search'
        self.SOURCE_PATH = f"/Volumes/{self.UC_CATALOG}/{self.UC_SCHEMA}/docs"
        self.EVALUATION_SET_FQN = f"`{self.UC_CATALOG}`.`{self.UC_SCHEMA}`.{self.RAG_APP_NAME}_evaluation_set"
        self.MLFLOW_EXPERIMENT_NAME = f"/Users/{self.user_email}/{self.RAG_APP_NAME}"
        self.POC_DATA_PIPELINE_RUN_NAME = "data_pipeline_poc"
        self.POC_CHAIN_RUN_NAME = "reduced-chunk-size"

    def print_config(self):
        print(f"RAG_APP_NAME {self.RAG_APP_NAME}")
        print(f"UC_CATALOG {self.UC_CATALOG}")
        print(f"UC_SCHEMA {self.UC_SCHEMA}")
        print(f"UC_MODEL_NAME {self.UC_MODEL_NAME}")
        print(f"VECTOR_SEARCH_ENDPOINT {self.VECTOR_SEARCH_ENDPOINT}")
        print(f"SOURCE_PATH {self.SOURCE_PATH}")
        print(f"EVALUATION_SET_FQN {self.EVALUATION_SET_FQN}")
        print(f"MLFLOW_EXPERIMENT_NAME {self.MLFLOW_EXPERIMENT_NAME}")
        print(f"POC_DATA_PIPELINE_RUN_NAME {self.POC_DATA_PIPELINE_RUN_NAME}")
        print(f"POC_CHAIN_RUN_NAME {self.POC_CHAIN_RUN_NAME}")

# Create global config instance
global_config = GlobalConfig()

# try: 
#     mlflow.set_experiment(global_config.MLFLOW_EXPERIMENT_NAME)
# except Exception as e:
#     print(f"Error setting MLflow experiment: {e}")

global_config.print_config()

# COMMAND ----------

import yaml 

with open("global_config.yaml", "w") as f:
    yaml.dump(global_config.__dict__, f)

# COMMAND ----------
