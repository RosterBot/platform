#!/bin/bash

PYTHON=$(which python)

test -z $PYTHON && echo "Could not find python executable." && exit 11
echo "Found python at $PYTHON, checking version..."

## Our minimum version is 2.7.2, which is the version
## that comes by default on the latest Mac OS X as of this writing.
MINMAJOR=2
MINMINOR=7
MINPATCHLEVEL=2

VERSION=$($PYTHON --version 2>&1 | cut -f 2 -d " ")

MAJOR=$(echo $VERSION | perl -ane 'print m/^(\d+)\.\d+\.\d+$/;')
MINOR=$(echo $VERSION | perl -ane 'print m/^\d+\.(\d+)\.\d+$/;')
PATCHLEVEL=$(echo $VERSION | perl -ane 'print m/^\d+\.\d+\.(\d+)$/;')

VERSIONERROR="Your version of python is too old. Please update."

if [[ $MAJOR -ge $MINMAJOR ]]
then
	if [[ $MINOR -ge $MINOR ]]
	then
		if [[ $PATCHLEVEL -ge $MINPATCHLEVEL ]]
		then
			echo "Version $VERSION is okay, minimum was $MINMAJOR.$MINMINOR.$MINPATCHLEVEL..."
			exit 0 # all good
		else
			echo $VERSIONERROR && exit 12
		fi
	else
		echo $VERSIONERROR && exit 12
	fi
else
	echo $VERSIONERROR && exit 12
fi
