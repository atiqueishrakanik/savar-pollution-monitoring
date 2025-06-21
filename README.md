# Sentinel-5P Based Air Pollutant Monitoring over Savar, Bangladesh (2018–2025)

This project provides an interactive web-based tool for monitoring atmospheric pollutants over **Savar**, a rapidly growing industrial suburb of Dhaka, Bangladesh. Savar is known as the hub of the country's garments export industry, which plays a crucial role in Bangladesh's economy and global reputation.

Using **Sentinel-5P satellite data** from 2018 to 2025, this app visualizes key air pollutants:
- NO₂ (Nitrogen Dioxide)
- CO (Carbon Monoxide)
- O₃ (Ozone)
- SO₂ (Sulfur Dioxide)
- HCHO (Formaldehyde)
- Aerosol Index

### 🔍 Features
- Interactive map to explore monthly atmospheric pollution
- Click on any point to inspect pollutant concentration
- Sidebar controls for selecting pollutant, year, and month
- Dynamic color legends for better visualization
- Developed using Streamlit, Earth Engine, Folium, and GeoPandas

### 📦 How to Run
```bash
streamlit run geo_pollution_app.py
