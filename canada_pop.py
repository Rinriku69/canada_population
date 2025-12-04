import streamlit as st
import pandas as pd
import numpy as np


URL = "quarterly_canada_population.csv"

@st.cache_data
def read_data():   
    df = pd.read_csv(URL, dtype={'Quarter': str, 
                                'Canada': np.int32,
                                'Newfoundland and Labrador': np.int32,
                                'Prince Edward Island': np.int32,
                                'Nova Scotia': np.int32,
                                'New Brunswick': np.int32,
                                'Quebec': np.int32,
                                'Ontario': np.int32,
                                'Manitoba': np.int32,
                                'Saskatchewan': np.int32,
                                'Alberta': np.int32,
                                'British Columbia': np.int32,
                                'Yukon': np.int32,
                                'Northwest Territories': np.int32,
                                'Nunavut': np.int32})
    return df

df = read_data()
#Seperate ['Qurter'] -> ['Quarter'],['Year'] make ['Period'] : ['Quarter'] + '-' + ['Year']
df[['Quarter','Year']] = df['Quarter'].str.split(' ',expand=True)
df['Year'] = df['Year'].apply(int)
df['Period'] = df['Year'].astype(str) + '-' + df['Quarter']

#Make Choices to put in selectbox
#quarter = sorted(list(dict.fromkeys(df['Quarter'])))
quarter = sorted(list(df['Quarter'].unique().tolist()))
#years = sorted(list(dict.fromkeys(df['Year'])))
years = sorted(list(df['Year'].unique().tolist()))


location = [i for i in df.columns[1:-2]]

#------------------------------------------#
st.title("Population of Canada")

#Example data
with st.expander("See data table"):
    st.write(df)

#Input form
with st.form("key_form"):
    col1, col2, col3 = st.columns(3)
    col1.write("From : ")
    from_quarter = col1.selectbox("Quarter",options=quarter,key='from_q')
    from_year = col1.slider("Year",min_value=years[0],max_value=years[-1],step=1,key='from_y')
    col2.write("To : ")
    to_quarter = col2.selectbox("Quarter",options=quarter,key='to_q')
    to_year = col2.slider("Year",min_value=years[0],max_value=years[-1],step=1,key='to_y')
    col3.write("Choose Location : ")
    location_select = col3.selectbox("City",options=location)
    st.form_submit_button("Analyst",type='primary')

#Variables to check if empty or not
start_check = df[(df['Quarter'] == from_quarter) & (df['Year'] == from_year)]
end_check = df[(df['Quarter'] == to_quarter) & (df['Year'] == to_year)]

start_period = f"{from_year}-{from_quarter}"
end_period   = f"{to_year}-{to_quarter}"
#make another df to filter value within period
df_plot = df[(df['Period'] >= start_period) & (df['Period'] <= end_period)]

#some error handling
if from_year > to_year :
    st.text("Invalid years input")
elif start_check.empty:
    st.text("No available information")
elif end_check.empty:
    st.text("No available information")

#real output
else:
    
    st.divider()
    #make tap for Population changes and Compare
    tab1, tab2 = st.tabs(['Population Change','Compare'])
    tab1.subheader(f"Population change from {from_quarter} {from_year} to {to_quarter} {to_year}")
    #Population changes outputs
    with tab1.container():
     col1, col2 = st.columns(2)
     
     #get population values
     from_pop_value = df[(df['Quarter'] == from_quarter) & (df['Year'] == from_year)][location_select].values[0]
     to_pop_value = df[(df['Quarter'] == to_quarter) & (df['Year'] == to_year)][location_select].values[0]
     
     #LEFT SIDE(col1)
     #show the values 
     col1.write(f"From **{from_quarter} {from_year}**")
     col1.write(f"## {from_pop_value:,}")
     
     col1.write(f"To **{to_quarter} {to_year}**")
     col1.write(f"## {to_pop_value:,}")
     
     col1.divider()
     #metric
     metric_value = to_pop_value-from_pop_value
     metric_delta = round(((to_pop_value-from_pop_value)/from_pop_value)*100,2)
     col1.metric(label="Diffrent",value=f"{metric_value:,}",delta=f"{metric_delta}%")
     multiplier = 10000000  
     df_plot[location_select] = df_plot[location_select] / multiplier

     #Chart 
     col2.line_chart(df_plot,x='Period',y=location_select,y_label="Population")
     
    with tab2.container():
        st.subheader("Compare with other location")
        multi_location = st.multiselect("Location",options=location,default=location_select)
        tab2.line_chart(df_plot,x='Period',y=multi_location) 