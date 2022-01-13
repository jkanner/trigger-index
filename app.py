import streamlit as st
import helper
import altair as alt

st.write("## GW Trigger Index")


# -- Read all trigs
triglist = helper.get_all_trigs()

gps_min = int(triglist['gps'].min())
gps_max = int(triglist['gps'].max())

# -- Set selections
gps_range = st.sidebar.slider('GPS Range', value=[gps_min, gps_max], step = 24*3600, 
	min_value = gps_min, max_value = gps_max )

selected = triglist[ (triglist['gps'] > gps_range[0]) & (triglist['gps'] < gps_range[1]) ]
selected = selected.reset_index(drop=True)

st.write("Selected {} triggers".format(len(selected)))

st.dataframe(selected)

# -- Download trigger list as JSON
jsontrigs = helper.convert_json(selected)
st.download_button(
   "Press to Download",
   jsontrigs,
   "file.json",
   "application/json",
   key='download-json'
)

# -- Plot triggers
chart = alt.Chart(selected).mark_circle(
    opacity=0.8,
    stroke='black',
    strokeWidth=1
).encode(
    alt.X('gps:Q', axis=alt.Axis(labelAngle=90), scale=alt.Scale(zero=False)),
    alt.Y('source:N'),
    alt.Color('source:N', legend=None),
    tooltip=['name', 'ifar']
).interactive(
	bind_y = False
).properties(
	width=450,
    height=320)

st.write(chart)

