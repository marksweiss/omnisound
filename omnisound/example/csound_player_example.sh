#!/usr/bin/env bash

# This is unfortunate, but it solves a problem actually invoking the csound_player_example
# (and the same technique must be used to run any CSound rendering). Unless invoked through the normal
# module path, by a process external to Python, the call to CSound doesn't actually write the output sound file.
# If called from Py subprocess(), the code completes without error, returns a 255 return code, but does not
# write the sound file. If the same call is made from the shell it does write the file.

# So this wrapper calls the Omnisound CSound Player, gets the command it generates, and runs that command
# directly from the shell.

player_module=$1

cmd=`python3 -m omnisound.test.${player_module}`
echo "$cmd"
`(${cmd})`