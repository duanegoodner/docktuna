FROM python:3.11.11-slim-bookworm
ARG PRIMARY_UID
ARG PRIMARY_GID
ARG PRIMARY_USER
ARG COMPONENTS=./image_resources/components

SHELL [ "/bin/bash", "--login", "-c" ]

COPY ${COMPONENTS}/create_sudo_user /tmp/create_sudo_user
RUN /tmp/create_sudo_user/main.sh ${PRIMARY_USER} ${PRIMARY_UID} ${PRIMARY_GID}\
    && sudo rm -rf /tmp/create_sudo_user

USER ${PRIMARY_USER}
ARG BUILD_DIR=/home/${PRIMARY_USER}/docker_build
WORKDIR ${BUILD_DIR}

RUN sudo apt-get update && \
    sudo apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    git \
    curl \
    wget \
    zsh \
    nano \
    && sudo rm -rf /var/lib/apt/lists/*

COPY ${COMPONENTS}/zsh_setup ${BUILD_DIR}/zsh_setup
RUN ${BUILD_DIR}/zsh_setup/main.sh ${PRIMARY_USER} \
    && sudo rm -rf ${BUILD_DIR}/*

# Install Poetry (as PRIMARY_USER)
RUN curl -sSL https://install.python-poetry.org | python3 -

# Ensure Poetry is in PRIMARY_USER's PATH
ENV PATH="/home/${PRIMARY_USER}/.local/bin:$PATH"

# Persist Poetry's path in user's profile for interactive sessions
RUN echo 'export PATH="/home/${PRIMARY_USER}/.local/bin:$PATH"' >> /home/${PRIMARY_USER}/.bashrc && \
    echo 'export PATH="/home/${PRIMARY_USER}/.local/bin:$PATH"' >> /home/${PRIMARY_USER}/.profile


# Upgrade pip and install Python packges
# RUN pip install --no-cache-dir --upgrade pip \
#     && pip install --no-cache-dir dotenv optuna psycopg2 isort black

# # #####################################################
# # Done installing things in container
# # #####################################################

RUN sudo mkdir /home/${PRIMARY_USER}/project
WORKDIR /home/${PRIMARY_USER}/project
RUN sudo rm -rf ${BUILD_DIR}

RUN sudo mkdir -p /usr/local/entrypoints
COPY ./image_resources/entrypoint_simple_persistence.sh /usr/local/entrypoints
