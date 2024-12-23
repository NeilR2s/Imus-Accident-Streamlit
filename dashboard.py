import streamlit as st
import plotly.express as px
import pandas as pd
import os
import warnings

warnings.filterwarnings('ignore')

# Streamlit App Configuration
st.set_page_config(page_title='Dashboard', page_icon=':bar_chart:', layout='wide')
st.title(':vertical_traffic_light: Imus City Vehicle Accident Dashboard')
st.markdown('<style>div.block-container{padding-top: 1.5rem}</style>', unsafe_allow_html=True)

# File Upload and Default Dataset Handling
data = st.file_uploader(':file_folder: Upload a file', type=['csv'])
if data is not None:
    file_name = data.name
    st.write(f'Uploaded File: {file_name}')
    df = pd.read_csv(data)
else:
    # Default dataset if no file uploaded
    default_path = 'C:/Users/Neil/Documents/artus/dlsud/codessey/dashboard/imus_accidents.csv'
    df = pd.read_csv(default_path)



# Data Preprocessing
df = df.convert_dtypes()  # Apply type conversion before creating the CSV
df['dateCommitted'] = pd.to_datetime(df['dateCommitted'])
df['timeCommitted'] = pd.to_datetime(df['timeCommitted'], format='%H:%M:%S').dt.time


# Date Range Filter
st.sidebar.header('Filter Data')

start_date = df['dateCommitted'].min()
end_date = df['dateCommitted'].max()

search_start_date = st.sidebar.date_input('Start Date', start_date)
search_end_date = st.sidebar.date_input('End Date', end_date)

if search_start_date > search_end_date:
    st.error('Start date must be earlier than or equal to end date.')
else:
    df = df[(df['dateCommitted'] >= pd.to_datetime(search_start_date)) &
            (df['dateCommitted'] <= pd.to_datetime(search_end_date))]

# Barangay Filter
barangay = st.sidebar.multiselect('Select Barangay', options=df['barangay'].unique(), default=None)
if barangay:
    df = df[df['barangay'].isin(barangay)]
 
# Incident Type Filter
incident_types = st.sidebar.multiselect('Select Incident Type', options=df['incidentType'].unique(), default=None)
if incident_types:
    df = df[df['incidentType'].isin(incident_types)]

# Offense Filter
offenses = st.sidebar.multiselect('Select Offense', options=df['offense'].unique(), default=None)
if offenses:
    df = df[df['offense'].isin(offenses)]

# Download Filtered Data
st.sidebar.markdown('---')
csv = df.to_csv(index=False).encode('utf-8')
st.sidebar.download_button('Download Filtered Data', data=csv, file_name='filtered_data.csv', mime='text/csv')

# Data Visualization
st.subheader('Visualizations')

col1, col2 = st.columns(2)

# Bar Chart: Incidents by Barangay
with col1:
    st.subheader('Incidents by Barangay')
    barangay_incidents = df.groupby('barangay').size().reset_index(name='count')
    fig1 = px.bar(barangay_incidents, x='barangay', y='count',
                  title='Number of Incidents per Barangay', text='count', template='seaborn')
    st.plotly_chart(fig1, use_container_width=True)

# Pie Chart: Incident Types Distribution
with col2:
    st.subheader('Incident Types Distribution')
    incident_summary = df.groupby('incidentType').size().reset_index(name='count')
    fig2 = px.pie(incident_summary, names='incidentType', values='count',
                  title='Incident Types Distribution', hole=0.4)
    st.plotly_chart(fig2, use_container_width=True)

# Line Chart: Incidents Over Time
st.subheader('Incidents Over Time')
time_series = df.groupby(df['dateCommitted'].dt.to_period('M')).size().reset_index(name='count')
time_series['dateCommitted'] = time_series['dateCommitted'].dt.strftime('%Y-%m')
fig3 = px.line(time_series, x='dateCommitted', y='count',
               title='Incidents Over Time', markers=True, template='plotly_white')
st.plotly_chart(fig3, use_container_width=True)

with st.expander('View Data of TimeSeries:'):
    st.write(time_series.T.style.background_gradient(cmap='Blues'))

# Scatter Plot: Relationship Between Offense and Time Committed
st.subheader('Scatter Plot: Offenses vs. Time Committed')
fig4 = px.scatter(df, x='timeCommitted', y='offense',
                  title='Offenses vs. Time Committed', color='incidentType',
                  labels={'timeCommitted': 'Time Committed', 'offense': 'Offense'})
st.plotly_chart(fig4, use_container_width=True)

# Example: Aggregate data for treemap
df_treemap = df.groupby(['barangay', 'incidentType', 'offenseType'], as_index=False).size()
df_treemap.rename(columns={'size': 'count'}, inplace=True)

# Create Treemap
st.subheader('Hierarchical view of Offenses using TreeMap')
fig3 = px.treemap(
    df_treemap,
    path=['barangay', 'incidentType', 'offenseType'],  # Hierarchical structure
    values='count',  # Value for treemap size
    hover_data=['count'],  # Data to display on hover
    color='count',  # Use the count as the color
    color_continuous_scale='Viridis'  # Color scale for visualization
)

fig3.update_layout(width=800, height=650, margin=dict(t=50, l=25, r=25, b=25))
st.plotly_chart(fig3, use_container_width=True)

# Data Preview Section
st.subheader('Data Preview')
with st.expander('View Filtered Data'):
    st.write(df.style.background_gradient(cmap='Blues'))

# Download Original Dataset
st.download_button('Download Original Data', data=pd.read_csv(default_path).to_csv(index=False).encode('utf-8'),
                   file_name='original_data.csv', mime='text/csv')

