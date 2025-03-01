FROM python:3.11-bookworm

ARG PRIMARY_UID
ARG PRIMARY_GID
ARG PRIMARY_USER
ARG COMPONENTS=./app_resources/components

SHELL [ "/bin/bash", "--login", "-c" ]

# Upgrade pip and install Optuna
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir dotenv optuna psycopg2 toml

COPY ${COMPONENTS}/create_sudo_user /tmp/create_sudo_user
RUN /tmp/create_sudo_user/main.sh ${PRIMARY_USER} ${PRIMARY_UID} ${PRIMARY_GID}\
    && sudo rm -rf /tmp/create_sudo_user

USER ${PRIMARY_USER}
ARG BUILD_DIR=/home/${PRIMARY_USER}/docker_build
WORKDIR ${BUILD_DIR}

COPY ${COMPONENTS}/install_apt_pkgs ${BUILD_DIR}/install_apt_pkgs
COPY ./app/pkglist ${BUILD_DIR}/pkglist
RUN ${BUILD_DIR}/install_apt_pkgs/main.sh ${BUILD_DIR}/pkglist \
    && sudo rm -rf ${BUILD_DIR}/*

COPY ${COMPONENTS}/zsh_setup ${BUILD_DIR}/zsh_setup
RUN ${BUILD_DIR}/zsh_setup/main.sh ${PRIMARY_USER} \
    && sudo rm -rf ${BUILD_DIR}/*

# # #####################################################
# # Done installing things in container
# # #####################################################

RUN sudo mkdir /home/${PRIMARY_USER}/project
WORKDIR /home/${PRIMARY_USER}/project
RUN sudo rm -rf ${BUILD_DIR}

RUN sudo mkdir -p /usr/local/entrypoints
COPY ./app_resources/entrypoint_simple_persistence.sh /usr/local/entrypoints
