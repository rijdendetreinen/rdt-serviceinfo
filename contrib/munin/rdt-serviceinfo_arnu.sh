#!/bin/sh

case $1 in
   config)
        cat <<'EOM'
graph_title ARNU information
graph_vlabel per ${graph_period}
graph_args --base 1000
graph_scale no
graph_category rdt-serviceinfo
graph_info ARNU information
graph_period minute
messages.label messages
messages.info Number of messages
messages.type DERIVE
messages.min 0
messages.colour a11313
services.label services
services.info Number of services
services.type DERIVE
services.min 0
services.colour 0b6161


EOM
        exit 0;;
esac

# Place your installation directory here:
cd /opt/rdt/serviceinfo

printf "messages.value "
./stats.py messages
printf "services.value "
./stats.py services
