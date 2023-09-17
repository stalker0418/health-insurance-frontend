import pandas as pd

df = pd.read_csv('insurance.csv')




grouped = df.groupby('INSURANCE_COMPANY')


dataframes_dict = {}

for company, group in grouped:
    dataframes_dict[company] = group.reset_index(drop=True)  # Reset the index for each group









