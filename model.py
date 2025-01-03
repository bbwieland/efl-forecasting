import pandas as pd
import etl

raw_data = pd.read_csv("match_data.csv")
model_data, coords = etl.format_data_for_stan(input_df=raw_data)

