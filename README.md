# trigger-index

### An index to compare gravitational-wave event triggers from various sources.

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/jkanner/trigger-index/main/app.py)

[Source Code](https://github.com/jkanner/trigger-index)

This app displays results from the International Gravitational Wave Network (IGWN), including [LIGO](https://www.ligo.org), 
[Virgo](https://www.virgo-gw.eu), and 
[KAGRA](https://gwcenter.icrr.u-tokyo.ac.jp/en/).

## Data Sources

 * 4-OGC: 4-OGC Catalog [github](https://github.com/gwastro/4-ogc)
 * GWTC-2.1: GWTC-2.1 Candidate Data Release [Zenodo](https://zenodo.org/record/5759108)
 * GWTC-3:   GWTC-3 Candidate Data Release   [Zenodo](https://zenodo.org/record/5546665)
 * Event Portal: GWOSC Event Portal view of GWTC [GWOSC](https://www.gw-openscience.org/eventapi/html/GWTC/)

## HDF5 File

All triggers on display in the app are available in [data/alltrigs.hdf](https://github.com/jkanner/trigger-index/tree/main/data)

The fields are:

 * `name`   Where available, the event name.  Else, this is the truncated GPS time
 * `ifar`   Inverse false alarm rate, in units of yr^-1
 * `mass`   Total mass of the source, in solar masses
 * `gps`    Approximate merger time
 * `pastro` Probability the trigger is astrophysical in origin
 * `source` Source of the information (see "Data Sources")
 * `snr`    Signal-to-noise ratio
 * `pipeline` Name of the search pipeline that identified the trigger
 
## Adding additional sources

Additional sources may be added to this app by updating the [git repo](https://github.com/jkanner/trigger-index).

You are welcome to make a pull request with any additions.  
The key step to add a new source is to write a method which will read in the source information, and return 
a dictionary including the same fields listed above.  Each item in the dictionary should
be a 1-dimensional numpy array.  See the method `data/format_trigs.py` for examples.  If you 
wish to try running `format_trigs.py`, you may first wish to run `bash data/download.sh` to
download the expected data files.






