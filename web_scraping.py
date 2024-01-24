import collections
import csv
import requests
from bs4 import BeautifulSoup
import pymongo
def changement(ch):
    ok=False
    while ok==False:
        if not(ch[0].isdigit()):
            ch=ch[1:]
        else:
            ok=True
    return ch


respons= requests.get("https://en.wikipedia.org/wiki/List_of_largest_companies_by_revenue#cite_note-4")
soup=BeautifulSoup(respons.content,'html.parser')
tables=soup.find_all('table')
if len(tables)> 1:
    table_data=tables[1]
    rows_body=table_data.tbody.find_all('tr') if table_data.tbody else []
    data = []
    head_data=[]
    for row in rows_body[:2]:
        cells=row.find_all(['th','td'])
        for cell in cells:
            if not(cell.text.strip()) or cell.text.strip()=="USD millions":
                continue
            else:
                head_data.append(cell.text.strip())
    data.append(head_data)
    for row in rows_body[2:]:
        
        cells=row.find_all(['th','td'])
        test=row.find_all(['th','td'],{"data-sort-value":["Yes","No"]})
        row_data=[]
        for cell in cells:
            if cell.text.strip() :
                if cell.text.strip()=="...":
                    row_data.append("0")
                else:
                    row_data.append(cell.text.strip())
            else:
                row_data.append("modification")
                
        j=0
        for i in range(len(row_data)):
            if(row_data[i]=="modification"):
                row_data[i]=(test[j])["data-sort-value"]
                j+=1
        data.append(row_data)
    print("Scraping data: done")
    with open("data.csv",'w',newline="", encoding="utf-8") as f:
        wri=csv.writer(f)
        wri.writerows(data)
    print("Writing the initial data: done")
    f.close()
    with open("data.csv",'r',newline='',encoding="utf-8") as m:
        csv_reader=csv.DictReader(m)
        data=list(csv_reader)
    for i in data:
        i["Revenue"]=changement(i["Revenue"])                       
        i["Profit"]=changement(i["Profit"])
        i["Employees"]=changement(i["Employees"])
        i["Revenue per worker"]=changement(i["Revenue per worker"])
        i["Revenue"]=i["Revenue"].replace(',','')                      
        i["Profit"]=i["Profit"].replace(',','')
        i["Employees"]=i["Employees"].replace(',','')
        i["Revenue per worker"]=i["Revenue per worker"].replace(',','')
    with open("data.csv",'w',newline="", encoding="utf-8") as f:
        wri=csv.DictWriter(f,fieldnames=csv_reader.fieldnames)
        wri.writeheader()
        wri.writerows(data)
    f.close()
    print("Cleaning data: done")
else:
    print("There's no table to extract")
client=pymongo.MongoClient("mongodb://localhost:27017/")
database= client["Scraped_data"]
collection= database.list_collection_names()
for coll in collection:
    database[coll].drop()
collection= database["LCBR"]
with open("data.csv",'r',newline='',encoding="utf-8") as h:
    csv_reader=csv.DictReader(h)
    data_to_insert=list(csv_reader)
collection.insert_many(data_to_insert)
print("Storing data: done")
client.close()
