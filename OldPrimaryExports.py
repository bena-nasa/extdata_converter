#!/usr/bin/env python3

import shlex

class OldPrimaryExports: 

   __zero_freq = "PT0S"

   @staticmethod
   def get_primary(exports,input_rc):
       i = 0
       found_start = False
       found_block = False
       for line in input_rc:
           if "PrimaryExports%%" in line:
               start = i+1
               found_start = True
           elif found_start and ("%%" in line):
               end = i
               found_block = True
               break
           i=i+1

       if found_block:
          for i in range(start,end):
              exports.append(input_rc[i].strip())
          exports = OldPrimaryExports.get_primary(exports,input_rc[end+1:])

       return(exports)

   @staticmethod
   def get_derived(derived,input_rc):
       i = 0
       found_start = False
       found_block = False
       for line in input_rc:
           if "DerivedExports%%" in line:
               start = i+1
               found_start = True
           elif found_start and ("%%" in line):
               end = i
               found_block = True
               break
           i=i+1

       if found_block:
          for i in range(start,end):
              derived.append(input_rc[i].strip())
          derived = OldPrimaryExports.get_derived(derived,input_rc[end+1:])

       return(derived)

   @classmethod
   def create_primary_entry(cls,entry):

       options = shlex.split(entry)

       vals = {}
       vals.update({"clim":options[2].lower()})
       vals.update({"regrid":options[3].lower()})
       vals.update({"refresh":options[4].lower()})
       vals.update({"offset":options[5].lower()})
       vals.update({"scale":options[6].lower()})
       vals.update({"var":options[7]})
       vals.update({"templ":options[8]})

       return {options[0]:vals}

   @classmethod
   def create_derived_entry(cls,entry):

       options = shlex.split(entry)
       vals = {}
       vals.update({"function":options[1]})
       vals.update({"refresh":options[2].lower()})

       return {options[0]:vals}

   @classmethod
   def create_default_entry(cls):

       vals = {}
       vals.update({"clim":"n"})
       vals.update({"regrid":"n"})
       vals.update({"refresh":"0"})
       vals.update({"scale":"none"})
       vals.update({"offset":"none"})
       vals.update({"var":"na"})
       vals.update({"templ":"na"})

       return {"default_export":vals}

   @classmethod
   def generate_pathkey_name(cls,filepath):
       if "/" in filepath:
          tstring = filepath.rsplit("/",1)
          return(tstring[1])
       else:
          return filepath

   @classmethod
   def convert_inttime_to_iso(cls,str_time):
       int_time =  int(str_time)
       hour = int_time//10000
       minute = (int_time%10000)//100
       second = int_time%100
       duration = "PT"
       if hour != 0:
          duration=duration+str(hour)+"H"
       if minute != 0:
          duration=duration+str(minute)+"M"
       if second != 0:
          duration=duration+str(second)+"S"
       if duration == "PT":
          duration = cls.__zero_freq
       return duration

   @classmethod 
   def generate_duration(cls,hour,minute,second):
       if "%" in hour:
           hour = "0"
       if "%" in minute:
           minute = "0"
       if "%" in second:
           second = "0"

       duration = "PT"
       if hour != "0" and hour != "00":
          duration = duration + hour +"H"
       if minute != "0" and minute != "00":
          duration = duration + minute +"M"
       #if second != "0" and second != "00":
          #duration = duration + second +"S"
       if duration == "PT":
          duration =  cls.__zero_freq
       return duration

   @classmethod
   def generate_freq_offset_reff(cls,old_sample):

       reff = "0"
       (before_token,after_token) = old_sample.rsplit("%",1)
       token = after_token[0]
       if token == "y":
          freq = "P1Y"
       elif token == "m":
          freq = "P1M"
       elif token == "d":
          freq = "PT24H"
       elif token == "h":
          freq = "PT1H"
       elif token == "n":
          freq = "PT1M"
      
       (date,time) = old_sample.split("t")
       count_colon = time.count(":")
       if count_colon == 1:
          (hours,minutes)=time.split(":")
          offset = cls.generate_duration(hours,minutes,"0")
       elif count_colon ==2:
          (hours,minutes,seconds)=time.split(":")
          offset = cls.generate_duration(hours,minutes,seconds)
       return (freq,offset,reff)

   @classmethod
   def generate_sampling_map(cls,old_sample, old_clim):

       frequency = cls.__zero_freq
       offset = cls.__zero_freq
       has_offset = False
       has_frequency = False
       has_ref_time = False
       is_fix = False
       is_clim = False
       has_climyear = False
       persist_closest = False

       if "f" == old_sample[0]:
          is_fix = True
          old_sample = old_sample[1:]

       if "%" in old_sample:
          has_ref_time = True
          (frequency,offset,ref_time) = cls.generate_freq_offset_reff(old_sample)
       else:
          if old_sample == "-":
             persist_closest = True
          else:
             if ";" in old_sample:
                 templ = old_sample.split(";")
                 offset = cls.convert_inttime_to_iso(templ[1])
                 old_sample = templ[0]
           
             if old_sample == "0":
                default_freq = True
             else:
                # To do!
                #frequency = cls.convert_inttime_to_iso(old_sample)
                default_freq = True

       if frequency != cls.__zero_freq:
          has_frequency = True
       if offset != cls.__zero_freq:
          has_offset = True

       if old_clim != "n":
          is_clim = True
          if old_clim != "y":
             has_climyear= True
             climyear = old_clim
      
       sample_map={}
       if persist_closest:
          sample_map.update({"extrapolation":"persist_closest"})
       if is_clim:
          sample_map.update({"extrapolation":"clim"})
       if is_fix:
          sample_map.update({"time_interpolation":"False"})
       if has_frequency:
          sample_map.update({"update_frequency":frequency})
       if has_offset:
          sample_map.update({"update_offset":offset})
       if has_ref_time:
          sample_map.update({"update_reference_time":ref_time})
       return sample_map

   @classmethod
   def generate_regrid(cls,regrid_line):
       if regrid_line == "n":
          return "default"
       elif regrid_line == "y":
          return "CONSERVE"
       elif regrid_line == "v":
          return "VOTE"
       elif regrid_line[0] == "f":
          tstr = regrid_line.split(";")
          fraction = "FRACTION;"+tstr[1]
          return fraction

   @classmethod
   def generate_scale(cls,offset,scale):
       if scale.strip() == "none":
          int_scale = 1.0
       else:
          int_scale = float(scale)

       if offset.strip() == "none":
          int_offset = 0.0
       else:
          int_offset = float(offset)
       if int_offset == 0.0 and int_scale == 1.0:
          return []
       else:
          return[int_offset,int_scale]
       
       

   def __init__(self,input_rc):

       primary_exports = []
       derived_exports = []
       primary_exports = self.get_primary(primary_exports,input_rc)
       derived_exports = self.get_derived(derived_exports,input_rc)
       self.exports = {}
       self.derived = {}
       for line in primary_exports:
           if ("#" not in line) and (line != ""):
              self.exports.update(self.create_primary_entry(line))

       for line in derived_exports:
           if ("#" not in line) and (line != ""):
              self.derived.update(self.create_derived_entry(line))

   def get_exports(self):
       return self.exports

   def generate_new_collections(self,collection_map,unique_paths,gridcomp):

       if gridcomp != "":
          prefix = gridcomp+"_"
       else:
          prefix = ""

       self.collections = {}

       if collection_map:
          tmap = collection_map["Collections"]
       else:
          collection_map = {"Collections":{}}
          tmap = {}
       for key in self.exports:
           export = self.exports[key]
           filepath = export["templ"]
           if "/dev/null" not in filepath:
              if filepath not in unique_paths:
                 unique_paths.append(filepath)
                 pathkey = self.generate_pathkey_name(filepath)
                 pathkey = prefix + pathkey
                 self.collections.update({key:pathkey})
                 pathmap = {"template":filepath}
                 tmap.update({pathkey:pathmap})
                 collection_map.update({"Collections":tmap})
              else:
                 pathkey = self.generate_pathkey_name(filepath)
                 pathkey = prefix + pathkey
                 self.collections.update({key:pathkey})
           else:
              self.collections.update({key:"/dev/null"})
       return collection_map,unique_paths

   def generate_new_samplings(self,sampling_map,samplings_list,gridcomp):

       if gridcomp != "":
          prefix = gridcomp+"_"
       else:
          prefix = ""
       
       self.samplings = {}

       if sampling_map:
          tmap = sampling_map["Samplings"]
       else:
          sampling_map = {"Samplings":{}}
          tmap = {}
       for key in self.exports:
           export = self.exports[key]
           refresh = export["refresh"]
           clim = export["clim"]
           refresh = refresh.strip()
           clim = clim.strip()
           smap = self.generate_sampling_map(refresh,clim)
           if smap:
              if smap not in samplings_list:
                 samplings_list.append(smap)
                 ith = len(samplings_list)-1
                 tmap.update({prefix+"sample_"+str(ith):smap})
                 sampling_map.update({"Samplings":tmap})
              else:
                 for i in range(len(samplings_list)):
                     if smap == samplings_list[i]:
                        ith = i
              sample_key = prefix+"sample_"+str(ith)
              self.samplings.update({key:sample_key})

       for key in self.derived:
           derived = self.derived[key]
           refresh = derived["refresh"]
           refresh = refresh.strip()
           clim = "n"
           smap = self.generate_sampling_map(refresh,clim)
           if smap:
              if smap not in samplings_list:
                 samplings_list.append(smap)
                 ith = len(samplings_list)-1
                 tmap.update({prefix+"sample_"+str(ith):smap})
                 sampling_map.update({"Samplings":tmap})
              else:
                 for i in range(len(samplings_list)):
                     if smap == samplings_list[i]:
                        ith = i
              sample_key = prefix+"sample_"+str(ith)
              self.samplings.update({key:sample_key})

       return sampling_map,samplings_list


   def generate_new_exports(self):

       export_map = {"Exports":{}}
       emap = {}
       for key in self.exports:
           export = self.exports[key]
           tmap = {}
           tmap.update({"collection":self.collections[key]})
           if self.collections[key] != "/dev/null":
              tmap.update({"variable":export["var"]})
              if key in self.samplings:
                 tmap.update({"sample":self.samplings[key]})

              regrid = self.generate_regrid(export["regrid"])
              if regrid != "default":
                 tmap.update({"regrid":regrid})

              linear_trans = self.generate_scale(export["offset"],export["scale"])
              if linear_trans != []:
                 tmap.update({"linear_transformation":linear_trans})
              


           emap.update({key:tmap})
           export_map.update({"Exports":emap})
       return export_map 

   def generate_new_derived(self):

       if self.derived:
          export_map = {"Derived":{}}
          emap = {}
          for key in self.derived:
              export = self.derived[key]

              tmap = {}
              func = export["function"]
              tmap.update({"function":func})

              if key in self.samplings:
                 tmap.update({"sample":self.samplings[key]})

              emap.update({key:tmap})
              export_map.update({"Derived":emap})
       else:
          export_map = {}
       return export_map 

