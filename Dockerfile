# Start from Ubuntu 22.04
FROM ubuntu:22.04

# Install core dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    wget \
    curl \
    python3 \
    python3-pip \
    libssl-dev \
    zlib1g-dev \
    libbz2-dev \
    liblzma-dev \
    libffi-dev \
    libsqlite3-dev \
    libgsl-dev \
    libtbb-dev \
    libboost-all-dev \
    graphviz \
    texlive \
    libx11-dev \
    libxpm-dev \
    libxft-dev \
    libxext-dev \
    libgl2ps-dev \
    libxml2-dev \
    libgfal2-dev \
    libmysqlclient-dev \
    libpq-dev \
    libkrb5-dev \
    libfftw3-dev \
    libcfitsio-dev \
    libgraphviz-dev \
    libavahi-compat-libdnssd-dev \
    libldap2-dev \
    libpython3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip3 install --upgrade pip && \
    pip3 install pandas numpy uproot

WORKDIR /opt
RUN wget https://root.cern/download/root_v6.28.10.source.tar.gz && \
    tar -xzf root_v6.28.10.source.tar.gz && \
    mkdir root_build && \
    cd root_build && \
    cmake -DCMAKE_INSTALL_PREFIX=/usr/local/root ../root-6.28.10 && \
    cmake --build . --target install -- -j$(nproc) && \
    cd .. && \
    rm -rf root_build root-6.28.10 root_v6.28.10.source.tar.gz

ENV ROOTSYS /usr/local/root
ENV PATH $ROOTSYS/bin:$PATH
ENV LD_LIBRARY_PATH $ROOTSYS/lib:$LD_LIBRARY_PATH
ENV PYTHONPATH $ROOTSYS/lib:$PYTHONPATH

# Install Pythia8 and DelphesPythia8
WORKDIR /opt

# Install Pythia8 dependencies
RUN apt-get update && apt-get install -y \
    libhepmc3-dev \
    liblhapdf-dev \
    libboost-dev \
    && rm -rf /var/lib/apt/lists/*

# Download and install Pythia8
RUN wget https://pythia.org/download/pythia83/pythia8309.tgz && \
    tar xvfz pythia8309.tgz && \
    cd pythia8309 && \
    ./configure --prefix=/usr/local/pythia8 --with-hepmc3 --with-lhapdf6 && \
    make -j$(nproc) && \
    make install && \
    cd .. && \
    rm -rf pythia8309 pythia8309.tgz


# Build Delphes with Pythia8 support
WORKDIR /opt
RUN wget http://cp3.irmp.ucl.ac.be/downloads/Delphes-3.5.0.tar.gz && \
    tar -xzf Delphes-3.5.0.tar.gz && \
    cd Delphes-3.5.0 && \
    make HAS_PYTHIA8=true PYTHIA8_DIR=/usr/local/pythia8 -j$(nproc) && \
    rm -rf /opt/Delphes-3.5.0.tar.gz
# Build Delphes with Pythia8 support


# Set Pythia8 environment variables
ENV PYTHIA8_DIR /usr/local/pythia8
ENV PYTHIA8DATA $PYTHIA8_DIR/share/Pythia8/xmldoc
ENV LD_LIBRARY_PATH $PYTHIA8_DIR/lib:$LD_LIBRARY_PATH
# Set Delphes environment variables
ENV DELPHES_DIR /opt/Delphes-3.5.0
ENV LD_LIBRARY_PATH $DELPHES_DIR:$LD_LIBRARY_PATH
ENV PATH $DELPHES_DIR:$PATH

# Default command
CMD ["/bin/bash"]