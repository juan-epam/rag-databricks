# Databricks notebook source
# MAGIC %md # Review App Logs to Evaluation Set
# MAGIC
# MAGIC This step will bootstrap an evaluation set with the feedback that stakeholders have provided by using the Review App.  Note that you can bootstrap an evaluation set with *just* questions, so even if your stakeholders only chatted with the app vs. providing feedback, you can follow this step.
# MAGIC
# MAGIC Visit [documentation](https://docs.databricks.com/generative-ai/agent-evaluation/evaluation-set.html#evaluation-set-schema) to understand the Agent Evaluation Evaluation Set schema - these fields are referenced below.
# MAGIC
# MAGIC At the end of this step, you will have an Evaluation Set that contains:
# MAGIC
# MAGIC 1. Requests with a 👍 :
# MAGIC    - `request`: As entered by the user
# MAGIC    - `expected_response`: If the user edited the response, that is used, otherwise, the model's generated response.
# MAGIC 2. Requests with a 👎 :
# MAGIC    - `request`: As entered by the user
# MAGIC    - `expected_response`: If the user edited the response, that is used, otherwise, null.
# MAGIC 3. Requests without any feedback e.g., no 👍 or 👎
# MAGIC    - `request`: As entered by the user
# MAGIC
# MAGIC Across all of the above, if the user 👍 a chunk from the `retrieved_context`, the `doc_uri` of that chunk is included in `expected_retrieved_context` for the question.

# COMMAND ----------

# MAGIC %pip install -U -qqqq databricks-agents mlflow mlflow-skinny databricks-sdk
# MAGIC dbutils.library.restartPython()

# COMMAND ----------

# MAGIC %run ./00_config

# COMMAND ----------

# MAGIC %run ../z_eval_set_utilities

# COMMAND ----------

import pandas as pd

import mlflow

# COMMAND ----------

# MAGIC %md ## Get the request and assessment log tables
# MAGIC
# MAGIC These tables are updated every ~hour with data from the raw Inference Table.
# MAGIC
# MAGIC TODO: Add docs link to the schemas

# COMMAND ----------

w = WorkspaceClient()

active_deployments = agents.list_deployments()
active_deployment = next(
    (item for item in active_deployments if item.model_name == UC_MODEL_NAME), None
)

endpoint = w.serving_endpoints.get(active_deployment.endpoint_name)

try:
    endpoint_config = endpoint.config.auto_capture_config
except AttributeError as e:
    endpoint_config = endpoint.pending_config.auto_capture_config

inference_table_name = endpoint_config.state.payload_table.name
inference_table_catalog = endpoint_config.catalog_name
inference_table_schema = endpoint_config.schema_name

# Cleanly formatted tables
assessment_log_table_name = f"{inference_table_catalog}.{inference_table_schema}.`{inference_table_name}_assessment_logs`"
request_log_table_name = f"{inference_table_catalog}.{inference_table_schema}.`{inference_table_name}_request_logs`"

print(f"Assessment logs: {assessment_log_table_name}")
print(f"Request logs: {request_log_table_name}")


assessment_log_df = _dedup_assessment_log(spark.table(assessment_log_table_name))
request_log_df = spark.table(request_log_table_name)

# COMMAND ----------

# MAGIC %md
# MAGIC ## ETL the request & assessment logs into Evaluation Set schema
# MAGIC
# MAGIC Note: We leave the complete set of columns from the request and assesment logs in this table - you can use these for debugging any issues.

# COMMAND ----------

requests_with_feedback_df = create_potential_evaluation_set(request_log_df, assessment_log_df)

requests_with_feedback_df.columns

# COMMAND ----------

# MAGIC %md
# MAGIC ## Inspect the potential evaluation set using MLflow Tracing
# MAGIC
# MAGIC Click on the `trace` column in the displayed table to view the Trace.  You should inspect these records

# COMMAND ----------

# display(requests_with_feedback_df.select(
#     F.col("request_id"),
#     F.col("request"),
#     F.col("response"),
#     F.col("trace"),
#     F.col("expected_response"),
#     F.col("expected_retrieved_context"),
#     F.col("is_correct"),
# ))

# COMMAND ----------

# MAGIC %md
# MAGIC # Save the resulting evaluation set to a Delta Table

# COMMAND ----------

eval_set = requests_with_feedback_df[["request", "request_id", "expected_response", "expected_retrieved_context", "source_user", "source_tag"]]

# eval_set.write.format("delta").saveAsTable(EVALUATION_SET_FQN)

# COMMAND ----------

# MAGIC %pip install -U -qqqq databricks-agents langchain==0.2.11 langchain_core==0.2.23 langchain_community==0.2.10 

# COMMAND ----------

from langchain_community.chat_models import ChatDatabricks
model = ChatDatabricks(
    endpoint="databricks-meta-llama-3-3-70b-instruct",
    extra_params={"temperature": 0.0},
)

model.invoke("What is the capital of France?")

# COMMAND ----------

GOLDEN_PROMPT_TEMPLATE = '''
    Our task is to create substantive evaluation questions that test a RAG system's understanding of key concepts, methodologies, and findings. Avoid superficial details like section titles or page numbers.

    Document URI: {doc_uri}
    Context: {context}

    Create {num_questions} questions that:
    1. Focus on core technical concepts and innovations
    2. Ask about quantitative results and comparisons
    3. Probe implementation details and design choices
    4. Require synthesis of multiple pieces of information
    5. Avoid trivial factual lookups

    Good Example:
    {{
        "request": "What architectural innovations in DeepSeek-V3 enable efficient training at scale?",
        "expected_response": "DeepSeek-V3 employs a DualPipe parallelization strategy with computation-communication overlap and an auxiliary-loss-free load balancing approach to enable efficient large-scale training.",
        "expected_retrieved_context": [
            {{"doc_uri": "{doc_uri}"}}
        ]
    }}

    Bad Example (avoid):
    {{
        "request": "What is the title of section 3.2.1?",
        "expected_response": "DualPipe and Computation-Communication Overlap"
    }}

    Respond in strict JSON format:
    {{
        "questions": [
            {{
                "request": "question about key technical concept",
                "expected_response": "detailed answer requiring understanding",
                "expected_response_context": "exact text snippet from context that contains the answer",
                "expected_retrieved_context": [
                    {{"doc_uri": "{doc_uri}"}}
                ]
            }}
        ]
    }}

    Requirements:
    - Include exact context snippet in 'expected_response_context'
    - Answers must require understanding of context, not just copy
    - JSON only, no markdown or extra text
    - Validate JSON syntax carefully
'''

from typing import List, Dict
def extract_structured_response(response: str) -> List[Dict]:
    """
    Extracts structured questions from the model response and validates the format.
    
    Args:
        response: Raw response string from the model
        
    Returns:
        List of question dictionaries with request, expected_response, and expected_retrieved_context
        
    Raises:
        ValueError: If the response cannot be parsed or is invalid
    """
    import json
    from typing import List, Dict
    
    try:
        # Try to parse the JSON response
        parsed = json.loads(response)
        
        # Validate the structure
        if not isinstance(parsed, dict) or "questions" not in parsed:
            raise ValueError("Invalid response format: missing 'questions' key")
            
        questions = parsed["questions"]
        
        # Validate each question
        for q in questions:
            if not all(key in q for key in ["request", "expected_response", "expected_retrieved_context"]):
                raise ValueError("Invalid question format: missing required fields")
                
            if not isinstance(q["expected_retrieved_context"], list):
                raise ValueError("expected_retrieved_context must be a list")
                
        return questions
        
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON response: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error parsing response: {str(e)}")


# COMMAND ----------

chunked_docs_df = spark.table(destination_tables_config["chunked_docs_table_name"]).toPandas()


# COMMAND ----------

chunked_docs_df = spark.table(destination_tables_config["chunked_docs_table_name"]).toPandas()

# COMMAND ----------

import pandas as pd 
# Convert chunked docs to pandas for easier processing
chunked_docs_df = spark.table(destination_tables_config["chunked_docs_table_name"]).toPandas().sample(n=50, random_state=42)

# Initialize list to store golden questions
golden_questions = []

# Process each chunk
from tqdm import tqdm

# Initialize list to store golden questions
golden_questions = []

# Process each chunk
for index, row in tqdm(chunked_docs_df.iterrows(), total=len(chunked_docs_df)):
    doc_uri = row['path']
    context = row['chunked_text']
    chunk_id = row['chunk_id']
    
    # Generate prompt
    prompt = GOLDEN_PROMPT_TEMPLATE.format(
        doc_uri=doc_uri,
        num_questions=2,  # Generate 2 questions per chunk
        context=context
    )
    
    # Get model response
    response = model.invoke(prompt)
    
    try:
        # Extract structured questions
        questions = extract_structured_response(response.content)
        
        # Add to golden dataset
        for q in questions:
            q['source_chunk_id'] = chunk_id  # Track which chunk generated this question
            golden_questions.append(q)
            
    except ValueError as e:
        print(f"Error processing chunk {chunk_id}: {e}")

# Convert to DataFrame for easier viewing
golden_df = pd.DataFrame(golden_questions)

# Display results
print(f"Generated {len(golden_df)} evaluation questions")
display(golden_df)


# COMMAND ----------


spark.createDataFrame(golden_df).write.format("delta").mode("overwrite").option("mergeSchema", "true").saveAsTable(EVALUATION_SET_FQN)
