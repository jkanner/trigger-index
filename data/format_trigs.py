import os
from glob import glob
from gwpy.table import Table
import numpy as np
import json
import pandas as pd
import requests, tempfile, h5py

KEYLIST = ['name', 'ifar', 'mass', 'gps', 'pastro', 'source', 'snr', 'pipeline']
IFAR_THRESH = 1/(365)    # FAR threshold of 1 / day


def read_xml_trigs(loc = 'source_data/search_data_products', pipeline = 'gstlal_allsky', source='GWTC-3'):

	trigdir = os.path.join(loc, pipeline)
	triglist = glob(trigdir + "/*.xml")
	print(trigdir)

	# -- Initialize dictionary
	trigdict = {}
	for key in KEYLIST:
		trigdict[key] = np.array([])

	print(trigdict.keys())
	print(type(trigdict['name']))

	for trig in triglist:

		#single_data = Table.read(trig,tablename="sngl_inspiral", use_numpy_dtypes=True)
		#print(trigdata.colnames)

		coinc_data = Table.read(trig,tablename="coinc_inspiral", use_numpy_dtypes=False)
		#print(coinc_data.colnames)


		trigdict['name'] = np.append(trigdict['name'], str(coinc_data[0]['end_time']))
		trigdict['ifar'] = np.append(trigdict['ifar'], 1/coinc_data[0]['combined_far']/3.154e+7)
		trigdict['snr']  = np.append(trigdict['snr'], coinc_data[0]['snr'])

		gps = coinc_data[0]['end_time'] + coinc_data[0]['end_time_ns']*1e-9
		trigdict['gps']  = np.append(trigdict['gps'], gps)
		trigdict['mass'] = np.append(trigdict['mass'], coinc_data[0]['mass'])
		trigdict['source'] = np.append(trigdict['source'], source)
		trigdict['pipeline'] = np.append(trigdict['pipeline'], pipeline)

		# -- Try to find p-astro
		strgps = str(coinc_data[0]['end_time'])

		pastro_fn = glob(trigdir + '/pastro/*{0}*.json'.format(strgps))
		
		if len(pastro_fn) == 1:
			with open(pastro_fn[0],'r') as astro_file:
				astro_json = json.loads(astro_file.read())
			pastro = astro_json['Astro']
		else:
			pastro = -1

		trigdict['pastro'] = np.append(trigdict['pastro'], pastro)
	
	return trigdict		


def read_ogc4(fn='4-OGC_small.hdf'):
	# -- URL for download
	url = "https://github.com/gwastro/4-ogc/raw/master/search/4-OGC_small.hdf"

	# -- Get file from web
	r = requests.get(url)
	tfile = tempfile.NamedTemporaryFile(suffix='.hdf')
	tfile.write(r.content)
	#samples = read(tfile.name)


	trigin = h5py.File(tfile.name)
	print(trigin.keys())
	datadict = {}

	# -- Retain all attributes listed in the keylist
	for key in ['name', 'ifar', 'pastro']:
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
	datadict['pipeline'] = ['pycbc']*len(gps_vec)
	datadict['mass'] = trigin['mass1'][...] + trigin['mass2'][...]

	# -- Calculate network SNR
	H_snr = np.maximum(0,trigin['H1_snr'])
	L_snr = np.maximum(0,trigin['L1_snr'])
	V_snr = np.maximum(0,trigin['V1_snr'])
	snr = np.sqrt(H_snr**2 + L_snr**2 + V_snr**2)
	datadict['snr'] = snr

	trigin.close()
	return datadict


def to_pd(trigdict):

	smalldict = {}
	for key in KEYLIST:
		smalldict[key] = trigdict[key]
	trigset = pd.DataFrame(smalldict)

	trig_confident = trigset[ trigset['ifar'] > IFAR_THRESH ]
	trig_confident = trig_confident.reset_index(drop=True)

	return trig_confident


ogc4 = read_ogc4()

gstlal = read_xml_trigs(pipeline = 'gstlal_allsky', source='GWTC-3')
#print(gstlal)

pycbc_bbh = read_xml_trigs(pipeline = 'pycbc_highmass', source='GWTC-3')
#print(pycbc_bbh)

pycbc = read_xml_trigs(pipeline = 'pycbc_all_sky')
#print(pycbc)

mbta = read_xml_trigs(pipeline='mbta_all_sky')
#print(mbta)

gwtc3_list = [to_pd(gstlal), to_pd(pycbc_bbh), to_pd(pycbc), to_pd(mbta), to_pd(ogc4)]

all_gwtc3 = pd.concat(gwtc3_list)

print(all_gwtc3)

# -- Save trigger set
all_gwtc3.to_hdf('alltrigs.hdf', key='triggers', mode='w')



