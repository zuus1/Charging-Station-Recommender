# EV Charging Station Recommender
This system aims to improve the convenience of electric vehicle (EV) charging by recommending charging stations based on user preferences. The user will specify their current location, search radius, charging station preferences, and activity preferences, and the system will return a map and a list of recommendations.

## Features
This system comprises the following features:
- ``app.py`` <br>
  Main code for executing this system. Sets up user interface using Streamlit, calls functions, and visualizes the results.
- ``chargers.py`` <br>
  Interacts with Open Charge Map API to find nearby charging stations.
- ``filter.py`` <br>
  Filters the charging stations based on user's charging station preferences like plug type and charging speed.
- ``prompt.py`` <br>
  Interacts with OpenAI API to extract keywords from user's activity preference.
- ``places.py`` <br>
  Interacts with Google Places API to find facilities near each charging station that satisfy user's activity preference. 

## Installation
This system requires the following libraries.

1. Streamlit
2. Requests
3. Pandas
4. json

The libraries can be installed with the command below:
```bash
pip install streamlit requests pandas python-dotenv
```

## Configuration
This system requires the following APIs.

1. Open Charge Map API <br>
  Used to find charging stations and gather charging station spec. API key can be obtained at https://openchargemap.io.

2. Google API <br>
  Used to convert address to latitude and longitude, gather data of facilities near charging stations, and embed Google Maps in user interface. API key can be obtained at https://cloud.google.com/cloud-console. Following APIs need to be enabled in API & Services setting: <br>
    - Google Geocoding API
    - Google Places API
    - Google Maps JavaScript API 

3. Open AI API <br>
  Used to extract keywords from user's activity preferences. API key can be obtained at https://platform.openai.com.

After obtaining the APIs, define the API keys as follows in ``config.py``:
```bash
OPEN_CHARGE_API_KEY=your_open_charge_map_api_key_here
GOOGLE_PLACES_API_KEY=your_google_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

## Usage 
1. Run the application <br>
   To run this system, use the command below:
    ```bash
    streamlit run app.py
    ```
2. Enter your preferences in the sidebar <br>
   - Current location (address)
   - Search radius [mi]
   - Charging speed (fast charging or normal charging)
   - Plug type (CCS1, NACS, CHAdeMO, J1772)
   - Activity preference 

3. Search <br>
   Click the Search button

4. Results <br>
   - Map displays makers for current location (blue) and charging stations (red)
   - Click on marker for details 
   - Table shows a list of recommendations of charging stations along with distances to charging stations, charging station operators, nearby facilities for the preferred acitivity and their ratings, and links to their websites.
