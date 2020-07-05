#!/bin/bash
set -e

source /opt/video_transcode/config/celery.conf

${CELERY_BIN} worker -A ${CELERY_APP} \
    --loglevel=${CELERYD_LOG_LEVEL} --pidfile=${CELERYD_PID_FILE} \
    --hostname ${CELERY_HOSTNAME} ${CELERYD_OPTS}