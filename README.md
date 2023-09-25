# SuperviselyInteractions
A library of scripts I use to interact with supervisely

There are two conda environments in this repo. The file `environment_supervisely.yml` has all the packages with specified versions that were used. The recommended approach is to use `git clone https://github.com/spectralnanodiamond/SuperviselyInteractions/` then 
``conda env create -f environment_supervisely.yml`` or ``mamba env create -f environment_supervisely.yml`` if you have mamba installed. 

If that does not work, or you would like newer versions of the packages used, please use `conda env create -f environment_supervisely.yml` as this version does not specify the versions of all the python packages.
