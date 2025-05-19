FROM python:3.9-slim

# Create a user and set env vars
ENV USER=username
ENV HOME=/home/$USER
RUN useradd -m -u 1000 $USER

# Set working directory
WORKDIR $HOME/app

# Install system dependencies (for Mamba, Streamlit, etc.)
RUN apt-get update && apt-get install --no-install-recommends -y \
    wget bzip2 git\
    build-essential \
    libgl1-mesa-glx \
    mesa-utils \
    libosmesa6-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Miniconda & Mamba
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh && \
    bash miniconda.sh -b -p /opt/conda && \
    rm miniconda.sh && \
    /opt/conda/bin/conda install -y -n base -c conda-forge mamba && \
    ln -s /opt/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh && \
    echo ". /opt/conda/etc/profile.d/conda.sh" >> /etc/bash.bashrc && \
    echo "conda activate base" >> /etc/bash.bashrc

# Add conda to PATH
ENV PATH="/opt/conda/bin:$PATH"

# Copy environment definition and app files
COPY env.yaml ./env.yaml
COPY app/ $HOME/app/
# COPY bvpy/ $HOME/bvpy
RUN chown -R $USER:$USER $HOME/app

# Create the environment from env.yaml
RUN mamba env create -p /env -f env.yaml && \
    rm -rf /opt/conda /root/.cache /tmp/*

# Set environment to use the new env only
ENV PATH="/env/bin:$PATH"
SHELL ["bash", "--login", "-c"]

# Switch to non-root user
USER $USER

# Streamlit settings
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ENABLECORS=false
ENV PYTHONUNBUFFERED=1
# attempt to solve permission issue
ENV HOME=/tmp
ENV DIJITSO_CACHE_DIR=/tmp/dijitso
ENV XDG_CACHE_HOME=/tmp
ENV MPLCONFIGDIR=/tmp/mplconfig

# Expose port
EXPOSE 8501

# Healthcheck
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Start Streamlit
ENTRYPOINT ["streamlit", "run", "🏠_Home.py", "--server.port=8501", "--server.address=0.0.0.0", "--browser.gatherUsageStats=false"]

# CMD ["conda", "run", "--no-capture-output", "-n", "bvpy_env", "streamlit", "run", "🏠_Home.py", "--server.port=8501", "--server.address=0.0.0.0"]