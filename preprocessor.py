import pandas as pd
def preprocess(df, region_df):
    """
    Preprocesses the athlete data by filtering for Summer Olympics, merging with region data,
    dropping duplicates, and one-hot encoding medal types.

    Parameters:
    - df (pd.DataFrame): DataFrame containing athlete data.
    - region_df (pd.DataFrame): DataFrame containing region (NOC) data.

    Returns:
    - pd.DataFrame: The preprocessed DataFrame.
    """
    # Ensure the required columns are present
    required_columns_df = {'Season', 'NOC', 'Medal'}
    required_columns_region_df = {'NOC'}

    if not required_columns_df.issubset(df.columns):
        raise ValueError("df is missing one of the required columns: 'Season', 'NOC', 'Medal'")
    if not required_columns_region_df.issubset(region_df.columns):
        raise ValueError("region_df is missing one of the required columns: 'NOC'")

    # Filtering for Summer Olympics
    df = df[df['Season'] == 'Summer']

    # Merge with region_df on the 'NOC' column
    df = df.merge(region_df, on='NOC', how='left')

    # Drop duplicates
    df = df.drop_duplicates()

    # One-hot encode the 'Medal' column
    df = pd.concat([df, pd.get_dummies(df['Medal'], dtype=int)], axis=1)

    return df
