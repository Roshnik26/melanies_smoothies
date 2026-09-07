# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")

st.write(
    """
    Choose the fruits you want in your custom Smoothie!
    """
)

name_on_order = st.text_input("Name on Smoothie:")

st.write(
    "The name on your Smoothie will be:",
    name_on_order
)

cnx = st.connection("snowflake")
session = cnx.session()

my_dataframe = session.table(
    "smoothies.public.fruit_options"
).select(col("FRUIT_NAME"))

ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    my_dataframe,
    max_selections=5
)

if ingredients_list:
    ingredients_string = ""

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "

        # Display nutrition information for each selected fruit
        st.subheader(f"{fruit_chosen} Nutrition Information")

        # Convert the selected fruit name for the API
        api_fruit_name = fruit_chosen.lower()

        # API uses "apple" instead of "apples"
        if api_fruit_name == "apples":
            api_fruit_name = "apple"

        smoothiefroot_response = requests.get(
            f"https://my.smoothiefroot.com/api/fruit/{api_fruit_name}"
        )

        # Convert API response into a dataframe
        sf_df = pd.DataFrame(
            [smoothiefroot_response.json()]
        )

        st.dataframe(
            data=sf_df,
            use_container_width=True
        )

    st.write("Your smoothie will be:")
    st.write(ingredients_string)

    time_to_insert = st.button("Submit Order")

    if time_to_insert:
        my_insert_stmt = """
            INSERT INTO smoothies.public.orders
                (ingredients, name_on_order)
            VALUES (?, ?)
        """

        session.sql(
            my_insert_stmt,
            params=[ingredients_string, name_on_order]
        ).collect()

        st.success("Your smoothie has been ordered!")
