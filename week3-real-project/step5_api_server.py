"""Step 5: API Server - Deploy model as REST API"""
from fastapi import FastAPI
app = FastAPI()
print("STEP 5: REST API SERVER")
print("Run: uvicorn step5_api_server:app --reload")
