import streamlit as st
import pandas as pd
import h5py
import numpy as np
import requests, tempfile


KEYLIST = ['name', 'ifar', 'mass1', 'mass2', 'gps', 'pastro', 'source']

IFAR_THRESH = 1/(365)    # FAR threshold of 1 / day

## name, IFAR, mass1, mass2, 
## {H1/L1/V1}_end_time, pastro 

def make_trigs(trigdict):


	smalldict = {}
	for key in KEYLIST:
		smalldict[key] = trigdict[key]
	trigset = pd.DataFrame(smalldict)

	trig_confident = trigset[ trigset['ifar'] > IFAR_THRESH ]
	trig_confident = trig_confident.reset_index(drop=True)

	# rslt_df = dataframe[dataframe['Percentage'] > 80]

	return trig_confident

def read_ogc4(fn='4-OGC_small.hdf'):

	# -- URL for download
	url = "https://github.com/gwastro/4-ogc/raw/master/search/4-OGC_small.hdf"

	# -- Get file from web
	r = requests.get(url)
	tfile = tempfile.NamedTemporaryFile(suffix='.hdf')
	tfile.write(r.content)
	#samples = read(tfile.name)


	trigin = h5py.File(tfile.name)
	datadict = {}

	# -- Retain all attributes listed in the keylist
	for key in KEYLIST:
		if key != 'gps' and key != 'source':
			datadict[key] = trigin[key][...]

	# -- Select the GPS time as a max over detectors to ensure 
	# -- valid GPS times
	gps_vec = np.maximum(trigin['H1_end_time'][...], 
						trigin['L1_end_time'][...] )
	gps_vec = np.maximum(gps_vec, trigin['V1_end_time'][...])

	namelist = [name.decode() for name in datadict['name']]
	datadict['name'] = np.array(namelist)
	datadict['gps'] = gps_vec
	datadict['source'] = ['4-OGC']*len(gps_vec)
	trigin.close()
	return datadict

def read_gwtc_3(fn='search_data.hdf5'):
	# -- URL for download
	# https://zenodo.org/record/5546665/files/search_data.tar.gz?download=1
	return 0


# -- Method to make final trig list, and cache it
@st.cache
def get_all_trigs():
	og4 = read_ogc4()
	triglist = make_trigs(og4)
	return triglist

@st.cache
def read_trigs():
	triglist = pd.read_hdf('data/alltrigs.hdf', 'triggers')
	return triglist

@st.cache
def convert_json(df):
   return df.to_json(orient="records", indent=2)


triglist = read_ogc4()
print(triglist['name'])


# -- debugging
#og4 = read_ogc4()
#print(og4)
#triglist = make_trigs(og4)

