FROM ubuntu:22.04

# 1. Install essential tools first (including rsync and terminal support)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    wget \
    git \
    rsync \
    libx11-dev \
    libxpm-dev \
    libxft-dev \
    libssl-dev \
    libsqlite3-dev \
    libgsl-dev \
    libhepmc3-dev \
    libboost-all-dev \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# 2. Set default terminal environment
ENV TERM=xterm-256color

# 3. Install ROOT (pre-built binary)
RUN wget https://root.cern/download/root_v6.28.10.Linux-ubuntu22-x86_64-gcc11.4.tar.gz && \
    tar xzf root_v*.tar.gz -C /usr/local --strip-components=1 && \
    rm root_v*.tar.gz

# 4. Install Pythia8 (with explicit build commands)
WORKDIR /tmp
RUN wget https://pythia.org/download/pythia83/pythia8309.tgz && \
    tar xzf pythia8309.tgz && \
    cd pythia8309 && \
    ./configure --prefix=/usr/local/pythia8 --with-hepmc3 && \
    make -j$(nproc) && \
    make install && \
    cd .. && \
    rm -rf pythia8309*

# 5. Set Pythia8 environment variables explicitly
ENV PYTHIA8_DIR=/usr/local/pythia8
ENV PYTHIA8DATA=$PYTHIA8_DIR/share/Pythia8/xmldoc
ENV CPLUS_INCLUDE_PATH=$PYTHIA8_DIR/include:$CPLUS_INCLUDE_PATH
ENV LIBRARY_PATH=$PYTHIA8_DIR/lib:$LIBRARY_PATH
ENV LD_LIBRARY_PATH=$PYTHIA8_DIR/lib:$LD_LIBRARY_PATH

# Build Delphes with explicit paths
RUN git clone https://github.com/delphes/delphes.git -b 3.5.0 && \
    cd delphes && \
    make HAS_PYTHIA8=true \
    PYTHIA8_DIR=$PYTHIA8_DIR \
    PYTHIA8_INC=-I$PYTHIA8_DIR/include/Pythia8 \
    PYTHIA8_LIB=-L$PYTHIA8_DIR/lib \
    PYTHIA8=$PYTHIA8_DIR/ \
    -j$(nproc)


ENV DELPHES_DIR=/tmp/delphes
ENV DELPHES_INCLUDE=$DELPHES_DIR/Delphes
ENV LD_LIBRARY_PATH=$DELPHES_DIR:$LD_LIBRARY_PATH

CMD ["/bin/bash"]