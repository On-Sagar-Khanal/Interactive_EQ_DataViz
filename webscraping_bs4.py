import requests
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd

"""define lists to store data"""
Date,Time,Latitude,Longitude,Magnitude,Epicenter,Remarks=[],[],[],[],[],[],[]

"""takes in data and returns processed values"""
def Parser(str,x):
    if x==0:
        return str.strip()[-10:]   #Date
    if x==1:
        return str.strip()[-5:]   #Time
    if x==4:
        return float(str)    #local magnitude
    if x==6:
        return str.strip()           #Epicentre location name
    if x==5:
        return str.strip()           #Remarks
    
"""function to return rows"""
def RowsPreserver(list):
   a=[]
   N = len(list)/8
   for n in range(0,int(N)):
       a.append(list[:8])
       list=list[8:]
   return a[1:]

url = 'https://seismonepal.gov.np/earthquakes'
r = requests.get(url)
soup = BeautifulSoup(r.text,'html.parser')
rows=soup.find_all('tr')

list=[]
for row in rows:            #use this, meaning, first scrape it all in a list then divide it into individaul data knowing the numer we have
    for cell in row:
        if cell.text.strip != '\n':
           list.append(cell.text.strip())
cleaned_list = [element for element in list if element != '']
# print(cleaned_list)

first_page=RowsPreserver(cleaned_list)

"""stores all values in a list"""
for x in first_page:
    Date.append(x[0])
    Time.append(x[1])
    Latitude.append(x[2])
    Longitude.append(x[3])
    Magnitude.append(x[4])
    Epicenter.append(x[6])
    Remarks.append(x[5])

##### FOR THE REMAINING PAGES SCRAPING #####

"""retrieves the current year"""
year=int(soup.find('h2').text.strip()[14:18])
last_year=int(soup.find('h2').text.strip()[-4:])
next_year=year-1

for yr in range(next_year,(last_year-1),-1):
#  print(yr)
 url_next = url + '/' + str(yr)
 r = requests.get(url_next)
 soup = BeautifulSoup(r.text,'html.parser')
 rows=soup.find_all('tr')

 list=[]
 for row in rows:            #use this, meaning, first scrape it all in a list then divide it into individaul data knowing the numer we have
    for cell in row:
        if cell.text.strip != '\n':
           list.append(cell.text.strip())
 cleaned_list = [element for element in list if element != '']
 formatted_list=RowsPreserver(cleaned_list)
 for x in formatted_list:
    Date.append(x[0])                       #numbers denote position of these data in website row from 0 to 7 ( 8 headers were available)
    Time.append(x[1])
    Latitude.append(x[2])
    Longitude.append(x[3])
    Magnitude.append(x[4])
    Epicenter.append(x[6])
    Remarks.append(x[5])

#### SAVING TO DATAFRAME AND THEN TO CSV ###
dict_data={
    'Date':Date,
    'Time':Time,
    'Latitude':Latitude,
    'Longitude':Longitude,
    'Magnitude':Magnitude,
    'Epicenter':Epicenter,
    'Remarks':Remarks
}
df = pd.DataFrame(dict_data)
# print(df.head(19))
df = df.drop(df[df['Magnitude'] == 'NSC'].index)
df = df.dropna(subset=['Magnitude','Latitude','Longitude'])

#### Changing data to easy format ###
df['Date']=df['Date'].apply(Parser,args=(0,))
df['Time']=df['Time'].apply(Parser,args=(1,))
df['Latitude']=df['Latitude'].apply(lambda x: float(x))
df['Longitude']=df['Longitude'].apply(lambda x: float(x))
df['Magnitude']=df['Magnitude'].apply(lambda x: float(x))
df['Remarks']=df['Remarks'].apply(Parser,args=(5,))
df['Epicenter']=df['Epicenter'].apply(Parser,args=(6,))
df['YYYY']=df['Date'].apply(lambda x:str(x[:4]))
df['MM']=df['Date'].apply(lambda x:str(x[5:7]))
df['DD']=df['Date'].apply(lambda x:str(x[8:]))
df.drop('Date',inplace=True,axis=1)
df['Date']=df['MM'] + '/'+ df['DD'] + '/'+ df['YYYY']
### SAVING FINAL DATAFRAME ###
df.to_csv('data.csv')
print(df.head())
print(df.dtypes)
print('Total number of earthquake data scrapped = ',len(df))

print(df[df['Magnitude']>=6])
