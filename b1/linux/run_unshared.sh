#!/bin/bash

unshare -Ur "$(dirname "$(realpath "${BASH_SOURCE[0]}")")"/itsec-game.x86_64
