# Task 1 – UFO Sightings Interactive Dashboard

## Overview
This project presents an interactive dashboard built for Task 1 of the Data Visualisation assessment. The dashboard explores a UFO sightings dataset and shows how reports vary across time, geography, and reported object shape.

The dashboard was designed to do more than display charts. Its purpose is to help users explore the data, identify patterns, and understand the main story in a clear and interactive way.

## Main Purpose
The main idea behind this dashboard is that UFO sighting reports are not evenly distributed. The data shows stronger reporting in some years, especially after the mid-1990s, and much higher reporting in some countries than others. It also shows that reported object shapes and locations vary in meaningful ways.

## Questions the Dashboard Helps Answer
The dashboard helps users explore questions such as:

- How have UFO sighting reports changed over time?
- Which countries have the highest number of reports?
- Which shapes are reported most often?
- How do reported shapes change across years?
- Where are sightings concentrated geographically?
- Which states and cities contribute the most reports within a selected country?

## Audience
This dashboard is designed for a broad but interested audience, including:

- course assessors
- data visualisation students
- general users
- UFO enthusiasts

Because of this, the dashboard was designed to be simple to use while still showing meaningful analysis.

## Design Approach
The dashboard was built using **Streamlit** and **Plotly**. These tools were chosen because they support interactive filtering, hover detail, and public sharing through a web link.

The design follows a clear structure:
- the most important charts appear first
- supporting views appear below
- filters allow users to change the views easily
- chart titles explain what each visual is showing

A dark neutral theme with limited accent colours was used to keep the dashboard professional and visually focused.

## Dashboard Features
The dashboard includes:
- time-based trend analysis
- country comparison
- shape-based comparison
- geographic map view
- country-to-state-to-city drill-down interaction
- linked filters and interactive tooltips

## Data Cleaning Summary
Several cleaning steps were necessary before building the dashboard:
- column names were standardised
- date and time fields were converted properly
- invalid or missing timestamps were removed
- text fields such as city, state, country, and shape were cleaned
- numeric fields such as latitude, longitude, and duration were converted safely
- additional time-based fields such as year, month, hour, and season were created

These steps helped improve consistency and made the final dashboard more accurate and reliable.

## Public Dashboard Link
Add your public dashboard link here:

https://ufo-dashboard-km5xm5vcgkbnpinlbyhbbv.streamlit.app/

## Files Included
This task submission usually includes:
- dashboard source code
- dataset used for analysis
- screenshots for the report
- written report in the final PDF

## Notes
The dashboard is intended to be understandable without needing the report beside it. The report supports the dashboard by explaining the audience, purpose, design choices, and usability considerations.

## Author
**Mursal Abdidahir Dirie**
