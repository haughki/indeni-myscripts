"""
- Add a device to Indeni, and then query for the device tags. You can use:
psql -c "select id, name, ip_address from device;"
to get the device UUID, and then the API:
curl -G -k -u "admin:admin123!" https://localhost:9009/api/v1/devices/<Device_UUID>
to get the tags. E.g.,
curl -G -k -u "admin:admin123!" https://localhost:9009/api/v1/devices/4f143b97-57a1-43c9-ad87-bac6c4f2c698 | python -m json.tool
- Copy the tags into a temp file, and then call this script, passing the tags file name and a directory containing
some IND .yaml files. E.g.,
python3 resolve_requires.py temp_tags.tags parsers/src/checkpoint/firewall
- The script will output all IND script names that will run against a device with the passed tags.
"""

import pprint, sys, re, os, warnings
from yaml import load, dump
from pathlib import Path
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

class ProcessYaml:
    def __init__(self, tags_file='', yaml_dir=''):
        self.tags_file = tags_file
        self.yaml_dir = Path(yaml_dir)
        self.requires = None
        self.tags = None
        self.scripts = []

        if self.yaml_dir and self.tags_file:
            self._getFilesMatchingRequirements()
            for script in self.scripts:
                print(script)

    def _getFilesMatchingRequirements(self):
        self._setTags()
        
        # Walk the passed directory to search for .ind files to process
        for dirpath, dirs, files in os.walk(self.yaml_dir):
            for filename in files:
                if filename.endswith('.yaml'):
                    fname = Path(dirpath) / filename
                    #print('-' * 80)
                    #print(fname)
                    
                    file_str = ""
                    with open(fname) as f:
                        for line in f:
                            # If true or false don't have quotes, the YAML parser converts them to Python True and False.
                            # Not what we want.
                            line = re.sub(r':\s*true', r': "true"', line)
                            line = re.sub(r':\s*false', r': "false"', line)
                            file_str = file_str + line

                    #print(fname)
                    #print("file_str: " + file_str)
                    self.requires = load(file_str, Loader=Loader)
                    #pprint.PrettyPrinter(width=1).pprint(self.requires)
                    #self.requires_str = dump(meta_dict, Dumper=Dumper)
                    if 'requires' in self.requires:
                            if self.meetsRequirements():
                                self.scripts.append(fname)
                    else:
                        warnings.warn('No requires section in this .ind script: ' + fname)
        
        self.scripts.sort()


    def _setTags(self):
        
        with open(self.tags_file) as tags_f:
            self.tags = eval(tags_f.read())
            #pprint.PrettyPrinter(width=1).pprint(self.tags)
            #print()
            if not self.tags:
                raise RuntimeError("Passed tags file: " + self.tags_file + " has no data.")

                        
    
    def _satisfiesOrClauses(self, or_clauses):
        if type(or_clauses) is not list:
            raise RuntimeError("OR clause value type should always be list, but is: " + str(type(or_clauses)))
        satisfies_or_clauses = False
        for or_clause in or_clauses:
            or_option = next(iter(or_clause))  # get the first (and should be only) key in the dict
            if or_option in self.tags:
                if or_clause[or_option] == self.tags[or_option]:
                    satisfies_or_clauses = True
                    break
        if satisfies_or_clauses == False:
            return satisfies_or_clauses
        else:
            return True


    def meetsRequirements(self):
        #print(self.requires)
        #print(self.tags)
        required = self.requires['requires']
        for req in required:
            if req == 'or':
                if not self._satisfiesOrClauses(required[req]):
                    return False

            elif req == 'and':
                and_clauses = required[req]
                for and_clause in and_clauses:
                    if type(and_clause) is not dict:
                        raise RuntimeError("AND clause type should always be dict, but is: " + str(type(and_clause)))
                    clause_key = next(iter(and_clause))  # get the first (and should be only) key in the dict
                    clause_val = and_clause[clause_key]

                    if clause_key == 'or':
                        if not self._satisfiesOrClauses(clause_val):
                            return False
                    else:
                        if type(clause_val) is not dict:
                            raise RuntimeError("AND clause value type should always be dict, but is: " + str(type(clause_val)))

                        clause_sub_key = next(iter(clause_val))
                        if clause_sub_key == 'neq':
                            if clause_key in self.tags:
                                if clause_val['neq'] == self.tags[clause_key]:
                                    return False  # value of the tag equals the value of neq -- fails requirements
                        else:
                            self._raiseNeqError(req)

            elif req in self.tags:
                req_val = required[req]
                if type(req_val) is str:
                    if required[req] != self.tags[req]:
                        return False
                elif type(req_val) is dict:  # This would be a 'sub-clause' like 'vsx': {'neq': 'true'}
                    req_val_key = next(iter(req_val))  # get the first (and should be only) key in the dict
                    if req_val_key == 'neq':
                        if req_val['neq'] == self.tags[req]:
                            return False  # value of the tag equals the value of neq -- fails requirements
                    else:
                        self._raiseNeqError(req)
                else:
                    raise RuntimeError("Unexpected type for requirement value. Requirement: " + str(req) + ". Type of requirement value: " + str(type(self.requires[req])))
            else:  # The reqired key is not in the tags
                req_val = required[req]
                if type(req_val) is dict:  # This would be a 'sub-clause' like 'vsx': {'neq': 'true'}
                    req_val_key = next(iter(req_val))  # get the first (and should be only) key in the dict
                    if req_val_key == 'neq':
                        return True
                    else:
                        self._raiseNeqError(req)
                return False
        return True


    def _raiseNeqError(self, req):
        raise RuntimeError("Unexpected type for requirement value. Requirement: " + str(req) + ". Type of requirement value: " + str(type(self.requires[req])))



if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("\nUsage:\n\n" + os.path.basename(__file__) + " <required_tags_file> <ind_scripts_dir>")
    else:
        tags_file = sys.argv[1]
        yaml_dir = sys.argv[2]
        print("\nProcessing: " + tags_file + " against " + yaml_dir)
        processor = ProcessYaml(tags_file, yaml_dir)

