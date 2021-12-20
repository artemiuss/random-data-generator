#!/usr/bin/env python3
import sys, os, json, logging, random, uuid
from datetime import datetime

def get_config(working_dir_path, key):
    with open(os.path.join(working_dir_path, 'config', 'config.json')) as json_file:
        try:
            dict_conf = json.load(json_file)
            return dict_conf[key]
        except:
            raise

def get_mapping(working_dir_path):
    mapping_file = get_config(working_dir_path, "MappingFile")
    with open(os.path.join(working_dir_path, 'config', mapping_file)) as json_file:
        try:        
            dict_map = json.load(json_file)
            return dict_map
        except:
            raise

def get_dictionary(working_dir_path, key):
    dictionary_file = get_config(working_dir_path, "DictionaryFile")
    with open(os.path.join(working_dir_path, 'config', dictionary_file)) as json_file:
        try:        
            dict_dictionary = json.load(json_file)
            return dict_dictionary[key]
        except:
            raise        

def compose_record(tab):
    """
    column_data_gen_rules:
        - "list"  -- get column values randomly from the list defined in "column_data_gen_rules_attr" (only applicable for the string columns)
        - "dict"  -- get column values randomly from the dictionary; dictionary's name is defined in "column_data_gen_rules_attr" (only applicable for the string columns)
        - "range" -- get column values randomly from the range defined in "column_data_gen_rules_attr" (only applicable for the int and datetime columns)
        - ""      -- set column values to empty string (for string types)
        - "null"  -- set column values to null 
        - "uuid"  -- generate uuid and set as column value
    """
    columns = tab.get("columns")
    column_types = tab.get("column_types")
    column_data_gen_rules = tab.get("column_data_gen_rules")
    column_data_gen_rules_attr = tab.get("column_data_gen_rules_attr")
    delimiter = get_config(script_dir_path, "OutputFileDelimiter")
    date_format = get_config(script_dir_path, "OutputDateFormat")   
    null_as_NULL = get_config(script_dir_path, "OutNullAsNULL")
    quote_strings = get_config(script_dir_path, "OutQuoteStrings")

    col_values = []
    
    for index, col in enumerate(columns):
        col_type = column_types[index]
        col_rule = column_data_gen_rules[index]
        col_rul_attr = column_data_gen_rules_attr[index]

        if col_rule == "list":
            col_value = random.choice(col_rul_attr)            
        elif col_rule == "dict":
            dictionary = get_dictionary(script_dir_path, col_rul_attr)
            col_value = random.choice(dictionary)
        elif col_rule == "range":
            if col_type == "int":
                col_value = random.randint(col_rul_attr[0], col_rul_attr[1])
            elif col_type == "datetime":
                col_value = datetime.fromtimestamp(
                                                   random.randint(
                                                                  datetime.fromisoformat(col_rul_attr[0]).timestamp()
                                                                 ,datetime.fromisoformat(col_rul_attr[1]).timestamp()
                                                                 )
                                                  ).strftime(date_format)
        elif col_rule == "":
            col_value = ""
        elif col_rule is None:
            col_value = None
        elif col_rule == "uuid":
            col_value = uuid.uuid4()

        if col_value is None:
            if null_as_NULL:
                col_value = "NULL"
            else:
                col_value = ""

        if col_type == "str" and quote_strings:
            col_value = "\"" + col_value + "\""
        
        col_values.append(str(col_value))

    rec =  delimiter.join(col_values)
    return rec
                 
def main():
    logging.info('Random data generation has been started')
    logging.info('script_dir_path: ' + script_dir_path)
    mapping = get_mapping(script_dir_path)
    delimiter = get_config(script_dir_path, "OutputFileDelimiter")
    file_extestion = get_config(script_dir_path, "OutputFileExtension")
    output_dir = get_config(script_dir_path, "OutputDir")
    output_path = os.path.join(script_dir_path, output_dir)

    try:
       for tab in mapping:
           # Open file
           output_filename = tab.get("table_name") + "." + file_extestion
           f = open(os.path.join(output_path, output_filename), "w+")

           # Generate header
           columns = tab.get("columns")
           header =  delimiter.join(columns)
           f.write(header + '\n')

           # Generate records
           for i in range(tab.get("rows_generated_number")):
               rec = compose_record(tab)
               f.write(rec + '\n')

           # Close file
           f.close()
    except Exception as e:
        logging.error('{0}'.format(e))
        raise

    logging.info('Random data generation has been finished')

if __name__ == '__main__':
    sys_ags = sys.argv
    script_dir_path = sys_ags[1]

    log_dir = get_config(script_dir_path, "LogDir")
    logfile_name = datetime.now().strftime('random_data_gen_%Y-%m-%d_%H-%M-%S.log')
    logfile_path = os.path.join(script_dir_path, log_dir, logfile_name)
    logging.basicConfig(filename=logfile_path, format='%(asctime)s %(message)s', level=logging.INFO)
    main()
