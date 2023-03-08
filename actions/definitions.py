"""
Store definitions used in rasa actions (e.g., related to database).
"""

import pandas as pd

DATABASE_HOST = "mysql"
DATABASE_PASSWORD = "password"
DATABASE_PORT = 3306
DATABASE_USER = "root"


# List of preparatory activities
df_act = pd.read_excel("Activities.xlsx", 
                       converters={'Exclusion':str, 'Prerequisite':str})
# Turn exclusion and prerequisite columns into lists
df_act["Exclusion"] = [list(df_act.iloc[i]["Exclusion"].split("|")) if not pd.isna(df_act.iloc[i]["Exclusion"]) else [] for i in range(len(df_act))]
# Note: when there are multiple prerequisites, only one needs to be met
df_act["Prerequisite"] = [list(df_act.iloc[i]["Prerequisite"].split("|")) if not pd.isna(df_act.iloc[i]["Prerequisite"]) else [] for i in range(len(df_act))]
