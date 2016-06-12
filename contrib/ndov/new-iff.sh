#!/bin/bash

if [ -f ../../cache/ns-latest.zip ];
then
	mv ../../cache/ns-latest.zip ../../cache/ns-old.zip
else
	if [ -f ../../cache/ns-old.zip ];
	then
		touch ../../cache/ns-old.zip
	fi;
fi;

# Haal nieuwe dataset op:
wget --quiet http://data.ndovloket.nl/ns/ns-latest.zip -O ../../cache/ns-latest.zip

# Vergelijk files:
diff -u ../../cache/ns-latest.zip ../../cache/ns-old.zip > /dev/null

if [[ $? -ne 0 ]]; then
	echo "Nieuwe dataset!"
	rm ../../cache/dataset/*

	unzip ../../cache/ns-latest.zip -d ../../cache/dataset/
	rm ../../cache/iff_parsed/*.tsv
	../../iff-converter.py --input ../../cache/dataset --config ../../config/serviceinfo.yaml --output ../../cache/iff_parsed
	../../iff-loader.py --parsed_dir ../../cache/iff_parsed --config ../../config/serviceinfo.yaml --truncate_tables
else 
	echo "Opgehaalde dataset is gelijk"
fi;

