import streamlit as st
import pandas as pd
import h5py
import numpy as np
import requests, tempfile


KEYLIST = ['name', 'ifar', 'mass1', 'mass2', 'gps', 'pastro', 'source']

IFAR_THRESH = 1/(365)    # FAR threshold of 1 / day

@st.cache
def read_trigs():
	triglist = pd.read_hdf('data/alltrigs.hdf', 'triggers')
	return triglist

@st.cache
def convert_json(df):
   return df.to_json(orient="records", indent=2)


