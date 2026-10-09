#!/bin/bash
rm -rf -- `ls | grep -Ev '^(clean\.sh|run\.sh|INFILE)$'`
rm -rf TABLE .OUTPUT_*
