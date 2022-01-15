import streamlit as st
import helper
import altair as alt
import numpy as np

st.write("## GW Trigger Index")

st.write("""
    * Compare sets of gravitational wave triggers from different sources.
    * Click on README at the bottom for more information.
    """)

# -- Read all trigs
#triglist = helper.get_all_trigs()
triglist = helper.read_trigs()

gps_min = int(triglist['gps'].min())
gps_max = np.ceil(triglist['gps'].max())
alltime = int(gps_max - gps_min)

st.sidebar.write("## Set GPS range")
st.sidebar.write("{0} - {1}".format(gps_min, gps_max))
gps_low = st.sidebar.number_input('GPS Start', value=gps_min )
gps_high = st.sidebar.number_input('GPS End', value=gps_max )
#gps_high = gps_low + gps_dur

# -- Set selections
#gps_range = st.sidebar.slider('GPS Range', value=[gps_min, gps_max], step = 24*3600, 
#	min_value = gps_min, max_value = gps_max )

st.sidebar.write("## Set FAR and SNR range")
min_ifar = st.sidebar.number_input('IFAR Threshold', value=0.0, step=1.0)
min_snr  = st.sidebar.number_input('SNR Threshold', value=0.0, step=1.0)

selected = triglist[ (triglist['gps'] > gps_low) & (triglist['gps'] < gps_high) ]
selected = selected[ selected['ifar'] > min_ifar ]
selected = selected[ selected['snr']  > min_snr  ]

selected = selected.reset_index(drop=True)

st.write("Selected {} triggers".format(len(selected)))

st.dataframe(selected)

# -- Download trigger list as JSON
jsontrigs = helper.convert_json(selected)
st.download_button(
   "Download triggers as JSON",
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
    tooltip=['name', 'gps', 'snr', 'mass', 'pastro']
).interactive(
	bind_y = False
).properties(
	width=450,
    height=320)

st.write(chart)

# -- Notes on plot
with st.expander("Help with plot"):
    st.write("""
        * Hover over a point to see trigger information
        * Scroll to zoom
        * Click and drag to move x-axis
        """)

# -- README
with open('README.md', 'r') as readme:
    readmetxt = readme.read()
with st.expander("README"):
    st.write(readmetxt)




