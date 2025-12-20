#!/bin/bash

set -e
set -o pipefail

ROOT="$(realpath "$(dirname "${BASH_SOURCE[0]}")"/..)"

echo "Building Docker image; might take a while..."
IMAGE="$(docker build -q - <<EOF
FROM debian:trixie

RUN apt-get update
RUN apt-get install -y --no-install-recommends \
	libxcursor1 libxinerama1 libxrandr2 libxi6 libgl1 libpulse0

CMD ["/game/linux/itsec-game.x86_64"]
EOF
)"
echo "Building image done"

echo "Preparing run arguments..."

RUN=()
RUN+=(docker run)

# Basics
RUN+=(
	# mount actual game in container
	-v "$ROOT":/game
	# recognizable name for docker ps and the like
	--name itsec-game
	# keep in foreground
	-it
	# let container be cancelable with Ctrl+C / SIGINT
	--init
	# remove container after it exited
	--rm
)

# Config persistence
RUN+=(
	# keep same uid / gid as caller
	-u "$(id -u):$(id -g)"
	# mount home of caller
	-v "$HOME":/home/user
	--env HOME=/home/user
)

# Display via X11
RUN+=(
	# make X11 socket accessible:
	# either TCP port 6000 on older systems
	# or Unix socket in abstract socket namespace
	--network host
	# with network=host, X11 is accessible the same way as outside of container
	--env DISPLAY
)
if [ "$XAUTHORITY" != "" ]; then
	# Xauthority file exists - forward it too.
	RUN+=(
		-v "$XAUTHORITY":/xauthority
		--env XAUTHORITY=/xauthority
	)
fi

# Forward available video cards to not eat unreasonable amounts of CPU
for vc in $(find /dev/dri -writable -name 'card*'); do
	RUN+=(--device "$vc")
done

# Audio via PulseAudio
RUN+=(
	-v /run/user/"$(id -u)":/run/user/"$(id -u)"
	--env XDG_RUNTIME_DIR=/run/user/"$(id -u)"
)

# Append image to run - has to go last
# because anything after image is interpreted as command to execute
RUN+=("$IMAGE")

echo "Running!"
"${RUN[@]}"
