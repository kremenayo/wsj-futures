# -*- coding: utf-8 -*-
"""
Created on Sun Aug 22 08:28:19 2021

@author: Kremena Yordanova
"""

import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_table as dt
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import dash_table
import numpy as np
import requests
from bs4 import BeautifulSoup
from datetime import date
import re

headers = {'User-Agent': 'Brave'}
 
# Function - create table
def generate_table(dataframe, max_rows=26):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns]) ] +
        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    )


# Parameters
today = date.today()
title = "Цени на земеделските култури"
subtitle = "към дата "+ str(today)

# Scraping EUR USD
link = 'https://finviz.com/forex.ashx'
rq = requests.get(link, headers=headers)
soup = BeautifulSoup(rq.text, 'html.parser')

l = soup.find_all(string=True)
l = [i for i in l if i.startswith('\r\n                (function()')]
n = l[0].find('"EURUSD","last":')
eurusd = l[0][n+16:n+16+7].replace(",",'')
eurusd = eval(eurusd)
bgnusd = round(1/eurusd * 1.95583, 5)


# Script ZAR USD
link = 'https://www.xe.com/currencyconverter/convert/?Amount=1&From=ZAR&To=USD'
rq = requests.get(link, headers=headers)
soup = BeautifulSoup(rq.text, 'html.parser')
l = soup.find_all(string=True)
l = [i for i in l if i != ' ']
n = l.index('Convert South African Rand to US Dollar')
zarusd = eval(l[n+5])

'''
# Scraping Sunflower
link = 'https://www.barchart.com/futures/quotes/HL*0/futures-prices'
rq = requests.get(link, headers=headers)
soup = BeautifulSoup(rq.text, 'html.parser')
l = soup.find_all(string=True)
l = [i for i in l if i != ' ']

soup.find_all(class_=re.compile("bc-datatable"))
soup.find_all(href=re.compile("HL"))
test = soup.find_all('a')
'''

# Scraping Wheat
link = 'https://www.wsj.com/market-data/quotes/futures/W00/contracts'
rq = requests.get(link, headers=headers)
soup = BeautifulSoup(rq.text, 'html.parser')

l = soup.find_all(string=True)
l = [i for i in l if i != ' ']

#s = l.index('data-module-name="quotes.module.webui/lib/wsj/navstrap"')
s = l.index('MONTH')
e = l.index('data-module-name="quotes.module.contracts.Module"')

l0 = l[s:e]
l1 = l0[::12]
l2 = l0[1::12]
l3 = l0[2::12]

df = pd.DataFrame([l1,l2,l3]).T
new_header = df.iloc[0,:]
df = df.iloc[1:,:]
df.columns = new_header
df['LAST'] = df['LAST'].astype('f')/100
df['CHG'] = df['CHG'].astype('f')/100

df['LAST'] = df['LAST'].apply(lambda x: round(x, 2))
df['CHG'] = df['CHG'].apply(lambda x: round(x, 2))
df['USD_tons'] = df["LAST"] * 36.7437
df['USD_tons'] = df['USD_tons'].apply(lambda x: round(x, 2))

df['BGN'] = df['USD_tons'] * bgnusd
df['BGN'] = df['BGN'].apply(lambda x: round(x, 2))
df['BGN_kg'] = (df['BGN']/1000).apply(lambda x: round(x, 2))

df.columns = ['Месец', 'Цена бушел USD', 'Промяна бушел USD', 'Цена тон USD','Цена тон BGN', 'Цена кг BGN']
df.iloc[:,0] = df.iloc[:,0].str.replace('Wheat ','')
months = {'en': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
          'bg': ['Януари', 'Февруари', 'Март', 'Април', 'Май', 'Юни', 'Юли',
                 'Август', 'Септември', 'Октомври', 'Ноември', 'Декември']}

ids = dict(zip(months['en'], months['bg']))

df.iloc[:,0] = df.iloc[:,0].replace(ids, regex=True)
df.iloc[:,0] = df.iloc[:,0].str.replace('Front Month', 'Текущ месец')


# Scraping Corn
link = 'https://www.wsj.com/market-data/quotes/futures/CORN/contracts'
rq = requests.get(link, headers=headers)
soup = BeautifulSoup(rq.text, 'html.parser')

l = soup.find_all(string=True)
l = [i for i in l if i != ' ']

#s = l.index('data-module-name="quotes.module.webui/lib/wsj/navstrap"')
s = l.index('MONTH')
e = l.index('data-module-name="quotes.module.contracts.Module"')

l_test = l[s:e]
l1 = l_test[::12]
l2 = l_test[1::12]
l3 = l_test[2::12]

df1 = pd.DataFrame([l1,l2,l3]).T
new_header = df1.iloc[0,:]
df1 = df1.iloc[1:,:]
df1.columns = new_header
df1['LAST'] = df1['LAST'].astype('f')/100
df1['CHG'] = df1['CHG'].astype('f')/100

df1['LAST'] = df1['LAST'].apply(lambda x: round(x, 2))
df1['CHG'] = df1['CHG'].apply(lambda x: round(x, 2))
df1['USD_tons'] = df1["LAST"] * 39.36825
df1['USD_tons'] = df1['USD_tons'].apply(lambda x: round(x, 2))

df1['BGN'] = df1['USD_tons'] * bgnusd
df1['BGN'] = df1['BGN'].apply(lambda x: round(x, 2))
df1['BGN_kg'] = (df1['BGN']/1000).apply(lambda x: round(x, 2))

df1.columns = ['Месец', 'Цена бушел USD', 'Промяна бушел USD', 'Цена тон USD','Цена тон BGN', 'Цена кг BGN']
df1.iloc[:,0] = df1.iloc[:,0].str.replace('Corn ','')

df1.iloc[:,0] = df1.iloc[:,0].replace(ids, regex=True)
df1.iloc[:,0] = df1.iloc[:,0].str.replace('Front Month', 'Текущ месец')


# App
stylesheet = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=stylesheet)
server = app.server
app.layout = html.Div([
    html.Div([],
             style={'width': '5%', 'display': 'inline-block'}),
    html.Div([
        html.Div([html.Br(),
            html.H1(title, style={'color':'#003B73', 'textAlign': 'left'}),
            html.Blockquote(subtitle, style={'textAlign': 'left'}),
            html.B('Валутни курсове', style={'color':'#003B73', 'textAlign': 'left'}),
            html.Section("EUR/USD  " + str(eurusd) + "  |  USD/BGN  " + str(bgnusd), style={'textAlign': 'left'})
            #html.Section(text_l1),
            #html.Section(text_l2),
            #html.Section(text_l3),
            ]),
        html.Hr(),
        html.Div([html.Div(children=[html.H4(children='Пшеница'), generate_table(df.iloc[:4,:])])]),
        html.Br(),
        html.Div([html.Div(children=[html.H4(children='Царевица'), generate_table(df1.iloc[:4,:])])]),
        html.Br(),
        html.Hr(), 
        html.Section('Цени пшеница и царевица - Чикагска Стокова Борса (Chicago Board of Trade)',style={'textAlign': 'left'}),
        html.Section('EUR/USD валутен курс https://finviz.com/forex.ashx',style={'textAlign': 'left'}),
        html.Section('EUR/BGN валутен курс 1.95583',style={'textAlign': 'left'}),
        html.Br()
        ],
        style={'width': '90%', 'display': 'inline-block'}),
            html.Div([],
             style={'width': '5%', 'display': 'inline-block'})])

if __name__ == '__main__':
    app.run_server(debug=True)