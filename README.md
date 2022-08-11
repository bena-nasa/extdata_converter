# extdata_converter
Some python scripts for converting a RC based ExtData files YAML based files

# Use
extdata_convert_single.py takes a single file as an argument and creates a converted extdata file in the yaml format with the same base filename but a .yaml extension

extdata_convert_list.py takes a list of files and converts every file in the list. The first argument is the list of files. This is a plain text file with one file per line. It also needs a 2nd argument which is the basename to use for the collection and sampling arguments. All collection and sampling information will be put in the collection and sampling file. Each original RC file will have a yaml verison with the same basename and a .yaml extention
