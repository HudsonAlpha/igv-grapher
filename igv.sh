#!/bin/sh

#This script is intended for launch on *nix machines

#-Xmx4000m indicates 4000 mb of memory, adjust number up or down as needed
#Script must be in the same directory as igv.jar
#Add the flag -Ddevelopment = true to use features still in development


IGV_MEM=${IGV_MEM:-4000m}
TMP_SYS=$(mktemp -d)
TMP_USER=$(mktemp -d)
TMP_IO=$(mktemp -d)
chmod 775 $TMP_SYS
chmod 775 $TMP_USER
chmod 775 $TMP_IO
prefix=/gpfs/gpfs2/software/igv-2.4.13/
exec java -Xmx${IGV_MEM} \
    -Dapple.laf.useScreenMenuBar=true \
    -Djava.net.preferIPv4Stack=true \
    -Djava.util.prefs.systemRoot=${TMP_SYS} \
    -Djava.util.prefs.userRoot=${TMP_USER} \
    -Djava.io.tmpdir=${TMP_IO} \
    -jar "$prefix"/igv.jar "$@"

# I think this should help a problem I ran into where multiple instances of the script were hanging trying to get a lock on a settings file
# https://stackoverflow.com/questions/23960451/java-system-preferences-under-different-users-in-linux
