#!/bin/bash
set -e

source /opt/video_transcode/config/celery.conf

${CELERY_BIN} worker -A ${CELERY_APP} \
    --loglevel=${CELERYD_LOG_LEVEL} --pidfile= \
    --hostname ${CELERY_HOSTNAME} ${CELERYD_OPTS}