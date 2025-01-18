import pandas as pd
def fetch_medal_tally(df, year, country):
    """
    Fetches the medal tally based on the given year and country.

    Parameters:
    - df (pd.DataFrame): The DataFrame containing athlete data.
    - year (str): The year for filtering, 'Overall' for all years.
    - country (str): The country for filtering, 'Overall' for all countries.

    Returns:
    - pd.DataFrame: The medal tally DataFrame.
    """
    medal_df = df.drop_duplicates(
        subset=['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal', 'region'])

    if year == 'Overall' and country == 'Overall':
        temp_df = medal_df
    elif year == 'Overall':
        temp_df = medal_df[medal_df['region'] == country]
    elif country == 'Overall':
        temp_df = medal_df[medal_df['Year'] == int(year)]
    else:
        temp_df = medal_df[(medal_df['Year'] == int(year)) & (medal_df['region'] == country)]

    if country == 'Overall':
        x = temp_df.groupby('Year').sum()[['Gold', 'Silver', 'Bronze']].sort_values('Year', ascending=False).reset_index()
    else:
        x = temp_df.groupby('region').sum()[['Gold', 'Silver', 'Bronze']].sort_values('Gold', ascending=False).reset_index()

    x['Total'] = x[['Gold', 'Silver', 'Bronze']].sum(axis=1)
    x = x.astype({'Gold': 'int', 'Silver': 'int', 'Bronze': 'int', 'Total': 'int'})

    return x

def medal_tally(df):
    """
    Calculates the total medal tally by country.

    Parameters:
    - df (pd.DataFrame): The DataFrame containing athlete data.

    Returns:
    - pd.DataFrame: The medal tally DataFrame by country.
    """
    medal_tally_df = df.drop_duplicates(subset=['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal'])
    medal_tally_df = medal_tally_df.groupby('region').sum()[['Gold', 'Silver', 'Bronze']].sort_values('Gold', ascending=False).reset_index()
    medal_tally_df['Total'] = medal_tally_df[['Gold', 'Silver', 'Bronze']].sum(axis=1)
    medal_tally_df = medal_tally_df.astype({'Gold': 'int', 'Silver': 'int', 'Bronze': 'int', 'Total': 'int'})

    return medal_tally_df

def country_year_list(df):
    """
    Generates a list of years and countries for dropdown selections.

    Parameters:
    - df (pd.DataFrame): The DataFrame containing athlete data.

    Returns:
    - tuple: A tuple containing two lists: years and countries.
    """
    years = sorted(df['Year'].unique().tolist())
    years.insert(0, 'Overall')

    countries = sorted(df['region'].dropna().unique().tolist())
    countries.insert(0, 'Overall')

    return years, countries

def data_overtime(df, col):
    """
    Calculates the number of occurrences of a column over the years.

    Parameters:
    - df (pd.DataFrame): The DataFrame containing athlete data.
    - col (str): The column for which to calculate occurrences.

    Returns:
    - pd.DataFrame: DataFrame with the number of occurrences of the column over the years.
    """
    data_overtime = df.drop_duplicates(['Year', col])[
        'Year'].value_counts().reset_index().sort_values('Year')

    data_overtime = data_overtime.rename(columns={'Year': 'Edition', 'count': col})

    return data_overtime

def most_successful(df, sport):
    """
    Finds the most successful athletes based on the number of gold medals.

    Parameters:
    - df (pd.DataFrame): The DataFrame containing athlete data.
    - sport (str): The sport to filter, 'Overall' for all sports.

    Returns:
    - pd.DataFrame: The most successful athletes DataFrame.
    """
    temp_df = df.dropna(subset=['Medal'])
    if sport != 'Overall':
        temp_df = temp_df[temp_df['Sport'] == sport]

    most_successful_df = temp_df.groupby('Name').count()['Gold'].reset_index().sort_values('Gold', ascending=False, ignore_index=True)
    most_successful_df = most_successful_df.merge(df, on='Name', how='left').drop_duplicates('Name')[['Name', 'Gold_x', 'Sport', 'region']]
    most_successful_df.rename(columns={'Name': 'Athlete', 'Gold_x': 'Gold Medals', 'region': 'Region'}, inplace=True)
    return most_successful_df

def year_wise_medal_tally(df, country):
    """
    Calculates the medal tally by year for a specific country.

    Parameters:
    - df (pd.DataFrame): The DataFrame containing athlete data.
    - country (str): The country for which to calculate medal tally.

    Returns:
    - pd.DataFrame: The year-wise medal tally DataFrame.
    """
    temp_df = df.dropna(subset=['Medal']).drop_duplicates(subset=['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal'])
    new_df = temp_df[temp_df['region'] == country]
    final_df = new_df.groupby('Year').count()['Medal'].reset_index()

    return final_df

def country_event_heatmap(df, country):
    """
    Generates a heatmap of the number of events by sport for a specific country.

    Parameters:
    - df (pd.DataFrame): The DataFrame containing athlete data.
    - country (str): The country for which to generate the heatmap.

    Returns:
    - pd.DataFrame: The pivot table for the heatmap.
    """
    temp_df = df.dropna(subset=['Medal']).drop_duplicates(subset=['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal'])
    new_df = temp_df[temp_df['region'] == country]
    heatmap_df = new_df.pivot_table(index='Sport', columns='Year', values='Medal', aggfunc='count').fillna(0)

    return heatmap_df

def most_successful_country_wise(df, country):
    """
    Finds the most successful athletes in a specific country based on the number of gold medals.

    Parameters:
    - df (pd.DataFrame): The DataFrame containing athlete data.
    - country (str): The country for which to find the most successful athletes.

    Returns:
    - pd.DataFrame: The most successful athletes DataFrame.
    """
    temp_df = df.dropna(subset=['Medal'])
    temp_df = temp_df[temp_df['region'] == country]

    most_successful_df = temp_df.groupby('Name').count()['Gold'].reset_index().sort_values('Gold', ascending=False, ignore_index=True)
    most_successful_df = most_successful_df.merge(df, on='Name', how='left').drop_duplicates('Name')[['Name', 'Gold_x', 'Sport']]
    most_successful_df.rename(columns={'Name': 'Athlete', 'Gold_x': 'Gold Medals'}, inplace=True)

    return most_successful_df

def weigh_v_height(df, sport):
    """
    Returns a DataFrame with unique athletes, their height and weight, and medal status.

    Parameters:
    - df (pd.DataFrame): The DataFrame containing athlete data.
    - sport (str): The sport to filter, 'Overall' for all sports.

    Returns:
    - pd.DataFrame: The DataFrame with athlete data filtered by sport.
    """
    athlete_df = df.drop_duplicates(subset=['Name', 'region'])
    athlete_df['Medal'].fillna('No Medal', inplace=True)
    if sport != 'Overall':
        temp_df = athlete_df[athlete_df['Sport'] == sport]
        return temp_df
    else:
        return athlete_df

def men_women_participation(df):
    """
    Calculates the number of male and female athletes participating each year.

    Parameters:
    - df (pd.DataFrame): The DataFrame containing athlete data.

    Returns:
    - pd.DataFrame: DataFrame with the number of male and female participants each year.
    """
    athlete_df = df.drop_duplicates(subset=['Name', 'region'])
    men = athlete_df[athlete_df['Sex'] == 'M'].groupby('Year').count()['Name'].reset_index()
    women = athlete_df[athlete_df['Sex'] == 'F'].groupby('Year').count()['Name'].reset_index()
    final_df = men.merge(women, on='Year', how='left')
    final_df.rename(columns={'Name_x': 'Men', 'Name_y': 'Women'}, inplace=True)
    final_df.fillna(0, inplace=True)

    return final_df
