FROM ubuntu

RUN apt-get update
RUN apt-get install -y libglib2.0-0
RUN apt-get install -y git wget
RUN apt-get install bzip2
RUN apt-get install -y gcc
RUN apt-get install -y g++
RUN apt-get install -y libgtk2.0-0
RUN export MINICONDA=$HOME/miniconda
RUN export PATH="$MINICONDA/bin:$PATH"
RUN hash -r
RUN wget -q https://3230d63b5fc54e62148e-c95ac804525aac4b6dba79b00b39d1d3.ssl.cf1.rackcdn.com/Anaconda2-2.5.0-Linux-x86_64.sh -O anaconda.sh
# RUN bash anaconda.sh -b -p $ANACONDA
RUN bash anaconda.sh -p /anaconda -b
ENV PATH=/anaconda/bin:${PATH}
RUN conda config --set always_yes yes
RUN conda update --yes conda
RUN conda info -a
RUN CONDA_SSL_VERIFY=false conda update pyopenssl
# RUN conda install -c menpo opencv3=3.1.0
# RUN conda install -c cvxgrp cvxpy
# RUN conda install -c https://conda.anaconda.org/conda-forge tifffile
# RUN git clone --recursive -b agiovann-master https://github.com/valentina-s/Constrained_NMF.git
# RUN git clone --recursive https://github.com/agiovann/Constrained_NMF.git
# RUN git clone --recursive -b dev https://github.com/agiovann/Constrained_NMF.git
ADD . /CaImAn
WORKDIR /CaImAn/
RUN conda env update -f environment.yml -n root
#RUN conda install --file requirements_conda.txt
#RUN pip install -r requirements_pip.txt
RUN apt-get install libc6-i386
RUN apt-get install -y libsm6 libxrender1
RUN conda install pyqt=4.11.4
RUN python setup.py install
RUN python setup.py build_ext -i

# RUN nosetests

EXPOSE 8080
