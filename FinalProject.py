"""
Name: Rhea Agarwal
CS230: Section 005
Data: Airport and Country Codes
URL: Link to your web application on Streamlit Cloud (if posted)
Description:
This program analyzes global aviation data. It explores how geography determines the distribution, type, and elevation of airports around the world. 
The queries involved are: 
Which regions have the highest elevation for a specific type of airport?
How does the number of airports differ across regions?
What types and how many airports are there in specific municipalities?
It uses a bar chart, a pie chart, and a scatterplot map. 

References:
https://docs.streamlit.io/develop/api-reference/widgets/st.slider
https://deckgl.readthedocs.io/en/latest/gallery/scatterplot_layer.html
https://www.w3schools.com/python/python_ref_dictionary.asp
"""

# Imports
import streamlit as st
import pandas as pd
import pydeck as pdk
import matplotlib.pyplot as plt
import base64
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def app_setup():
    # Creates a title for the website, and formats the layout as wide
    st.set_page_config(page_title="Airport Explorer", layout="wide")
    # CSS to keep the header the same color as the background
    st.markdown("""
    <style>
    [data-testid="stHeader"] {
        background-color: #fff0f5;
    }
    [data-testid="stAppViewContainer"] {
        background-color: #fff0f5;
    }
    </style>
    """, unsafe_allow_html=True)

def load_data():
# File read in and cleans missing values
    airports = pd.read_csv("airport-codes(in).csv")
    countries = pd.read_csv("wikipedia-iso-country-codes(in).csv")
    # Makes sure that elevation is treated as a number
    airports["elevation_ft"] = pd.to_numeric(airports["elevation_ft"], errors='coerce')
    # This removes rows where elevation, municipality, or type is NaN
    # Cleans all the data
    airports = airports.dropna(subset=["elevation_ft", "municipality", "type"])
    return airports, countries

#[FUNC2P]
# Function for airports data frame, airport type, and an elevation buffer of 500 feet.
def filter_by_type_and_elevation(df, airport_type, elevation_buffer=500):
    # Returning the filtered version of the dataframe
    return df[
        # Returns the selected airport type
        (df["type"] == airport_type) &
        # And returns the selected elevation with a buffer both ways of 500 feet.
        (df["elevation_ft"] >= elevation_buffer - 500) &
        (df["elevation_ft"] <= elevation_buffer + 500)
    ]
# Function to map the countries dataframe
def create_country_mapping(countries_df):
    # Goes through two columns and turns it into a dictionary.
    return dict(zip(
        # Keys
        countries_df["Alpha-2 code"],
        # Values
        countries_df["English short name lower case"]
    ))

# I am proud of this code, because I think it is useful to be able to find the code based on the country name.
# Function to find country code based on the name
def get_country_codes(country_dict, country_name):
    # Returning a list of code, country names pairs that match the selected country
    return [
        # Loops through the dictionary with the code as the key and name as value
        (code, name)
        for code, name in country_dict.items()
        # Only return the pair when the name matches the selected one
        if name == country_name 
    ]

# I am also proud of this code, because I think it is even more useful to find a country name based on the code.
# Function to look up country name based on country code, and returns "None" if there is no code.
def get_country_name(country_dict, country_code):
    #[DICTMETHOD]
    return country_dict.get(country_code, None)

# Function to make a pie chart for airport types for a selected country.
def pie_chart(filtered_df, country_choice):
    # Counts the different types of airports for a country.
    type_counts = filtered_df["type"].value_counts()
    fig, ax = plt.subplots()
    ax.pie(
        type_counts, 
        # Labels are the airport types
        labels=type_counts.index, 
        # Presents it in a percentage
        autopct='%1.1f%%', 
        # Starts the chart at the top
        startangle=90,
        # The colors
        colors=['#ff8000', '#ffcc99', '#66b3ff', '#99ff99', '#FF0000']
    )
    # Keeps both axises equal, makes it a circle
    ax.axis('equal')  
    # Title
    plt.title(f"Distribution of Airport Types in {country_choice}")
    # Returns the modified figure
    return fig

# Function to make a bar chart for airports in a chosen municipality.
def bar_chart(df, municipality):
        #[SORT] - sorts the airports by elevation and puts the highest first. Only includes the top 15, otherwise the bar chart is too crowded.
        df = df.sort_values(by="elevation_ft", ascending=False).head(15)
        # Prints the airport name with the type in parentheses
        df["display_label"] = df["name"] + " (" + df["type"] + ")"
        #[LISTCOMP] - the names are the x-axis labels, and the elevations are the y-axis labels
        labels = [name for name in df["display_label"]]
        elevations = [e for e in df["elevation_ft"]]
        #[CHART2]
        fig, ax = plt.subplots()
        # Matches the color for elevation from the map
        def get_bar_color(elevation):
            if elevation < 1000:
                return '#0066FF'   
            elif elevation < 5000:
                return '#00AA55'   
            else:
                return '#FF6600'   
        colors = [get_bar_color(e) for e in elevations]
        # Each bar is an airport, and the height is based on elevation
        ax.bar(range(len(labels)), elevations, color=colors)  
        # Labels     
        ax.set_xlabel('Airport Name and Type', fontsize=10)
        ax.set_ylabel('Elevation (feet)', fontsize=10)
        ax.set_title(f'Airports in {municipality}', fontsize=12) 
        # Places the labels under the bars.      
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=9)
        # Returns the modified figure
        return fig

#[ST3]
def sidebar_navigation():
    with st.sidebar:
        choice = st.radio(
            "Choose a page",
            ("Home", "Elevations", "Regions", "Municipalities", "Map", "Airport Types", "Municipality Analysis", "Conclusion")
        )
    return choice

def home_page():
    # Title
    st.title("How Does Geography Shape Global Airports?")
    # Explanatory paragraph
    st.write(
    "Welcome to the interactive exploration of global airports! "
    "Use the sidebar to explore elevation, regions, and municipalities. ✈️"
)
    # Video
    video_file = open("Plane_taking_off.mp4", "rb")
    video_bytes = video_file.read()
    video_file.close()
    # CSS to keep the video autoplaying, looped, and muted
    video_base64 = base64.b64encode(video_bytes).decode()
    video_html = f"""
    <video autoplay loop muted playsinline style="width: 100%;">
    <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
    </video>
    """
    st.components.v1.html(video_html, height=400)

def elevations(airports, country_dict):
    st.header("Elevations ⛰️")
    #[ST1]
    # A dropdown menu to select the airport type
    airport_type = st.selectbox("Select Airport Type", airports["type"].unique())
    #[ST2]
    # A slider to select elevation, with the min, max, and the intervals.
    elevation = st.slider("Select Elevation", -1300, 30000, 100)
    #[FILTER2]
    # Call the function
    filtered = filter_by_type_and_elevation(airports, airport_type, elevation)
    # Subheader
    st.subheader(f"The regions with {airport_type} airports at an elevation of {elevation} are: ")
    # Finds the highest number from the filtered data, and stores it in max_elevation
    #[MAXMIN]
    max_elevation = filtered["elevation_ft"].max()
    highest = filtered[filtered["elevation_ft"] == max_elevation]
    # Displays the region and the elevation
    st.write(highest[["iso_region", "elevation_ft"]])  
    # Filters the data to only include the selected airport type
    type_only = airports[airports["type"] == airport_type]
    # Finds the highest elevation for that type
    #[MAXMIN]
    max_elevation = type_only["elevation_ft"].max()
    # Keeps only the rows which match the type and highest elevation
    highest_rows = type_only[type_only["elevation_ft"] == max_elevation]
    if not highest_rows.empty:
        region = highest_rows["iso_region"].values[0]
        st.subheader(f"Region with the Highest Elevation for {airport_type}")
        st.write(f"{region}: {max_elevation} ft")
    else:
        st.write("No data available for this selection.")
    # Dropdown to select a code
    code_choice = st.selectbox(
        "Select a code:",
        sorted(airports["iso_country"].dropna().unique()))
    # Calls the function
    country_name = get_country_name(country_dict, code_choice)
    # Prints the code to the mapped country
    st.write(f"{code_choice} -> {country_name}")
    # Subheader for the button
    st.subheader("But why?")
    # I am proud of this code, because I think a button is a fun addition, and the fact that the answer changes based on which airport type is selected.
    # If the user clicks on this button, it will print the following
    if st.button("Tell me why 👀", key="why_elevations"):
        # What gets printed depends on the airport type
        if airport_type == "heliport":
            st.write(f"The US has the highest elevation for heliports because there are mountainous regions where towns, resorts, and facilities are located \
                     for medical evacuation, and for military training sites.")
        elif airport_type == "small_airport":
            st.write(f"Peru has the highest elevation for small airports because a lot of airports are located up in the Andes due to the many cities and towns \
                     located there.")
        elif airport_type == "closed":
            st.write(f"The US has the highest elevation for closed airports because they are located in mountainous regions, and are older or unused \
                    because of changes in travel, infrastructure, or replacement.")
        elif airport_type == "seaplane_base":
            st.write(f"The US has the highest elevation for seaplane base airports because the US has seaplane lakes at higher elevations in mountainous \
                    or inland regions.")
        elif airport_type == "balloonport":
            st.write(f"The US has the highest elevation for balloon ports because balloon ports are usually located where the weather is stable and predictable, \
                    there is an open, flat space for landing, and a safe airspace, which are located in high desert or mountainous regions. Since they are at a \
                    higher elevation, there is dry air, consistent wind patterns, and a wide open terrain--all suitable for balloons.")
        elif airport_type == "medium_airport":
            st.write(f"The US has the highest elevation for medium airports because there are populated regions in high-altitude areas, and people living \
                    there need transportation.")
        elif airport_type == "large_airport":
            st.write(f"Peru has the highest elevation for large airports because majority of Peru is covered by the Andes mountains, and a lot of cities are \
                    located at high altitudes--lots of people equals a need for transportation, even at high altitudes.")

def regions(airports, country_dict):
    # Header
    st.header("Regions 🌎")
    #[ST1]
    # User can select a country from a dropdown menu
    country_choice = st.selectbox(
        "Select a country:",
        sorted(airports["country_name"].dropna().unique()))
    # Call the function
    matching_codes = get_country_codes(country_dict, country_choice)
    st.subheader("Country Code Mapping")
    # For the chosen country, it displays the matching code and country.
    for code, name in matching_codes:
        st.write(f"{code} -> {name}")
    #[FILTER1]
    # Filters the dataframe to keep rows where the country matches the country choice.
    filtered = airports[airports["country_name"] == country_choice]
    # Counts the airports and writes it.
    st.subheader(f"Number of airports in {country_choice}")
    st.write(len(filtered))
    # Groups the countries with the number of airports and sorts it in descending order.
    country_counts = airports.groupby("country_name").size().sort_values(ascending=False)
    # Takes the highest value of the index, which is the country and the highest value of the airports.
    top_country = country_counts.idxmax()
    top_count = country_counts.max()
    st.subheader("Country with the Most Airports (Global)")
    # Prints out the country with the most airports.
    if st.button("Show country"):
        st.write(f"{top_country}: {top_count} airports")
    st.subheader("But why?")
    if st.button("Tell me why 👀", key="why_regions"):
        st.write(f"The United States has the most airports because it is a large country with cities and towns spread apart, thereby needing many ports for \
                transport among them. There is a lot of transport within the country as well as people leaving and coming into the country. It has mountains, \
                deserts, islands, and rural areas which are easiest to reach by flight instead of car. Lastly, it has a strong aviation network and the \
                resources to build it and maintain it.")
        
def municipalities(airports):
    # Header
    st.header("Municipalities 🏙")
    #[ST1]
    # Drop down menu to select a municipality
    municipality_choice = st.selectbox(
        "Select a municipality:",
        sorted(airports["municipality"].dropna().unique()))
    # Filters the data set to only keep the rows which the user selected.
    filtered = airports.query("municipality == @municipality_choice")
    st.subheader(f"Number of airports in {municipality_choice}")
    # Writes out the number of airports in selected municipality. 
    st.write(len(filtered))
    municipality_counts = airports["municipality"].value_counts()
    top_municipality = municipality_counts.index[0]
    top_count = municipality_counts.values[0]
    st.subheader("Municipality with the Most Airports")
    if st.button("Show municipality"):
        st.write(f"{top_municipality}: {top_count} airports")
    st.subheader("But why?")
    if st.button("Tell me why 👀", key="why_municipalities"):
        st.write(f"São Paulo has the most airports because it's Brazil's largest urban region and has high demand for business, cargo, and regional air travel.")

def show_map(airports):
    # Header
    st.header("Global Distribution of Airports by Elevation 🌍")
    # Cleans the data so it is ready for mapping
    airports_clean = airports.dropna(subset=["coordinates", "elevation_ft"]).copy()
    # Splits the coordinates column into two columns
    coords = airports_clean["coordinates"].str.split(",", expand=True)
    # Strips the columns of blank spaces and converts them into float integers
    airports_clean["longitude"] = coords[0].str.strip().astype(float)
    airports_clean["latitude"] = coords[1].str.strip().astype(float)
    # Lists the categories
    st.markdown("""
        Elevation Categories:
         🔵 Low (< 1,000 ft)  |  🟢 Mid (1,000 - 5,000 ft)  |  🟠 High (> 5,000 ft)
    """)
    # Function to assign the colors based on elevations
    def get_color(elevation):
        if elevation < 1000:
            return [0, 100, 255, 140] 
        elif elevation < 5000:
            return [0, 200, 100, 140]  
        else:
            return [255, 100, 0, 160] 
    # Applies the function to every row 
    airports_clean["color"] = airports_clean["elevation_ft"].apply(get_color)
    #[MAP]
    layer = pdk.Layer(
        # Scatterplot map
        "ScatterplotLayer",
        # Assigning the data
        data=airports_clean,
        get_position='[longitude, latitude]',
        # Size of each dot
        get_radius=20000, 
        get_fill_color="color",
        # I am proud of this code, because it is useful to hover on a point and learn more information.
        # Can hover on a point
        pickable=True
    )
    # Default map view
    view_state = pdk.ViewState(
        latitude=20,
        longitude=-20,
        zoom=1.5,
        pitch=0
    )
    st.pydeck_chart(pdk.Deck(
        # Light background
        map_style="mapbox://styles/mapbox/light-v9", 
        layers=[layer],
        initial_view_state=view_state,
        # Pop up when hovering of the municipality and the elevation.
        tooltip={
        "html": """ <b>Airport:</b> {name} <br/> <b>Municipality:</b> {municipality} <br/> <b>Country:</b> {country_name} <br/>
        <b>Type:</b> {type} <br/> <b>Elevation:</b> {elevation_ft} ft """,
        "style": {"color": "white"}
        }
    ))

def airport_types(airports, countries):
    # Header
    st.header("Airport Types by Country 📊")
    # Creates a dictionary to map country codes to country names
    country_dict = dict(zip(countries["Alpha-2 code"], countries["English short name lower case"]))
    #[ST1]
    # Drop down menu to select country
    country_choice = st.selectbox(
        "Select a country to see the distribution of airport types:",
        sorted(airports["country_name"].dropna().unique())
    )
    # Filters the data to only keep the airports of the specific country
    filtered = airports[airports["country_name"] == country_choice]
    #[CHART1]
    # Calls the pie chart function
    fig = pie_chart(filtered, country_choice)
    st.pyplot(fig)
    st.write(f"Total airports in {country_choice}: {len(filtered)}")

def municipality_analysis(airports):
    # Header
    st.header("Local Airport Elevation Comparison 🏙️")
    #[ST1]
    # Drop down to select municipality
    municipality_choice = st.selectbox(
        "Select a municipality:",
        sorted(airports["municipality"].dropna().unique())
    )
    # Filters the data to include only the airports in the selected municipality 
    muni_data = airports[airports["municipality"] == municipality_choice]
    muni_data = muni_data.dropna(subset=["elevation_ft"])
    # Call the bar chart function
    fig = bar_chart(muni_data, municipality_choice)  
    st.pyplot(fig)
    total_sum = 0
    total_count = 0
    #[ITERLOOP]
    # Sum the values in the selected municipality's airports' elevations
    for e in muni_data["elevation_ft"].values:
        total_sum += e
        total_count += 1   
    # Create the average based on the number of airports            
    if total_count > 0:
        average = total_sum / total_count
        # Print the average
        st.write(f"The average elevation in {municipality_choice} is {average:,.2f} ft.")

def conclusions():
    st.header("Key Insights ✨")
    st.write("""
    Through this exploration of global aviation data, here are the findings:
             
             - 🌍 Geography strongly influences airport elevation
             The highest elevation airports are located in mountainous regions.
             
             - ✈️ Airport types are based on the regional needs of where they are located
             Heliports and small airports are more common in remote or hard-to-reach areas, while large airports are more common in densely populated and urban regions. 
             
             - 🇺🇸 The United States has the most airports overall
             The United States has a large land area, widespread population, and strong aviation infrastructure, with the resources to invest in it.
             
             - 🏙 Municipalities vary widely in airport distribution
             Highly populated cities (like São Paulo) usually have more airports because of their dense urban living space and high demand for travel.
    """)
    st.subheader("Final Takeaway ꪜ")
    st.write("""
    In conclusion, this analysis shows that airports are not randomly distributed - it is based on geography, population, and the general needs of the region and population.
    """)
    
# Main function
def main():
    app_setup()
    airports, countries = load_data()
    # Creates dictionary from country dataframe
    #[DICTMETHOD]
    country_dict = create_country_mapping(countries)
    # Creates a new column in airports and replaces the code with a country name.
    #[COLUMNS]
    airports["country_name"] = airports["iso_country"].map(country_dict)
    choice = sidebar_navigation()
    if choice == "Home":
        home_page()
    elif choice == "Elevations":
        elevations(airports, country_dict)
    elif choice == "Regions":
        regions(airports, country_dict)
    elif choice == "Municipalities":
        municipalities(airports)
    elif choice == "Map":
        show_map(airports)
    elif choice == "Airport Types":
        airport_types(airports, countries)
    elif choice == "Municipality Analysis":
        municipality_analysis(airports)
    elif choice == "Conclusion":
        conclusions()
 
main()