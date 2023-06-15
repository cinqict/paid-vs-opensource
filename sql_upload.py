# %%
import os
from sqlalchemy import create_engine
import pandas as pd
from dotenv import load_dotenv, find_dotenv
from glob import glob

# %%
_ = load_dotenv(find_dotenv())

# %%
# mysql+pymysql://<user>:<password>@<host>[:<port>]/<dbname>
check_engine = create_engine(os.environ.get("MYSQL_CONNECT_URL"))

# %%
try:
    if "train_data" not in pd.read_sql_query("SHOW DATABASES;", check_engine)["Database"].tolist():
        pd.read_sql_query("CREATE DATABASE train_data;", check_engine)
except:
    print("This result object does not return rows. It has been closed automatically.")

train_engine = create_engine(os.environ.get("MYSQL_CONNECT_URL") + "train_data")

# %%
df = pd.concat(
    [pd.read_csv(f) for f in glob("data/*.csv")], axis=0, ignore_index=True
)
# %%
try:
    df.to_sql("raw_data", train_engine, if_exists="fail", index=False)
except ValueError:
    print("Table already exists")
# %%
df = pd.read_sql_query("SELECT * FROM raw_data;", train_engine)
# %%
df
# %%
