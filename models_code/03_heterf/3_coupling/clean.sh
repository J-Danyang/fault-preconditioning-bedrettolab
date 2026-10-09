#!/bin/bash
rm -rf `ls | grep -v "^clean.sh\|^run.sh\|^flac3d.sh\|^INFILE\|^flac_output_d.py\|^flac3d.py$"`
rm -rf TABLE .OUTPUT_*
