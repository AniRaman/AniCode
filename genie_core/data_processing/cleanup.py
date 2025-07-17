import pandas as pd
import streamlit as st
def cleanup_process(df):
    #print(df)
    Fields = df[df['Output XPATH'].notna()].index.tolist()

    for index in range(1, len(Fields)):
        for i in range(Fields[index-1]+1,Fields[index]): # i in range of 2 to 4
            for col in ['Input XPATH', 'Description']:
                if pd.notna(df.at[i, col]):
                    df.at[Fields[index-1], col] = f"{df.at[Fields[index - 1], col]}, {df.at[i, col]}"
                
    df_cleaned = df.dropna(subset=['Output XPATH']).reset_index(drop=True)

    # Save the cleaned DataFrame to a new CSV file
    df_cleaned.to_csv('my_dataframe.csv', index=False)
    df_cleaned['Field'] = df_cleaned['Field'].str.strip()
    print("DataFrame cleaned and saved as 'my_dataframe.csv'")   

    # %%
    df_cleaned['Field'][0]

    # %%
    df_cleaned["Complexity"] = df_cleaned["Complexity"].fillna('C').replace('', 'C')

    # %%
    df_cleaned = df_cleaned.sort_values(by='Complexity')
    return df_cleaned

def row_extraction(specs):
# %%
    df_cleaned = cleanup_process(specs)
    s_rows = df_cleaned[df_cleaned["Complexity"] == "S"].reset_index(drop=True)
    s_rows
    # %%
    c_rows = df_cleaned[df_cleaned["Complexity"] == "C"].reset_index(drop=True)
    c_rows
    batch_size = 4
    # for i in range(0, len(s_rows), batch_size):
    #     batch = s_rows.iloc[i:i + batch_size]
    #     print(batch['Field'])
    #     batch_ids = ",".join(map(str, batch["Field"]))
    #     print(f"Map {batch_ids}")
        #print(f"Batch {i // batch_size + 1}:")
        #print(batch)
    return s_rows,c_rows

