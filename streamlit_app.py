import streamlit as st
from snowflake.snowpark.functions import col
import requests

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write(
    """Choose the fruits you want in your custom Smoothie!!
    """
)
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# Establish connection to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

my_dataframe = session.table("smoothies.public.fruit_options").select(col('fruit_name')).collect()

# Convert dataframe to list for multiselect
fruit_options = [row['FRUIT_NAME'] for row in my_dataframe]

ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_options,
    max_selections=5
)

if ingredients_list:
        ingredients_string = ''
    
        for fruit_chosen in ingredients_list:
                ingredients_string+=fruit_chosen + ' '
                st.subheader(fruit_chosen+ ' Nutrition Information')
                fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" +fruit_chosen)
                fv_df=st.dataframe(data=fruityvice_response.json(),use_container_width=True)
        my_insert_stmt = """ insert into smoothies.public.orders(ingredients,name_on_order)
               values ('""" + ingredients_string + """','"""+name_on_order+"""')"""

    
        time_to_insert = st.button("Submit Order")
    
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")

    # Fetch data from Fruityvice API
    
    if fruityvice_response.status_code == 200:
        st.json(fruityvice_response.json())
    else:
        st.error("Failed to fetch data from Fruityvice API")
