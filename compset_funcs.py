import pandas as pd
import requests

api_key = "f3898958-b76a-4a47-816f-0294f0c5103d"

BASE_URL = "https://api.hellodata.ai"

HEADERS = {
    "x-api-key": api_key
}

def fetch_property_data(property, lat=None, lon=None, zip_code=None):
    """Function to fetch property data using property name and zip code."""
    querystring = {"q": property}

    # Only add lat and lon if they are provided
    if lat is not None and lon is not None:
        querystring["lat"] = lat
        querystring["lon"] = lon
        querystring["max_distance"] = 0.2

    if zip_code is not None:
        querystring['zip_code'] = zip_code

    url = f"{BASE_URL}/property/search"
    response = requests.get(url, headers=HEADERS, params=querystring)
    try:
        data = response.json()
        return data if data and len(data) > 0 else None
    except ValueError as e:
        raise ValueError(f"Error parsing JSON response from property search: {e}")

def fetch_property_details(property_id):
    """Function to fetch details for a specific property."""
    url = f"{BASE_URL}/property/{property_id}"
    response = requests.get(url, headers=HEADERS)
    try:
        return response.json()
    except ValueError as e:
        raise ValueError(f"Error parsing JSON response from property details: {e}")
    
def fetch_comparables(property_details, params):
    """Function to fetch HelloData comparables for a given property using a POST request."""
    url = f"{BASE_URL}/property/comparables"
    payload = {"subject": property_details}

    # Filter only the allowed parameters to be included in query string
    allowed_params = {
        "topN", "renovations", "maxDistance", "minDistance",
        "minNumberUnits", "maxNumberUnits", 
        "minYearBuilt", "maxYearBuilt", 
        "minNumberStories", "maxNumberStories"
    }

    # Construct filtered query parameters
    query_params = {k: v for k, v in params.items() if k in allowed_params}

    response = requests.post(url, headers=HEADERS, params=query_params, json=payload)

    if response.status_code == 200:
        return response.json()
    else:
        return None

def aggregate_comps(comps_json, property_details):

    if comps_json is None:
        return None

    # Extract subject property info
    subject_name = property_details.get('building_name')
    subject_address = f"{property_details.get('street_address', '')}, {property_details.get('city', '')}, {property_details.get('state', '')}"
    subject_year_built = property_details.get('year_built')
    subject_number_units = property_details.get('number_units')
    subject_number_stories = property_details.get('number_stories')

    # Initialize DataFrame with subject property
    comps_df = pd.DataFrame([{
        'Property Name': subject_name,
        'Address': subject_address,
        'Year Built': subject_year_built,
        'Number of Units': subject_number_units,
        'Number of Stories': subject_number_stories,
        'Reference': True
    }])

    # Append comps
    for i in range(len(comps_json)):
        cur = comps_json[i]

        property_name = cur.get('building_name')
        address = f"{cur.get('street_address', '')}, {cur.get('city', '')}, {cur.get('state', '')}"
        year_built = cur.get('year_built')
        number_units = cur.get('number_units')
        number_stories = cur.get('number_stories')
        similarity_score = cur.get('similarity_score').get('overall')
        distance = cur.get('distance_miles')

        comps_df = pd.concat([comps_df, pd.DataFrame([{
            'Property Name': property_name,
            'Similarity Score': round(similarity_score, 3),
            'Distance (Mi.)': round(distance, 2),
            'Year Built': year_built,
            'Number of Units': number_units,
            'Number of Stories': number_stories,
            'Address': address,
            'Reference': False
        }])], ignore_index=True)

    return comps_df
