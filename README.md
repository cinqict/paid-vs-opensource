# paid-vs-opensource
A project used to compare open source vs paid technologies when using weather data to predict train disruptions.

The comparions is currently between databricks and kubernetes.

(bonus: azure machine learning studio)

## Pipeline Architecture (Databricks)
![Pipeline Architecture Databricks](./docs/orchestrate-mlops-azure-databricks-01.png)
#### For the databricks approach see the [azure_databricks_version](./azure_databricks_version) folder.

## Pipeline Architecture (Kubernetes)
![Pipeline Architecture Kubernetes](./docs/kube-microservice-data-dash-pipeline.png)
#### For the kubernetes approach see the rest of this README.

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

## Minikube setup order
- mysql, upload sql data (`sql_upload.py`), middleware, dashboard

## Minikube MySQL setup and deployment
- `minikube start`
- `kubectl apply -f kubectl_deploy/mysql-pv.yaml` create the persistent volume
- `kubectl apply -f kubectl_deploy/mysql-pvc.yaml` create the persistent volume claim
- `kubectl apply -f kubectl_deploy/mysql-deployment.yaml` create the deployment
- `kubectl apply -f kubectl_deploy/mysql-service.yaml`
- `kubectl describe deployment mysql` check the deployment is running
- `kubectl get pods -l app=mysql` check the pod is running
- `kubectl describe pvc mysql-pv-claim` check the persistent volume claim is running
- Optional:
    - `kubectl run -it --rm --image=mysql:8.0 --restart=Never mysql-client -- mysql -h mysql -ppassword` connect to the mysql pod
    - `STATUS; SHOW DATABASES;` check the status and what databases are running
    - `SELECT table_name FROM information_schema.tables;` check the available tables
    - exit with `ctrl + d`
- `kubectl expose pod mysql-**********-****** --type=LoadBalancer --port=3306` expose the pod as a service
- `minikube tunnel` needs to be run in a separate terminal (optional; necessary if you are using minikube)
- `kubectl get services` check the service is running

## Minikube middleware setup and deployment
- `minikube start`
- `cd model_api`
- `eval $(minikube docker-env)` set the docker environment to minikube
- `docker compose build` build the docker image
- `kubectl run model-api --image=xgboost-api-i --image-pull-policy=Never` create the deployment
- `kubectl get pods` check the pod is running
- `kubectl expose pod model-api --type=LoadBalancer --port=8000` expose the pod as a service
- `kubectl get services` check the service is running
- because `minikube tunnel` is running from before you can now access the api at `http://localhost:8000/docs`

## Minikube setup and dashboard deployment
- Install minikube
    - `brew install minikube`
- `minikube start`
- `minikube dashboard` (optional) needs to be run in a separate terminal
- create a pod from the above docker image
  - `eval $(minikube docker-env)` set the docker environment to minikube
  - `docker compose --env-file=./.streamlit/secrets.toml build`
  - `kubectl run weather-dash --image=weather-dash-i --image-pull-policy=Never`
  - `kubectl get pods` check the pod is running
- expose the pod as a service
  - `kubectl expose pod weather-dash --type=LoadBalancer --port=8080`
  - `kubectl get services` check the service is running
- because `minikube tunnel` is running from before you can now access the dashboard at `http://localhost:8080`
- if you have issues the model not being able to be called it is likely due to changes in the IP address/ port of the middleware service. To fix this:
    - go to the function `utils.get_disruption_prediction()` and update the offending uris

## Cleanup
- `kubectl delete pods --all` delete all pods
- `kubectl delete services --all` delete all services
- `kubectl delete deployments --all` delete all deployments
- `minikube stop` stop minikube
- `minikube delete --all` delete minikube