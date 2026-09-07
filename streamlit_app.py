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
).select(
    col("FRUIT_NAME"),
    col("SEARCH_ON")
)

pd_df = my_dataframe.to_pandas()

ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    pd_df["FRUIT_NAME"],
    max_selections=5
)

if ingredients_list:
    ingredients_string = ""

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "

        search_on = pd_df.loc[
            pd_df["FRUIT_NAME"] == fruit_chosen,
            "SEARCH_ON"
        ].iloc[0]

        st.write(
            "The search value for",
            fruit_chosen,
            "is",
            search_on,
            "."
        )

        st.subheader(
            f"{fruit_chosen} Nutrition Information"
        )

        api_fruit_name = search_on.lower()

        smoothiefroot_response = requests.get(
            f"https://my.smoothiefroot.com/api/fruit/{api_fruit_name}"
        )

        if smoothiefroot_response.status_code == 200:

            sf_df = pd.DataFrame(
                [smoothiefroot_response.json()]
            )

            st.dataframe(
                data=sf_df,
                use_container_width=True
            )

        else:

            st.warning(
                f"Nutrition information for {fruit_chosen} "
                "is not available."
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
