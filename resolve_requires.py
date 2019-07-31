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

import pprint, sys, re, os, warnings#, traceback
from yaml import load, dump, scanner
from pathlib import Path
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

class ProcessYaml:
    def __init__(self, tags_file='', yaml_dir='', search=False):
        self.tags_file = tags_file
        self.yaml_dir = yaml_dir
        self.search = search
        self.requires = None
        self.tags = None
        self.scripts = []

        if self.yaml_dir and self.tags_file:
            self.tags_file = Path(self.tags_file)
            self.yaml_dir = Path(self.yaml_dir)
            self._getFilesMatchingRequirements()
            for script in self.scripts:
                print(script)

    def _getFilesMatchingRequirements(self):
        self._setTags()
        
        # Walk the passed directory to search for .ind files to process
        for dirpath, dirs, files in os.walk(str(self.yaml_dir)):
            for filename in files:
                if filename.endswith('.ind.yaml'):
                    fname = Path(dirpath) / filename
 #                   print('-' * 80)
 #                   print(fname)
                    
                    file_str = ""
                    with open(str(fname)) as f:
                        for line in f:
                            # If true or false don't have quotes, the YAML parser converts them to Python True and False.
                            # Not what we want.
                            line = re.sub(r':\s*true', r': "true"', line)
                            line = re.sub(r':\s*false', r': "false"', line)
                            file_str = file_str + line

                    #print(fname)
                    #print("file_str: " + file_str)
                    try:
                        self.requires = load(file_str, Loader=Loader)
                    except scanner.ScannerError:
                        print("WARNING: could not load .yaml file: " + str(fname) + ". Maybe YAML is not well-formed.")

                    #pprint.PrettyPrinter(width=1).pprint(self.requires)
                    #self.requires_str = dump(meta_dict, Dumper=Dumper)
                    if self.search:
                        if 'requires' in self.requires:
                                if self.scriptRequiresTag():
                                    self.scripts.append(fname)
                        else:
                            print("INTERROGATION: " + str(fname))
                    else:
                        if 'requires' in self.requires:
                                if self.meetsRequirements():
                                    self.scripts.append(fname)
                        else:
                            print("INFO: " + str(fname) + " looks like an interrogation script which can run against " \
                                    "any device for all vendors. It may or may not be relevant to your device.")
                        
        
        self.scripts.sort()

    def scriptRequiresTag(self):
#        print(self.requires)
#        print(self.tags)
        required = self.requires['requires']
        for find_key,find_val in self.tags.items():
            if self._foundTagInRequired(find_key, find_val, required):
                return True
        return False


    def _foundTagInRequired(self, find_key, find_val, required):
        if type(required) is not dict:
            raise RuntimeError("Search: required search type should always be dict, but is: " + str(type(required)))
        for req in required:
            req_val = required[req]
            if type(req_val) is str: 
                if req == find_key and req_val == find_val:
                    return True
            elif type(req_val) is dict:
                if self._foundTagInRequired(find_key, find_val, req_val):
                    return True
            elif type(req_val) is list:
                for list_req in req_val:
                    if type(list_req) is dict:
                        if self._foundTagInRequired(find_key, find_val, list_req):
                            return True
                    else:
                        raise RuntimeError("Search: required list item type should always be dict, but is: " + str(type(list_req)))
            else:
                raise RuntimeError("Search: unexpected required value type: " + str(type(req_val)))
        return False # no match in this dict

    def _setTags(self):
        with open(str(self.tags_file)) as tags_f:
            self.tags = eval(tags_f.read())
            #pprint.PrettyPrinter(width=1).pprint(self.tags)
            #print()
            if not self.tags:
                raise RuntimeError("Passed tags file: " + str(self.tags_file) + " has no data.")


    def _satisfiesOrClauses(self, or_clauses):
        if type(or_clauses) is not list:
            raise RuntimeError("OR clause value type should always be list, but is: " + str(type(or_clauses)))
        satisfies_or_clauses = False
        for or_clause in or_clauses:
            or_option = next(iter(or_clause))  # get the first (and should be only) key in the dict
            if self._requirementIsMet(or_clause, or_option):
                satisfies_or_clauses = True
                break
        return satisfies_or_clauses


    def meetsRequirements(self):
#        print(self.requires)
#        print(self.tags)
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
                        if not self._requirementIsMet(and_clause, clause_key):
                            return False
            else:
                if not self._requirementIsMet(required, req):
                    return False

        return True


    def _raiseUnexpectedReqType(self, required, req):
        raise RuntimeError("Unexpected type for requirement value. Requirement: " + str(req) + ". Type of requirement value: " + str(type(required[req])))

    def _requirementIsMet(self, required, req):
        if req in self.tags:
            req_val = required[req]
            if type(req_val) is str:
                if required[req] != self.tags[req]:
                    return False
            elif type(req_val) is dict:  # This would be a 'sub-clause' like 'vsx': {'neq': 'true'}
                req_val_key = next(iter(req_val))  # get the first (and should be only) key in the dict
                if req_val_key == 'neq':
                    if req_val['neq'] == self.tags[req]:
                        return False  # value of the tag equals the value of neq -- fails requirements
                elif req_val_key == 'eq':
                    if req_val['eq'] != self.tags[req]:
                        return False  # value of the tag does not equal value of eq -- fails requirements
                elif req_val_key == 'exists':
                    req_val_val = req_val['exists']
                    if req_val_val == 'true' and req not in self.tags:
                        return False
                    if req_val_val == 'false' and req in self.tags:
                        return False
                else:
                    self._raiseUnexpectedReqType(required, req)
            else:
                self._raiseUnexpectedReqType(required, req)
        else:  # The reqired key is not in the tags
            req_val = required[req]
 #           print("req: " + str(req))
 #           print("req_val type: " + str(type(req_val)))
            if type(req_val) is dict:  # This would be a 'sub-clause' like 'vsx': {'neq': 'true'}
                req_val_key = next(iter(req_val))  # get the first (and should be only) key in the dict
                # Example: vsx is required to not be true. The vsx key doesn't even exist in the tags:
                # maybe it's just a regular firewall. In any case, if the vsx key doesn't exist,
                # it definitely can't equal 'true' (or any thing else) so it meets the requirements by default.
                if req_val_key == 'neq':
                    return True
                elif req_val_key == 'eq':  # No tag for this, so implicitly false
                    return False
                elif req_val_key == 'exists':
                    if req_val['exists'] == 'true':  # Requires the tag to exist, but it doesn't
                        return False
                    if req_val['exists'] == 'false':  # Requires the tag _not_ to exist, and it doesn't
                        return True
                
                else:
                    self._raiseUnexpectedReqType(required, req)
                    
                    
            return False
        return True # Couldn't say for sure if all the requirements are met -- need to look at the rest of the requirements

def printUsage():
    print("\nUsage:\n\n" + os.path.basename(__file__) + " [-s|--search] <required_tags_file> <ind_scripts_dir>")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        printUsage()
    elif len(sys.argv) == 3:
        tags_file = sys.argv[1]
        yaml_dir = sys.argv[2]
        print("\nProcessing: " + tags_file + " against " + yaml_dir)
        processor = ProcessYaml(tags_file, yaml_dir)
    elif (len(sys.argv) == 4):
        option = sys.argv[1]
        if (option == "-s") or (option == "--search"):
            tags_file = sys.argv[2]
            yaml_dir = sys.argv[3]
            print("\nSearching for: " + tags_file + " in " + yaml_dir)
            processor = ProcessYaml(tags_file, yaml_dir, True)
    else:
        printUsage()
