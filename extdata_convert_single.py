#!/usr/bin/env python3
from OldPrimaryExports import OldPrimaryExports
from yaml import load,dump
import argparse
import os

def parse_args():
    p = argparse.ArgumentParser(description='Converter for old extdata rc files to yaml format')
    p.add_argument('input',type=str,help='example file',default=None)
    return vars(p.parse_args())

if __name__ == '__main__':

   args = parse_args()
   input_file = args['input']
   f = open(input_file,"r")
   input_rc = f.readlines()
   f.close()

   if input_file[:2] == "./":
      full_path = input_file[2:]
   else:
      full_path = input_file

   split_string = full_path.rsplit(".",1)
   output_file = split_string[0]+".yaml"

   base_file = os.path.basename(full_path)
   split_string = base_file.split("_")
   gridcomp = split_string[0]

   samp_vec = []
   coll_vec = []
   sample_map = {}
   coll_map = {}

   f = open(output_file,"w")

   entries = OldPrimaryExports(input_rc)
   coll_map,coll_vec = entries.generate_new_collections(coll_map,coll_vec,gridcomp)
   output_yaml = dump(coll_map)+"\n"

   sample_map,samp_vec = entries.generate_new_samplings(sample_map,samp_vec,gridcomp)
   output_yaml = output_yaml+dump(sample_map)+"\n"

   export_map = entries.generate_new_exports()
   output_yaml = output_yaml+dump(export_map)+"\n"

   derived_map = entries.generate_new_derived()
   if derived_map:
      output_yaml = output_yaml+dump(derived_map)+"\n"

   lines = output_yaml.split("\n")
   for line in lines:
       stripped_line = line.lstrip()
       if len(stripped_line) > 0:
          if stripped_line[0] == "-":
             line = "  " + line
       f.write(line+"\n")

   
