import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

sns.set(style='dark')

def create_daily_bike_df(df):
    daily_bike_df = df.groupby("hour").total_count_x.sum().reset_index()
    return daily_bike_df

def create_weekly_bike_df(df):
    weekly_bike_df = df.groupby("weekday_y").total_count_x.sum().reset_index()
    days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    for i in range(7):
        weekly_bike_df['weekday_y'][i] = days[i]
    return weekly_bike_df

def create_weather_bike_df(df):
    weather_bike_df = df.groupby('weather_condition_x').total_count_x.sum().reset_index()
    weather = ['Clear', 'Cloudy', 'Light Rain', 'Heavy Rain']
    for i in range(4):
        weather_bike_df['weather_condition_x'][i] = weather[i]
    return weather_bike_df

def create_anomalies_dates_df(df):
    bydays_df = df.groupby('datetime').agg({
        'datetime': 'max',
        "anomaly": 'max',
        'count_change':'max',
    }) # Buat mengambil satu elemen saja karena ada 24 duplikat per tanggal
    bydays_df = bydays_df.sort_index(ascending=False)
    anomaly_df = bydays_df[bydays_df['anomaly'] == True]
    return anomaly_df

def max_per_hour_index(df):
    max = df['total_count_x'].max()
    index = 0
    for i in range(24):
        if df['total_count_x'][i] == max:
            index = i
            break
    return index

def max_per_day_index(df):
    max = df['total_count_x'].max()
    index = 0
    for i in range(7):
        if df['total_count_x'][i] == max:
            index = i
            break
    return index

def extract_year(data):
    return data.strftime('%Y')

def extract_date_month(data):
    month = ['January', 'February', 'March', 'April', 'May', 'June',
             'July', 'August', 'September', 'October', 'November', 'December']
    month_data = month[int(data.strftime('%m'))-1]
    date_data = data.strftime('%d')
    return f'{date_data} {month_data}'

all_df = pd.read_csv("dashboard/all_data.csv")

all_df.sort_values(by="datetime", inplace=True)
all_df.reset_index(inplace=True)
all_df['datetime'] = pd.to_datetime(all_df['datetime'])

min_date = all_df["datetime"].min()
max_date = all_df["datetime"].max()
     
with st.sidebar:
    # Menambahkan logo perusahaan
    #
    #
    st.image("dashboard/bicycle.png")
        
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = all_df[(all_df["datetime"] >= str(start_date)) & 
        (all_df["datetime"] <= str(end_date))]

daily_bike_df = create_daily_bike_df(main_df)
weekly_bike_df = create_weekly_bike_df(main_df)
weather_bike_df = create_weather_bike_df(main_df)
anomalies_df = create_anomalies_dates_df(main_df)

st.header('Bike Share')
 
col1, col2, col3 = st.columns(3)
 
with col1:
    total_count = daily_bike_df.total_count_x.sum()
    st.metric("Total Bike", value=total_count)
 
with col2:
    max_value = daily_bike_df.total_count_x.max()
    st.metric("Maximum (per hour)", value=max_value)


with col3:
    min_value = daily_bike_df.total_count_x.min()
    st.metric("Minimum (per hour)", value=min_value)
     
fig, ax = plt.subplots(figsize=(16, 8))
     
colors = ["#D3D3D3" for i in range(24)]
colors[max_per_hour_index(daily_bike_df)] = "#90CAF9"
     
sns.barplot(x="hour", y="total_count_x", data=daily_bike_df, palette=colors)
ax.set_ylabel('Total Bike', fontsize=30)
ax.set_xlabel('Hour', fontsize=30)
ax.set_title("Daily Bike Share (per Hour)", loc="center", fontsize=40)
ax.tick_params(axis='y', labelsize=35)
ax.tick_params(axis='x', labelsize=30)

st.pyplot(fig)

col1, col2, col3 = st.columns(3)
 
with col1:
    total_count = weekly_bike_df.total_count_x.sum()
    st.metric("Total Bike", value=total_count)
 
with col2:
    max_value = weekly_bike_df.total_count_x.max()            
    st.metric("Maximum (per day)", value=max_value)

with col3:
    min_value = weekly_bike_df.total_count_x.min()
    st.metric("Minimum (per day)", value=min_value)
     
fig, ax = plt.subplots(figsize=(20, 10))
     
colors = ["#D3D3D3" for i in range(7)]
colors[max_per_day_index(weekly_bike_df)] = "#90CAF9"
     
sns.barplot(x="weekday_y", y="total_count_x", data=weekly_bike_df, palette=colors)
ax.set_ylabel('Total Bike', fontsize=30)
ax.set_xlabel('Day', fontsize=30)
ax.set_title("Weekly Bike Share (per Day)", loc="center", fontsize=40)
ax.tick_params(axis='y', labelsize=35)
ax.tick_params(axis='x', labelsize=30)
     
st.pyplot(fig)

col1, col2= st.columns(2)
 
with col1:
    max_value = weather_bike_df.total_count_x.max()
    max_weather = None
    for i in range(weather_bike_df['total_count_x'].count()):
        if weather_bike_df['total_count_x'][i] == max_value:
            max_weather = weather_bike_df['weather_condition_x'][i]
    st.metric("Best Weather for Bike Share", value=max_weather)

with col2:
    min_value = weather_bike_df.total_count_x.min()
    min_weather = None
    for i in range(weather_bike_df['total_count_x'].count()):
        if weather_bike_df['total_count_x'][i] == min_value:
            min_weather = weather_bike_df['weather_condition_x'][i]
    st.metric("Worst Weather for Bike Share", value=min_weather)
     
fig, ax = plt.subplots(figsize=(20, 10))
     
colors = ["#D3D3D3" for i in range(4)]
colors[0] = "#90CAF9"
     
sns.barplot(x="total_count_x", y="weather_condition_x", data=weather_bike_df.sort_values(by="total_count_x", ascending=False), palette=colors)
ax.set_ylabel('Weather', fontsize=30)
ax.set_xlabel('Total Bike', fontsize=30)
ax.set_title("Bike Share based on Weather", loc="center", fontsize=40)
ax.tick_params(axis='y', labelsize=35)
ax.tick_params(axis='x', labelsize=30)
     
st.pyplot(fig)

st.subheader('Previous Anomalies')

if anomalies_df['datetime'].count() == 0:
    st.text('No Anomalies Found')

group = anomalies_df['datetime'].count() // 3
remainder_group = anomalies_df['datetime'].count() % 3

for i in range(group):

    col1, col2, col3 = st.columns(3)
     
    with col1:
        st.metric(value=f"{extract_date_month(anomalies_df['datetime'][3*i])}", 
                label=f"{extract_year(anomalies_df['datetime'][3*i])}", 
                delta=f"{anomalies_df['count_change'][3*i]}"
                )
     
    with col2:
        st.metric(value=f"{extract_date_month(anomalies_df['datetime'][3*i+1])}", 
                label=f"{extract_year(anomalies_df['datetime'][3*i+1])}", 
                delta=f"{anomalies_df['count_change'][3*i+1]}"
                )
    
    with col3:
        st.metric(value=f"{extract_date_month(anomalies_df['datetime'][3*i+2])}", 
                label=f"{extract_year(anomalies_df['datetime'][3*i+2])}", 
                delta=f"{anomalies_df['count_change'][3*i+2]}"
                )

if remainder_group == 1:
    st.metric(value=f"{extract_date_month(anomalies_df['datetime'][group*3])}", 
            label=f"{extract_year(anomalies_df['datetime'][group*3])}", 
            delta=f"{anomalies_df['count_change'][group*3]}"
            )
elif remainder_group == 2:
    col1, col2, col3 = st.columns(3)
 
    with col1:
        st.metric(value=f"{extract_date_month(anomalies_df['datetime'][group*3])}", 
                label=f"{extract_year(anomalies_df['datetime'][group*3])}", 
                delta=f"{anomalies_df['count_change'][group*3]}"
                )
 
    with col2:
        st.metric(value=f"{extract_date_month(anomalies_df['datetime'][group*3+1])}", 
            label=f"{extract_year(anomalies_df['datetime'][group*3+1])}", 
            delta=f"{anomalies_df['count_change'][group*3+1]}"
            )
    