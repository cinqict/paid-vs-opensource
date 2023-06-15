## Azure databricks version instructions
- create a new azure databricks workspace from portal.azure.com
- launch the workspace
- create a new cluster
- ingest data (training data in `../data`)
- run the ML.ipynb notebook in a databricks notebook/ workspace
- click "use model for inference" from models tab and copy the code from "query endpoint" section
- create a new token (click on user settings and generate new token) and save it as DATABRICKS_TOKEN in your environment variables
- run `python test_endpoint.py` in your local python environment to test the endpoint, if you get a prediction as a response, you are good to go!
- run `streamlit run dashboard.py` to launch the dashboard

## Clean up
- delete the cluster and workspace from azure portal