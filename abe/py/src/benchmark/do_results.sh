#!/bin/bash


#for i in SS512 MNT159 SS1024 MNT201 MNT224; do for j in bsw07 bsw08 waters09 rw12 ot12; do python3 avg_res.py $i $j; done; done
#SS1024 - is not working on OSX :'(
for i in SS512 MNT159 MNT201 MNT224; do for j in bsw07 bsw08 waters09 rw12 ot12; do python3 avg_res.py $i $j; done; done
python3 results2tex.py

