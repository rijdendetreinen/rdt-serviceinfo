#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd)/../../"
BASEDIR=`realpath $DIR`

# Check whether base directories exist:
mkdir -p $BASEDIR/cache/dataset
mkdir -p $BASEDIR/cache/iff_parsed

if [ -f $BASEDIR/cache/ns-latest.zip ];
then
	mv $BASEDIR/cache/ns-latest.zip $BASEDIR/cache/ns-old.zip
else
	if [ -f $BASEDIR/cache/ns-old.zip ];
	then
		touch $BASEDIR/cache/ns-old.zip
	fi;
fi;

# Get new dataset:
wget --quiet http://data.ndovloket.nl/ns/ns-latest.zip -O $BASEDIR/cache/ns-latest.zip

# Compare files:
diff -u $BASEDIR/cache/ns-latest.zip $BASEDIR/cache/ns-old.zip > /dev/null

if [[ $? -ne 0 ]]; then
	echo "New dataset!"
	rm $BASEDIR/cache/dataset/*

	unzip $BASEDIR/cache/ns-latest.zip -d $BASEDIR/cache/dataset/
	rm $BASEDIR/cache/iff_parsed/*.tsv
	$BASEDIR/iff-converter.py --input $BASEDIR/cache/dataset --config $BASEDIR/config/serviceinfo.yaml --output $BASEDIR/cache/iff_parsed
	$BASEDIR/iff-loader.py --parsed_dir $BASEDIR/cache/iff_parsed --config $BASEDIR/config/serviceinfo.yaml --truncate_tables
else 
	echo "Retrieved data is equal to existing data"
fi;
