import pandas as pd
import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import scipy
import plotly.figure_factory as ff
import gdown
import os

import helper
import preprocessor

    
# Google Drive file IDs for the datasets (replace with your actual IDs)
athletes_file_id = '1JWzWfjiWeOYzTFHRzVCbZwyrPYR4E4t7'
noc_regions_file_id = '1ykB_swmmzqDN0X6D98VGfeQjzvqqfbMX'

# URLs to download the datasets
athletes_url = f'https://drive.google.com/uc?id={athletes_file_id}'
noc_regions_url = f'https://drive.google.com/uc?id={noc_regions_file_id}'

# Function to download the dataset if not already present
def download_dataset(file_id, local_filename):
    os.makedirs(os.path.dirname(local_filename), exist_ok=True)
    if not os.path.exists(local_filename):
        gdown.download(file_id, local_filename, quiet=False)

# Check if the datasets exist and download them if necessary
download_dataset(athletes_url, 'data/athlete_events.csv')
download_dataset(noc_regions_url, 'data/noc_regions.csv')

# Load datasets after ensuring they're downloaded
try:
    df = pd.read_csv('data/athlete_events.csv')
    region_df = pd.read_csv('data/noc_regions.csv')
except FileNotFoundError as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# Preprocess data
df = preprocessor.preprocess(df, region_df)

# Display a note about data accuracy
st.markdown("""
**Note:** The data used in this analysis may contain inaccuracies due to historical geographic changes. Many countries have merged or formed over time, which can affect the attribution of Olympic medals and other data points.
""")

# Sidebar for user options

# Customizing Sidebar Title with Markdown and Emoji
st.sidebar.markdown("""
# 🏅 **OlympicStats** 
_Your ultimate source for Olympic data analysis_  
""", unsafe_allow_html=True)

# User menu for selecting the type of analysis
user_menu = st.sidebar.radio(
    'Select an option',
    ('Medal Tally', 'Overall Analysis', 'Country-wise Analysis', 'Athlete-wise Analysis')
)

# Function to render Medal Tally analysis
def render_medal_tally(df):
    st.sidebar.header("Medal Tally")
    years, country = helper.country_year_list(df)

    selected_year = st.sidebar.selectbox('Select Year', years)
    selected_country = st.sidebar.selectbox('Select Country', country)

    # Fetch medal tally based on user selection
    medal_tally = helper.fetch_medal_tally(df, selected_year, selected_country)

    # Define the title based on user selection
    if selected_year == 'Overall' and selected_country == 'Overall':
        st.title('Overall Tally')
    elif selected_year != 'Overall' and selected_country == 'Overall':
        st.title(f"Medal Tally in {selected_year} Olympics")
    elif selected_year == 'Overall' and selected_country != 'Overall':
        st.title(f"{selected_country}'s Overall Performance")
    else:
        st.title(f"{selected_country}'s Performance in {selected_year} Olympics")

    # Display the medal tally table
    st.table(medal_tally)


# Function to render Overall Analysis
def render_overall_analysis(df):
    # Compute overall statistics
    editions = df['Year'].unique().shape[0] - 1
    cities = df['City'].unique().shape[0]
    sports = df['Sport'].unique().shape[0]
    events = df['Event'].unique().shape[0]
    athletes = df['Name'].unique().shape[0]
    nations = df['region'].unique().shape[0]

    # Display overall statistics
    st.title("Top Statistics")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.header("Editions")
        st.title(editions)
    with col2:
        st.header("Hosts")
        st.title(cities)
    with col3:
        st.header("Sports")
        st.title(sports)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.header("Events")
        st.title(events)
    with col2:
        st.header("Nations")
        st.title(nations)
    with col3:
        st.header("Athletes")
        st.title(athletes)

    # Plotting trends over time
    nations_overtime = helper.data_overtime(df, 'region')
    st.title("Participating Nations over the years")
    fig = px.line(nations_overtime, x='Edition', y='region')
    st.plotly_chart(fig)

    events_overtime = helper.data_overtime(df, 'Event')
    st.title("Events over the years")
    fig = px.line(events_overtime, x='Edition', y='Event')
    st.plotly_chart(fig)

    athletes_overtime = helper.data_overtime(df, 'Name')
    st.title("Athletes over the years")
    fig = px.line(athletes_overtime, x='Edition', y='Name')
    st.plotly_chart(fig)

    # Heatmap for number of events over time
    st.title("No. of Events over time (Every Sport)")
    fig, ax = plt.subplots(figsize=(10, 10))
    x = df.drop_duplicates(['Year', 'Sport', 'Event'])
    ax = sns.heatmap(
        x.pivot_table(index='Sport', columns='Year', values='Event', aggfunc='count').fillna(0).astype(
            'int'), annot=True
    )
    st.pyplot(fig)

    # Most successful athletes
    st.title("Most Successful Athletes")
    sport_list = df['Sport'].unique().tolist()
    sport_list.sort()
    sport_list.insert(0, 'Overall')
    selected_sport = st.selectbox('Select a Sport', sport_list)
    x = helper.most_successful(df, selected_sport)
    st.table(x.head(20))


# Function to render Country-wise Analysis
def render_country_analysis(df):
    st.sidebar.title('Country-wise Analysis')
    country_list = df['region'].dropna().unique().tolist()
    country_list.sort()
    selected_country = st.sidebar.selectbox('Select a country', country_list)

    # Medal tally over the years for the selected country
    country_df = helper.year_wise_medal_tally(df, selected_country)
    fig = px.line(country_df, x='Year', y='Medal')
    st.title(f"{selected_country} Medal Tally over the years")
    st.plotly_chart(fig)

    # Heatmap of performance by sport
    st.title(f"{selected_country} Performance by Sports")
    pt = helper.country_event_heatmap(df, selected_country)
    fig, ax = plt.subplots(figsize=(10, 10))
    if len(pt) > 0:
        ax = sns.heatmap(pt, annot=True)
        st.pyplot(fig)
    else:
        st.warning("No data available.")

    # Top 10 athletes of the selected country
    st.title(f"Top 10 Athletes of {selected_country}")
    top10_df = helper.most_successful_country_wise(df, selected_country)
    st.table(top10_df.head(10))


# Function to render Athlete-wise Analysis
def render_athlete_analysis(df):
    athlete_df = df.drop_duplicates(subset=['Name', 'region'])

    # Distribution of age by medal type
    x1 = athlete_df['Age'].dropna()
    x2 = athlete_df[athlete_df['Medal'] == 'Gold']['Age'].dropna()
    x3 = athlete_df[athlete_df['Medal'] == 'Silver']['Age'].dropna()
    x4 = athlete_df[athlete_df['Medal'] == 'Bronze']['Age'].dropna()

    fig = ff.create_distplot(
        [x1, x2, x3, x4],
        ['Overall Age', 'Gold Medalist', 'Silver Medalist', 'Bronze Medalist'],
        show_hist=False, show_rug=False
    )
    st.title("Distribution of Age")
    st.plotly_chart(fig)

    # Distribution of age by sport for gold medalists
    x = []
    name = []
    famous_sports = [
        'Basketball', 'Judo', 'Football', 'Tug-Of-War', 'Athletics', 'Swimming', 'Badminton', 'Sailing',
        'Gymnastics', 'Art Competitions', 'Handball', 'Weightlifting', 'Wrestling', 'Water Polo',
        'Hockey',
        'Rowing', 'Fencing', 'Shooting', 'Boxing', 'Taekwondo', 'Cycling', 'Diving', 'Canoeing',
        'Tennis',
        'Golf', 'Softball', 'Archery', 'Volleyball', 'Synchronized Swimming', 'Table Tennis',
        'Baseball',
        'Rhythmic Gymnastics', 'Rugby Sevens', 'Beach Volleyball', 'Triathlon', 'Rugby', 'Polo',
        'Ice Hockey'
    ]

    for sport in famous_sports:
        temp_df = athlete_df[athlete_df['Sport'] == sport]
        x.append(temp_df[temp_df['Medal'] == 'Gold']['Age'].dropna())
        name.append(sport)

    fig = ff.create_distplot(x, name, show_hist=False, show_rug=False)
    st.title("Distribution of Age wrt Sports (Gold Medalists)")
    st.plotly_chart(fig)

    # Scatter plot for Height vs Weight
    st.title("Height V Weight")
    sport_list = df['Sport'].unique().tolist()
    sport_list.sort()
    sport_list.insert(0, 'Overall')
    selected_sport = st.selectbox('Select a Sport', sport_list)
    temp_df = helper.weigh_v_height(df, selected_sport)
    fig, ax = plt.subplots()
    ax = sns.scatterplot(x=temp_df['Weight'], y=temp_df['Height'], hue=temp_df['Medal'],
                         style=temp_df['Sex'], s=60)
    st.pyplot(fig)

    # Participation by gender over the years
    st.title("Men V Women Participation Over the Years")
    final = helper.men_women_participation(df)
    fig = px.line(final, x='Year', y=['Men', 'Women'])
    st.plotly_chart(fig)


# Render the selected analysis based on user input
if user_menu == 'Medal Tally':
    render_medal_tally(df)
elif user_menu == 'Overall Analysis':
    render_overall_analysis(df)
elif user_menu == 'Country-wise Analysis':
    render_country_analysis(df)
elif user_menu == 'Athlete-wise Analysis':
    render_athlete_analysis(df)
