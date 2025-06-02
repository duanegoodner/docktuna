FROM python:3.12.10-slim-bookworm
           
ARG PRIMARY_UID
ARG PRIMARY_GID
ARG PRIMARY_USER
ARG CONDA_ENV_NAME
ENV CONDA_ENV_NAME=${CONDA_ENV_NAME}

SHELL [ "/bin/bash", "--login", "-c" ]

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    libpq-dev \
    git \
    curl \
    wget \
    zsh \
    nano \
    fontconfig \
    unzip \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /usr/local/entrypoints
COPY ./docker/image_resources/entrypoint_simple_persistence.sh /usr/local/entrypoints


# Create group and user without sudo
RUN groupadd -g ${PRIMARY_GID} ${PRIMARY_USER} && \
    useradd -m -s /bin/bash -u ${PRIMARY_UID} -g ${PRIMARY_GID} ${PRIMARY_USER}

# Switch to PRIMARY_USER
USER ${PRIMARY_USER}
RUN mkdir -p /home/${PRIMARY_USER}/project
WORKDIR /home/${PRIMARY_USER}/project

# Install Oh My Zsh + plugins + theme 
RUN git clone https://github.com/ohmyzsh/ohmyzsh.git ~/.oh-my-zsh && \
    cp ~/.oh-my-zsh/templates/zshrc.zsh-template ~/.zshrc && \
    git clone https://github.com/zsh-users/zsh-autosuggestions ~/.oh-my-zsh/custom/plugins/zsh-autosuggestions && \
    git clone https://github.com/zsh-users/zsh-completions ~/.oh-my-zsh/custom/plugins/zsh-completions && \
    git clone https://github.com/zsh-users/zsh-syntax-highlighting ~/.oh-my-zsh/custom/plugins/zsh-syntax-highlighting && \
    git clone https://github.com/zsh-users/zsh-history-substring-search ~/.oh-my-zsh/custom/plugins/zsh-history-substring-search && \
    git clone --depth=1 https://github.com/romkatv/powerlevel10k.git ~/.oh-my-zsh/custom/themes/powerlevel10k

# Fonts: install MesloLGS Nerd Font (user-local)
RUN mkdir -p ~/.local/share/fonts && \
    wget --show-progress --user-agent="Mozilla" \
    https://github.com/ryanoasis/nerd-fonts/releases/latest/download/Meslo.zip \
    -O /tmp/Meslo.zip && \
    unzip -j /tmp/Meslo.zip '*.ttf' -d ~/.local/share/fonts && \
    fc-cache -fv && \
    rm /tmp/Meslo.zip

# Copy final Zsh and p10k configs (as root)
USER root
COPY ./docker/image_resources/.zshrc /home/${PRIMARY_USER}/.zshrc
COPY ./docker/image_resources/.p10k.zsh /home/${PRIMARY_USER}/.p10k.zsh
RUN chown ${PRIMARY_USER}:${PRIMARY_GID} /home/${PRIMARY_USER}/.zshrc /home/${PRIMARY_USER}/.p10k.zsh
USER ${PRIMARY_USER}

# Install Miniconda under PRIMARY_USER home
RUN mkdir -p /home/${PRIMARY_USER}/miniconda3 \
    && wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /home/${PRIMARY_USER}/miniconda3/miniconda.sh \
    && bash /home/${PRIMARY_USER}/miniconda3/miniconda.sh -b -u -p /home/${PRIMARY_USER}/miniconda3 \
    && rm /home/${PRIMARY_USER}/miniconda3/miniconda.sh \
    && source ~/miniconda3/bin/activate \
    && conda init --all

# Create Conda env
COPY ../../environment.yml /tmp/environment.yml
RUN /home/${PRIMARY_USER}/miniconda3/bin/conda env create -n ${CONDA_ENV_NAME} -f /tmp/environment.yml
RUN echo "conda activate ${CONDA_ENV_NAME}" >> ~/.zshrc && \
    echo "conda activate ${CONDA_ENV_NAME}" >> ~/.bashrc

# Use Poetry from inside the activated Conda environment
COPY ../../pyproject.toml ../../poetry.lock* /tmp/poetry_env/
WORKDIR /tmp/poetry_env

RUN /bin/bash -c "source /home/${PRIMARY_USER}/miniconda3/bin/activate ${CONDA_ENV_NAME} && poetry install --no-root"

# Change to root to remove directory under /tmp
USER root
RUN rm -rf /tmp/poetry_env
USER ${PRIMARY_USER}

# RUN sudo mkdir /home/${PRIMARY_USER}/project
WORKDIR /home/${PRIMARY_USER}/project

