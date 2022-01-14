
# -- Hack to use old pickle protocol
import pickle
pickle.HIGHEST_PROTOCOL = 4

# -- Needed imports
import os
from glob import glob
from gwpy.table import Table
import numpy as np
import json
import pandas as pd
import requests, tempfile, h5py

KEYLIST = ['name', 'ifar', 'mass', 'gps', 'pastro', 'source', 'snr', 'pipeline']
IFAR_THRESH = 1/(365)    # FAR threshold of 1 / day

def read_gwosc():

	url = 'https://www.gw-openscience.org/eventapi/json/GWTC/'
	r = requests.get(url)
	trigdict = json.loads(r.content)
	#print(json.dumps(trigdict, indent=2))
	outdict = {}
	for key in KEYLIST:
		outdict[key] = np.array([])

	N = len(trigdict['events'].keys())
	outdict['source'] = np.array(['Event-Portal']*N)
	outdict['pipeline'] = np.array(['NA']*N)
	for tag, info in trigdict['events'].items():

		outdict['name']   = np.append(outdict['name'], info['commonName'])
		outdict['ifar']   = np.append(outdict['ifar'], 1/info['far'])
		try:
			outdict['mass']   = np.append(outdict['mass'], info['mass_1_source'] + info['mass_2_source'])
		except:
			outdict['mass']   = np.append(outdict['mass'], -1.0)
		outdict['gps']    = np.append(outdict['gps'], info['GPS'])
		outdict['pastro'] = np.append(outdict['pastro'], info['p_astro'])
		outdict['snr']    = np.append(outdict['snr'], info['network_matched_filter_snr'])


	print(outdict)
	return outdict
	

def read_xml_trigs(loc = 'source_data/gwtc3/search_data_products', pipeline = 'gstlal_allsky', source='GWTC-3'):

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
		trigdict['source'] = np.append(trigdict['source'], source + '_' + pipeline)
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


def read_ogc4():
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

# -- Load GWTC
gwosc = read_gwosc()

# -- Load OGC-4
ogc4 = read_ogc4()

# -- Load GWTC-3
gstlal3 = read_xml_trigs(pipeline = 'gstlal_allsky', source='GWTC-3')
#print(gstlal)
pycbc_bbh3 = read_xml_trigs(pipeline = 'pycbc_highmass', source='GWTC-3')
#print(pycbc_bbh)
pycbc3 = read_xml_trigs(pipeline = 'pycbc_all_sky')
#print(pycbc)
mbta3 = read_xml_trigs(pipeline='mbta_all_sky')
#print(mbta)

# -- Load GWTC-2.1
gstlal2p1 = read_xml_trigs(loc='source_data/gwtc2p1/search_data_products', pipeline='gstlal_all_sky', source='GWTC-2.1')
mbta2p1 = read_xml_trigs( loc='source_data/gwtc2p1/search_data_products', pipeline='mbta_all_sky', source='GWTC-2.1')
pycbc2p1 = read_xml_trigs( loc='source_data/gwtc2p1/search_data_products', pipeline='pycbc_all_sky', source='GWTC-2.1')
pycbc_bbh2p1 = read_xml_trigs( loc='source_data/gwtc2p1/search_data_products', pipeline='pycbc_highmass', source='GWTC-2.1')


# -- Combine all lists into a pandas dataframe
source_list = [to_pd(gstlal3), to_pd(pycbc_bbh3), to_pd(pycbc3), to_pd(mbta3), to_pd(ogc4), 
	to_pd(gstlal2p1), to_pd(mbta2p1), to_pd(pycbc2p1), to_pd(pycbc_bbh2p1), to_pd(gwosc)]
all_triggers = pd.concat(source_list)

print(all_triggers)

# -- Save trigger set
all_triggers.to_hdf('alltrigs.hdf', key='triggers', mode='w')



