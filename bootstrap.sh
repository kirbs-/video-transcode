#!/bin/bash
set -e

source /opt/video_transcode/config/celery.conf

# ${CELERY_BIN} multi start ${CELERYD_NODES} \
#   -A ${CELERY_APP} --pidfile=${CELERYD_PID_FILE} \
#   --logfile=${CELERYD_LOG_FILE} --loglevel=${CELERYD_LOG_LEVEL} ${CELERYD_OPTS} &

# exec sleep infinity

${CELERY_BIN} worker -A ${CELERY_APP} \
    --loglevel=${CELERYD_LOG_LEVEL} --pidfile=${CELERYD_PID_FILE} \
    --hostname ${CELERY_HOSTNAME} ${CELERYD_OPTS}