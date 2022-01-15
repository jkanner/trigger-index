
# -- GWTC-3 trigger set
mkdir source_data
mkdir source_data/gwtc3
wget https://zenodo.org/record/5546665/files/search_data.tar.gz?download=1 -O source_data/gwtc3/search_data.tar.gz
tar -xf source_data/gwtc3/search_data.tar.gz -C source_data/gwtc3


# -- GWTC 2.1 trigger set
mkdir source_data/gwtc2p1
wget https://zenodo.org/record/5759108/files/search_data_GWTC2p1.tar.gz?download=1 -O source_data/gwtc2p1/search_data_GWTC2p1.tar.gz
tar -xf source_data/gwtc2p1/search_data_GWTC2p1.tar.gz -C source_data/gwtc2p1
