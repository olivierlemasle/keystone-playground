#!/usr/bin/env bash
# Plugin file for keystone-playground services
# -------------------------------

# Dependencies:
# ``functions`` file
# ``DEST``, ``DATA_DIR``, ``STACK_USER`` must be defined

# Save trace setting
XTRACE=$(set +o | grep xtrace)
set -o xtrace


# Support entry points installation of console scripts
if [[ -d $KEYSTONE_PLAYGROUND_DIR/bin ]]; then
    KEYSTONE_PLAYGROUND_BIN_DIR=$KEYSTONE_PLAYGROUND_DIR/bin
else
    KEYSTONE_PLAYGROUND_BIN_DIR=$(get_python_exec_prefix)
fi


function mkdir_chown_stack {
    if [[ ! -d "$1" ]]; then
        sudo mkdir -p "$1"
    fi
    sudo chown $STACK_USER "$1"
}

# create_keystone-playground_account() - Set up required Keystone user
#
# Project     User                    Roles
# --------------------------------------------
# service     keystone-playground     admin
function create_keystone-playground_user() {
    if ! is_service_enabled key; then
        return
    fi

    create_service_user $KEYSTONE_PLAYGROUND_ADMIN_USER

    if [[ "$KEYSTONE_CATALOG_BACKEND" = 'sql' ]]; then
        get_or_create_service "keystoneplayground" "keystone-playground" "Keystone Playground"
        get_or_create_endpoint "keystone-playground" \
            "$REGION_NAME" \
            "$KEYSTONE_PLAYGROUND_SERVICE_PROTOCOL://$KEYSTONE_PLAYGROUND_SERVICE_HOST:$KEYSTONE_PLAYGROUND_SERVICE_PORT" \
            "$KEYSTONE_PLAYGROUND_SERVICE_PROTOCOL://$KEYSTONE_PLAYGROUND_SERVICE_HOST:$KEYSTONE_PLAYGROUND_SERVICE_PORT" \
            "$KEYSTONE_PLAYGROUND_SERVICE_PROTOCOL://$KEYSTONE_PLAYGROUND_SERVICE_HOST:$KEYSTONE_PLAYGROUND_SERVICE_PORT"
    fi
}

# configure_keystone-playground() - Set config files, create data dirs, etc
function configure_keystone-playground {
    mkdir_chown_stack "$KEYSTONE_PLAYGROUND_CONF_DIR"

    # Generate keystone-playground configuration file and configure common parameters.
    oslo-config-generator --namespace keystoneplayground \
                          --namespace keystonemiddleware.auth_token \
                          --namespace oslo.middleware.cors \
                          > $KEYSTONE_PLAYGROUND_CONF_FILE

    cp $KEYSTONE_PLAYGROUND_DIR/etc/keystone-playground-paste.ini $KEYSTONE_PLAYGROUND_CONF_DIR

    # Setup keystone_authtoken section
    iniset $KEYSTONE_PLAYGROUND_CONF_FILE keystone_authtoken auth_uri "http://${KEYSTONE_AUTH_HOST}:5000/v2.0"
    iniset $KEYSTONE_PLAYGROUND_CONF_FILE keystone_authtoken auth_host $KEYSTONE_AUTH_HOST
    iniset $KEYSTONE_PLAYGROUND_CONF_FILE keystone_authtoken auth_port $KEYSTONE_AUTH_PORT
    iniset $KEYSTONE_PLAYGROUND_CONF_FILE keystone_authtoken auth_protocol $KEYSTONE_AUTH_PROTOCOL
    iniset $KEYSTONE_PLAYGROUND_CONF_FILE keystone_authtoken cafile $KEYSTONE_SSL_CA
    iniset $KEYSTONE_PLAYGROUND_CONF_FILE keystone_authtoken admin_tenant_name $SERVICE_TENANT_NAME
    iniset $KEYSTONE_PLAYGROUND_CONF_FILE keystone_authtoken admin_user $KEYSTONE_PLAYGROUND_ADMIN_USER
    iniset $KEYSTONE_PLAYGROUND_CONF_FILE keystone_authtoken admin_password $SERVICE_PASSWORD

    iniset $KEYSTONE_PLAYGROUND_CONF_FILE keystoneplayground host $KEYSTONE_PLAYGROUND_SERVICE_HOST
    iniset $KEYSTONE_PLAYGROUND_CONF_FILE keystoneplayground port $KEYSTONE_PLAYGROUND_SERVICE_PORT
}

# install_keystone-playground() - Collect source and prepare
function install_keystone-playground() {
    git_clone $KEYSTONE_PLAYGROUND_REPO $KEYSTONE_PLAYGROUND_DIR $KEYSTONE_PLAYGROUND_BRANCH

    setup_develop $KEYSTONE_PLAYGROUND_DIR
}

# start_keystone-playground() - Start running processes, including screen
function start_keystone-playground() {
    screen_it keystone-playground "cd $KEYSTONE_PLAYGROUND_DIR && $KEYSTONE_PLAYGROUND_BIN_DIR/keystone-playground-api --config-file $KEYSTONE_PLAYGROUND_CONF_DIR/keystone-playground.conf"
}


# stop_keystone-playground() - Stop running processes
function stop_keystone-playground() {
    screen -S $SCREEN_NAME -p keystone-playground -X kill
}


# Main dispatcher

if is_service_enabled keystone-playground; then
    if [[ "$1" == "stack" && "$2" == "install" ]]; then
        echo_summary "Installing keystone-playground"
        install_keystone-playground
    elif [[ "$1" == "stack" && "$2" == "post-config" ]]; then
        echo_summary "Configuring keystone-playground"
        configure_keystone-playground
        create_keystone-playground_user
    elif [[ "$1" == "stack" && "$2" == "extra" ]]; then
        echo_summary "Initializing keystone-playground"
        start_keystone-playground
    fi

    if [[ "$1" == "unstack" ]]; then
        stop_keystone-playground
    fi
fi

# Restore xtrace
$XTRACE
