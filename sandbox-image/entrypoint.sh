#!/bin/bash
# sandbox-image/entrypoint.sh

# Start virtual display for browser
Xvfb :99 -screen 0 1280x800x24 -nolisten tcp &

# Execute command or keep alive
exec "$@"
