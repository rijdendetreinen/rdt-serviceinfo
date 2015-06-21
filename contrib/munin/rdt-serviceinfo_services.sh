#!/bin/sh

case $1 in
   config)
        cat <<'EOM'
graph_title Total services
graph_vlabel services per ${graph_period}
graph_category rdt-serviceinfo
graph_info Total services
graph_period minute
graph_args --base 1000 -l 0
graph_scale no
graph_printf %3.0lf

scheduled.label Scheduled services
scheduled.info Number of schedules services in store
scheduled.draw AREASTACK
scheduled.colour COLOUR1

actual.label Actual services
actual.info Number of actual services in store
actual.draw AREASTACK
actual.colour COLOUR3

EOM
        exit 0;;
esac

# Place your installation directory here:
cd /opt/rdt/serviceinfo

printf "scheduled.value "
./stats.py scheduled_services
printf "actual.value "
./stats.py actual_services
