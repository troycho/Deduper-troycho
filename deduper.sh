#!/bin/bash

#SBATCH --account=bgmp
#SBATCH --partition=bgmp
#SBATCH -c 4
#SBATCH --mem=16G
#SBATCH --time=1-0

conda activate bgmp_star
/usr/bin/time -v ./Roychowdhury_deduper.py \
    -f sorted_C1_SE.sam \
    -o realoutput.sam \
    -u STL96.txt