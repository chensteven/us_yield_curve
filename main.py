# %%
import streamlit as st
from bs4 import BeautifulSoup
import requests
import pandas as pd
import matplotlib.pyplot as plt
import altair as alt

soup = BeautifulSoup(requests.get('https://data.treasury.gov/feed.svc/DailyTreasuryYieldCurveRateData').text,'lxml')
table = soup.find_all('m:properties')
tbondvalues = []
for i in table:
    tbondvalues.append([i.find('d:new_date').text[:10],i.find('d:bc_1month').text,i.find('d:bc_2month').text,i.find('d:bc_3month').text,i.find('d:bc_6month').text,i.find('d:bc_1year').text,i.find('d:bc_2year').text,i.find('d:bc_3year').text,i.find('d:bc_5year').text,i.find('d:bc_10year').text,i.find('d:bc_20year').text,i.find('d:bc_30year').text])
ustcurve = pd.DataFrame(tbondvalues,columns=['date','1m','2m','3m','6m','1y','2y','3y','5y','10y','20y','30y'])

ustcurve.iloc[:,1:] = ustcurve.iloc[:,1:].apply(pd.to_numeric)/100
ustcurve['datetime'] = pd.to_datetime(ustcurve['date'])
ustcurve = ustcurve.sort_values('date')
ustcurve = ustcurve[ustcurve['date'] != '2017-04-14']

ustcurve_plot = pd.DataFrame()
ustcurve_plot['datetime'] = ustcurve['datetime']
ustcurve_plot['date'] = ustcurve['date']
timeframe = '10y'
ustcurve_plot[timeframe] = ustcurve[timeframe]
timeframe = '3m'
ustcurve_plot[timeframe] = ustcurve[timeframe]

inversion = ustcurve_plot
inversion['spreads'] = ustcurve_plot['10y'] - ustcurve_plot['3m']

overlay = pd.DataFrame({'y': [0.0]})

last_day =  inversion.iloc[-1]
spread_val = last_day['10y'] - last_day['3m']

second_last_day =  inversion.iloc[-2]
previous_val = second_last_day['10y'] - second_last_day['3m']

delta = spread_val - previous_val

date = last_day['date']
st.metric(label=f"Current Spread on {date}", value=spread_val, delta=delta)


vline = alt.Chart(overlay, title='Spread between 10 years minus 3 months rates').mark_rule(color='lightgray', strokeWidth=1, strokeDash=[10, 10]).encode(y='y:Q')

c = alt.Chart(inversion).mark_line(color='darkgray', strokeWidth=1).encode(x='datetime', y='spreads')

# d = alt.Chart(ustcurve_plot).mark_line(color='red').encode(
#     x='date', y='10y')

e = alt.layer(c, vline)

st.altair_chart(e, use_container_width=True)