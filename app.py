import pymongo
import numpy as np
import pandas as pd 
import plotly.express as px
import streamlit as st
import time
import os

#basic dashboard setup
st.set_page_config(page_title="Real-time Dashboard",layout="wide")

#Connecting to the database
client=pymongo.MongoClient("mongodb://localhost:27017/")
database= client["Scraped_data"]
collection= database["LCBR"]

@st.cache_data
def get_data()->pd.DataFrame:
    mongodata=collection.find()
    data_list=list(mongodata)
    df=pd.DataFrame(data_list)
    df.drop(columns=["_id"],inplace=True)
    df=df.drop_duplicates()
    df=df.rename(columns={"Headquarters[note 1]":"Headquarters"})
    df["Revenue"] = pd.to_numeric(df["Revenue"], errors='coerce')
    df["Revenue"] = df["Revenue"].dropna().astype(int)
    df["Revenue per worker"] = pd.to_numeric(df["Revenue per worker"], errors='coerce')
    df["Employees"] = pd.to_numeric(df["Employees"], errors='coerce')
    df["Employees"] = df["Employees"].dropna().astype(int)
    return df
df=get_data()

#Dashboard
st.title("Live Dashboard")
country=st.selectbox("Select the country",pd.unique(df["Headquarters"]))
df=df[df["Headquarters"]==country]
placeholder=st.empty()
placeholder2=st.empty()

name_max_comp=(df.loc[df["Revenue"].idxmax()])["Name"]
revenue_max_comp=(df.loc[df["Revenue"].idxmax()])["Revenue"]
profit_max_comp=(df.loc[df["Revenue"].idxmax()])["Profit"]
count_yes=0
count_no=0
for i,row in df.iterrows():
    if row["State-owned"]=="Yes":
        count_yes+=1
    else:
        count_no+=1
with placeholder.container():
    #kpis
    kpi1,kpi2,kpi3=st.columns(3)
    kpi1.metric(label="Company",value=name_max_comp)
    kpi2.metric(label="Revenue",value=revenue_max_comp)
    kpi3.metric(label="Emplyee",value=profit_max_comp)
    #charts
    fig_col1,fig_col2=st.columns(2)
    with fig_col1:
        st.markdown("##First Chart")
        fig=px.pie(labels=(df["State-owned"].value_counts()).index,values=df["State-owned"].value_counts(),names=(df["State-owned"].value_counts()).index,title="piechart")
        fig.update_layout(showlegend=True)
        st.write(fig)
    with fig_col2:
        st.markdown("##Seconde Chart")
        fig=px.histogram(data_frame=df,x="Name",y="Profit")
        st.write(fig)
    st.markdown("### Detailed Data View")
    st.dataframe(df)
    time.sleep(1)
    #Adding Data Manually form
    st.title("Add a Company to the database")
    name=st.text_input("Enter Name of comapny: ")
    industry=st.text_input("Enter Industry: ")
    revenue=st.number_input("Enter Revenue: ")
    profit=st.number_input("Enter Profit: ")
    emp=st.number_input("Enter the Number of Employee")
    hq=st.text_input("Enter Headquarter")
    state_owned=st.radio("Is it state-owned?",["Yes","No"])
    if st.button("Add to database"):
        rank=int(df.tail(1)["Rank"])+1
        new_data={"Rank":str(rank),"Name":name,"Industry":industry,"Revenue":str(revenue),"Profit":str(profit),"Employees":str(emp),"Headquarters[note 1]":hq,"State-owned":state_owned,"Ref.":'',"Revenue per worker":str(revenue/emp)}
        collection.insert_one(new_data)
        st.success("Data added")
        os.system("streamlit run app.py")
    #Delete Data manually
    st.title("Delete Company from the Database")
    name_to_delete=st.text_input("Enter Name of comapny that you want to delete: ")
    if st.button("Delete Company"):
        data_to_delete={"Name":name_to_delete}
        collection.delete_one(data_to_delete)
        st.success("Data Deleted")
        os.system("streamlit run app.py")
client.close()