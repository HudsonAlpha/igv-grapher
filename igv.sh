#!/bin/sh

#Customized from /cluster/lab/gcooper/software/IGV_Linux_2.11.0/igv.sh for gcooperlab igv grapher

#This script is intended for launch on *nix machines

#-Xmx4g indicates 4 gb of memory.
#To adjust this (or other Java options), edit the "$HOME/.igv/java_arguments"
#file.  For more info, see the README at
#https://raw.githubusercontent.com/igvteam/igv/master/scripts/readme.txt
#Add the flag -Ddevelopment = true to use features still in development
#Add the flag -Dsun.java2d.uiScale=2 for HiDPI displays
grapher_path=/cluster/lab/gcooper/igv-grapher/
igv_path=/cluster/lab/gcooper/software/IGV_Linux_2.11.0
#igv_path=/gpfs/gpfs2/software/igv-2.4.13/
# Custom setup to fix issues
# I think this should help a problem I ran into where multiple instances of the script were hanging trying to get a lock on a settings file
# https://stackoverflow.com/questions/23960451/java-system-preferences-under-different-users-in-linux

TMP_SYS=$(mktemp -d)
TMP_USER=$(mktemp -d)
TMP_IO=$(mktemp -d)
TMP_DIR=$(mktemp -d)
TMP_PREFS=$(mktemp)
chmod 777 $TMP_SYS
chmod 777 $TMP_USER
chmod 777 $TMP_IO
chmod 777 $TMP_PREFS



# Check whether or not to use the bundled JDK
if [ -d "${igv_path}/jdk-11" ]; then
    echo "Using bundled JDK."
    JAVA_HOME="${igv_path}/jdk-11"
    PATH=$JAVA_HOME/bin:$PATH
else
    echo "Couldn't find bundled JDK."
    #exit 1
fi

java -showversion --module-path=${igv_path}/lib -Xmx4g \
    @"${grapher_path}/igv.args" \
    -Dapple.laf.useScreenMenuBar=true \
    -Djava.net.preferIPv4Stack=true \
    -Djava.util.prefs.systemRoot=${TMP_SYS} \
    -Djava.util.prefs.userRoot=${TMP_USER} \
    @"${grapher_path}/java_arguments" \
    --module=org.igv/org.broad.igv.ui.Main -o /cluster/lab/gcooper/igv-grapher/prefs.properties "$@" \
    --igvDirectory ${TMP_DIR} \

echo "Cleanup"
#rm -r ${TMP_SYS} ${TMP_USER} ${TMP_IO} ${TMP_DIR} ${TMP_PREFS}
