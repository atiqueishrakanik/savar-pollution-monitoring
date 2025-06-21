import streamlit as st
import ee
import folium
import geopandas as gpd
from streamlit_folium import st_folium
import geemap.folium as geemap


# ✅ EE Initialization using service account
service_account = "savar-no2--8-to-2025-c1f7606de@industrial-glow-461921-k4.iam.gserviceaccount.com"
key_file = "service_account.json"  # Place this file in your app folder

credentials = ee.ServiceAccountCredentials(service_account, key_file)
ee.Initialize(credentials)

# Patch Folium for EE layers
def add_ee_layer(self, ee_image_object, vis_params, name):
    map_id_dict = ee.Image(ee_image_object).getMapId(vis_params)
    folium.raster_layers.TileLayer(
        tiles=map_id_dict['tile_fetcher'].url_format,
        attr='Google Earth Engine',
        name=name,
        overlay=True,
        control=True
    ).add_to(self)

folium.Map.add_ee_layer = add_ee_layer

# Load AOI
aoi_path = "Savar EOI Shape File.json"
savar_gdf = gpd.read_file(aoi_path)
savar_geom = geemap.geopandas_to_ee(savar_gdf)
aoi_style = {'color': 'black', 'fillColor': '00000000'}

# Pollutant Info
pollutant_info = {
    'NO₂': {
        'dataset': 'COPERNICUS/S5P/OFFL/L3_NO2',
        'band': 'tropospheric_NO2_column_number_density',
        'unit': 'mol/m²',
        'vis': {'min': 0, 'max': 0.0003, 'palette': ['green', 'yellow', 'orange', 'red', 'maroon']}
    },
    'CO': {
        'dataset': 'COPERNICUS/S5P/OFFL/L3_CO',
        'band': 'CO_column_number_density',
        'unit': 'mol/m²',
        'vis': {'min': 0.02, 'max': 0.06, 'palette': ['navy', 'blue', 'cyan', 'lime', 'yellow', 'red']}
    },
    'O₃': {
        'dataset': 'COPERNICUS/S5P/OFFL/L3_O3',
        'band': 'O3_column_number_density',
        'unit': 'mol/m²',
        'vis': {'min': 0.1, 'max': 0.13, 'palette': ['orange','red','blue' ,'lime', 'yellow','maroon','cyan','purple']}
    },
    'SO₂': {
        'dataset': 'COPERNICUS/S5P/OFFL/L3_SO2',
        'band': 'SO2_column_number_density',
        'unit': 'mol/m²',
        'vis': {'min': 0, 'max': 0.0005, 'palette': ['purple', 'blue', 'green', 'yellow', 'orange', 'red','lime','cyan']}
    },
    'HCHO': {
        'dataset': 'COPERNICUS/S5P/OFFL/L3_HCHO',
        'band': 'tropospheric_HCHO_column_number_density',
        'unit': 'mol/m²',
        'vis': {'min': 0.0001, 'max': 0.00025, 'palette': ['white', 'green', 'yellow', 'orange', 'red','blue']}
    },
    'Aerosol Index': {
        'dataset': 'COPERNICUS/S5P/OFFL/L3_AER_AI',
        'band': 'absorbing_aerosol_index',
        'unit': 'Index',
        'vis': {'min': -1.5, 'max': 0.4, 'palette': ['red', 'blue', 'green', 'yellow', 'orange', 'purple','lime','cyan']}
    }
}

# Get Monthly Image
def get_monthly_image(year, month, pollutant):
    p = pollutant_info[pollutant]
    start = ee.Date.fromYMD(year, month, 1)
    end = start.advance(1, 'month')
    return (ee.ImageCollection(p['dataset'])
            .filterDate(start, end)
            .filterBounds(savar_geom)
            .select(p['band'])
            .mean()
            .clip(savar_geom))

# Streamlit UI
st.set_page_config(layout="wide")
st.title("🛰️ Sentinel-5p based Air Pollutant(NO2,SO2,O3,CO,HCHO,AI) Monitoring over Savar,Bangladesh (2018–2025)")
col1, col2 = st.columns([3, 1])

with col1:
    with st.sidebar:
        st.header("🧭 Controls")
        
        pollutant = st.selectbox("Select Pollutant", list(pollutant_info.keys()))
        year = st.selectbox("Select Year", list(range(2018, 2026)), index=3)

        months_dict = {
            1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June",
            7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"
        }

        month_name = st.selectbox("Select Month", list(months_dict.values()), index=0)
        month = list(months_dict.keys())[list(months_dict.values()).index(month_name)]

        st.markdown("**🖱️ 🖱️ Click on map to inspect value ▶ ▶ ▶**")

        lat = st.text_input("Latitude (e.g., 23.8351)")
        lon = st.text_input("Longitude (e.g., 90.2564)")
        inspect_btn = st.button("🕵️ Inspect Point")

        inspected_text = st.empty()

        st.markdown("---", unsafe_allow_html=True)
        st.markdown(
            """
            <div style='font-size:20px; font-weight:bold;'>Author</div>
            <div style='font-size:21px;'>Atique Ishrak Anik, Chittagong University of Engineering and Technology (CUET)</div>
            <a href='https://orcid.org/0009-0008-2175-0835' target='_blank'>ORCID</a><br>
            <a href='https://www.researchgate.net/profile/Atique-Ishrak-Anik' target='_blank'>ResearchGate</a><br>
            <div style='font-size:15px;'>
                Cite This: Anik, Atique (2025). Sentinel-5p based Air Pollutant (NO₂, SO₂, O₃, CO, HCHO, AI) Monitoring over Savar, Bangladesh (2018–2025). figshare. Software. https://doi.org/10.6084/m9.figshare.29375336.v1
            </div>
            <div style='font-size:15px;'>Copyright (c) 2025 atiqueishrakanik</div>
            """,
            unsafe_allow_html=True
        )


    # Map Setup
    center = [23.8351, 90.2564]
    m = folium.Map(
        location=center,
        zoom_start=10,
        control_scale=True,
        tiles='https://mt1.google.com/vt/lyrs=r&x={x}&y={y}&z={z}',
        attr='Google'
    )
    image = get_monthly_image(year, month, pollutant)
    m.add_ee_layer(image, pollutant_info[pollutant]['vis'], f"{pollutant} {year}-{month:02d}")

    import json  # Better to put this import at the top of your file

    aoi_geojson = json.loads(savar_gdf.to_json())
    folium.GeoJson(
    aoi_geojson,
    name="Savar AOI",
    style_function=lambda x: {'color': 'black', 'fillColor': 'transparent', 'weight': 2}
    ).add_to(m)


    # Dynamic key to force rerender
    map_key = f"{pollutant}_{year}_{month}"
    st_map = st_folium(m, width=850, height=600, returned_objects=["last_clicked"], key=map_key)

    if inspect_btn and lat and lon:
        try:
            point = ee.Geometry.Point(float(lon), float(lat))
            val_dict = image.reduceRegion(
                reducer=ee.Reducer.first(),
                geometry=point,
                scale=1000,
                maxPixels=1e13
            ).getInfo()
            value = val_dict.get(pollutant_info[pollutant]['band'])
            unit = pollutant_info[pollutant]['unit']
            if value is not None:
                inspected_text.success(f"{pollutant} @ ({float(lat):.4f}, {float(lon):.4f}): {value:.6f} {unit}")
            else:
                inspected_text.warning("No data at this location.")
        except Exception as e:
            inspected_text.error("Error retrieving value.")

    if st_map and st_map.get("last_clicked"):
        coords = st_map["last_clicked"]
        lon_c, lat_c = coords["lng"], coords["lat"]
        point = ee.Geometry.Point([lon_c, lat_c])
        val_dict = image.reduceRegion(
            reducer=ee.Reducer.first(),
            geometry=point,
            scale=1000,
            maxPixels=1e13
        ).getInfo()
        value = val_dict.get(pollutant_info[pollutant]['band'])
        unit = pollutant_info[pollutant]['unit']
        if value is not None:
            inspected_text.success(f"{pollutant} @ ({lat_c:.4f}, {lon_c:.4f}): {value:.6f} {unit}")
        else:
            inspected_text.warning("No data at this point.")

with col2:
    # Legend Rendering
    vis = pollutant_info[pollutant]['vis']
    unit = pollutant_info[pollutant]['unit']
    palette = vis['palette']
    min_val = vis['min']
    max_val = vis['max']

    st.markdown(f"### Legend ({pollutant}, {unit})")
    steps = len(palette)
    for i, color in enumerate(palette):
        val = min_val + (max_val - min_val) * i / (steps - 1)
        st.markdown(
            f"<div style='display:flex; align-items:center; margin-bottom:4px;'>"
            f"<div style='width:20px; height:20px; background-color:{color}; margin-right:10px;'></div>"
            f"<div>{val:.6f}</div></div>",
            unsafe_allow_html=True
        )
