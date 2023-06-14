# paid-vs-opensource
A project used to compare open source vs paid technologies when using weather data to predict train disruptions.

## TODO list
- Choose hosting platform
    - Azure has been chosen as the hosting platform
- Terraform deployment
    - Kubernetes + Apache Airflow
    - Databricks Workspace

## Installation and Usage (python)
- Clone the repository
    - `git clone git@github.com:cinqict/paid-vs-opensource.git`
- Install dependencies
    - `pip install -r requirements.txt`
- Run the app
    - `streamlit run app.py`

## Installation and Usage (docker)
- Clone the repository
    - `git clone git@github.com:cinqict/paid-vs-opensource.git`
- Build the docker image
    - `docker compose --env-file=./.streamlit/secrets.toml build`
- Run the docker image
    - `docker run -p 8080:8080 weather-dash-i`