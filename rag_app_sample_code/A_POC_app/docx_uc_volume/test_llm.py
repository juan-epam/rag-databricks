# Databricks notebook source
from langchain_community.chat_models import ChatDatabricks

model = ChatDatabricks(
    endpoint="databricks-meta-llama-3-3-70b-instruct",
    extra_params={"temperature": 0.5, 
                  "max_tokens": 1000,
                #   "top_p": 1,
                #   "repetition_penalty": 1.0,
                #   "top_k": 1,
                #   "max_new_tokens": 1000,
                #   "stop": ["\n\n"],
                  },
)

response = model.invoke("What is the capital of France?")

print(response.content)


# COMMAND ----------
