#!/usr/bin/env python3
from OldPrimaryExports import OldPrimaryExports
from yaml import load,dump
import argparse
import os

def parse_args():
    p = argparse.ArgumentParser(description='Converter for old extdata rc files to yaml format')
    p.add_argument('input',type=str,help='example file',default=None)
    p.add_argument('sample_coll',type=str,help='example file',default=None)
    return vars(p.parse_args())

if __name__ == '__main__':

   args = parse_args()
   input_file_list = args['input']
   samples_and_colls = args['sample_coll']

   f = open(input_file_list,"r")
   input_files = f.readlines()

   coll_vec = []
   samp_vec = []
   sample_map = {}
   coll_map = {}
   for input_file in input_files:

      input_file = input_file.strip()
      basepath = os.path.dirname(input_file)
      filename = os.path.basename(input_file)
      split_string = filename.split(".")

      basename = split_string[0]
      output_file = basepath+"/"+basename+".yaml"
      print("converting: ",input_file)

      f = open(input_file,"r")
      input_rc = f.readlines()
      f.close()

      f = open(output_file,"w")

      entries = OldPrimaryExports(input_rc)
      coll_map,coll_vec = entries.generate_new_collections(coll_map,coll_vec)

      sample_map,samp_vec = entries.generate_new_samplings(sample_map,samp_vec)

      export_map = entries.generate_new_exports()
      output_yaml = dump(export_map)

      lines = output_yaml.split("\n")
      for line in lines:
          stripped_line = line.lstrip()
          if len(stripped_line) > 0:
             if stripped_line[0] == "-":
                line = "  " + line
          f.write(line+"\n")
      f.close

  
   output_yaml_sample = dump(sample_map)
   f = open(samples_and_colls+".yaml","w")
   lines = output_yaml_sample.split("\n")
   for line in lines:
       stripped_line = line.lstrip()
       if len(stripped_line) > 0:
          if stripped_line[0] == "-":
             line = "  " + line
       f.write(line+"\n")

   output_yaml_sample = dump(coll_map)
   lines = output_yaml_sample.split("\n")
   for line in lines:
       stripped_line = line.lstrip()
       if len(stripped_line) > 0:
          if stripped_line[0] == "-":
             line = "  " + line
       f.write(line+"\n")


   f.close()



   
