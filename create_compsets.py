import pandas as pd
import streamlit as st
import requests
from compset_funcs import *

dimasset = pd.read_csv('data/DimAsset.csv')
dimasset = dimasset[dimasset['YearBuiltEnd'] < 2025]
assetdetailactive = pd.read_csv('data/vw_AssetDetailActive.csv', usecols=['AssetCode', 'ParentAssetName'])

dimasset = dimasset.merge(assetdetailactive, on='AssetCode')

# Streamlit UI
st.title("HelloData Comp Set Finder")

asset_names = sorted(set(dimasset['ParentAssetName']))

selected_asset = st.selectbox(label="Select Asset", options=asset_names)

selected_asset_info = dimasset[dimasset['ParentAssetName'] == selected_asset]

lat = selected_asset_info['Latitude'].values[0]
lon = selected_asset_info['Longitude'].values[0]
year_built = int(selected_asset_info['YearBuiltEnd'].values[0])
num_units = int(selected_asset_info['CurrentUnitCount'].values[0])

st.markdown(f"""
            **Year Built:** {year_built}  
            **Number of Units:** {num_units}
            """)

st.sidebar.header("Optional Parameters")
params = {
    "topN": st.sidebar.number_input("Number of Comps", value=10, step=1, format="%d", max_value=20),
    "maxDistance": st.sidebar.number_input("Max Distance (miles)", value=10.0, step=1.0),
    "minDistance": st.sidebar.number_input("Min Distance (miles)", value=0.0, step=1.0),
    "minNumberUnits": st.sidebar.number_input("Min Number of Units", value=num_units-50, step=1),
    "maxNumberUnits": st.sidebar.number_input("Max Number of Units", value=num_units+50, step=1),
    "minYearBuilt": st.sidebar.number_input("Min Year Built", value=year_built-5, step=1),
    "maxYearBuilt": st.sidebar.number_input("Max Year Built", value=year_built+5, step=1),
    "minNumberStories": st.sidebar.number_input("Min Number of Stories", value=None, step=1),
    "maxNumberStories": st.sidebar.number_input("Max Number of Stories", value=None, step=1),
}


if st.button("Fetch Comparables"):
    property_data = fetch_property_data(selected_asset, lat=lat, lon=lon)
    property_id = property_data[0]['id']

    property_details = fetch_property_details(property_id)
    comps_json = fetch_comparables(property_details, params)

    if comps_json is None:
        st.write("Invalid Input, try again")
    else:
        comps_df = aggregate_comps(comps_json['comparables'], property_details)

        # Drop Reference column for display
        display_df = comps_df.drop(columns='Reference')

        # Style to bold the reference row, drop index
        styled_df = display_df.style.apply(
            lambda row: ['font-weight: bold' if comps_df.loc[row.name, 'Reference'] else '' for _ in row], axis=1
        )

        # Render styled table without index
        st.write(styled_df.to_html(index=False, escape=False), unsafe_allow_html=True)
