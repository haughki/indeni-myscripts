import pprint, sys, re, os, warnings
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

class ProcessYaml:
    def __init__(self, tags_file='', ind_dir=''):
        self.requires = None
        self.tags = None
        
        if ind_dir and tags_file:
                
            pp = pprint.PrettyPrinter(width=1)
            with open(tags_file) as tags_f:
                self.tags = eval(tags_f.read())
                pp.pprint(self.tags)
                print()
                if not self.tags:
                    raise RuntimeError("Passed tags file: " + tags_file + " has no data.")
            

            for dirpath, dirs, files in os.walk(ind_dir):
                for filename in files:
                    if filename.endswith('.ind'):
                        fname = os.path.join(dirpath,filename)
                        print('-' * 80)
                        print(fname)
                        
                        file_str = ""
                        with open(fname) as f:
                            # We only want to read the META section of the file. The META section is delimited by a 
                            # some following section which starts with '#! " -- it could really be anything. So, instead 
                            # of doing a simple file read, we have to jump through some hoops.
                            line = f.readline().strip()
                            while line != "#! META":
                                line = f.readline().rstrip()

                            while True:
                                line = f.readline().rstrip()
                                if not line:  # EOF
                                    break
                                if re.match(r'^\s*#! ', line):  # next section -- might not be #! COMMENTS, so we break on anything
                                    break
                                # If true or false don't have quotes, the YAML parser converts them to Python True and False.
                                # Not what we want.
                                line = re.sub(r':\s*true', r': "true"', line)
                                line = re.sub(r':\s*false', r': "false"', line)
                                file_str = file_str + line +'\n'

                        self.requires = load(file_str, Loader=Loader)
                        pp.pprint(self.requires)
                        #self.requires_str = dump(meta_dict, Dumper=Dumper)
                        if 'requires' in self.requires:
                             if self.meetsRequirements():
                                 print("*" * 20)
                                 print(fname)
                        else:
                            warnings.warn('No requires section in this .ind script: ' + fname)

                        
                        
    
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
    ind_dir = ""
    if len(sys.argv) < 3:
        print("\nUsage:\n\n" + os.path.basename(__file__) + " <required_tags_file> <ind_scripts_dir>")
    else:
        tags_file = sys.argv[1]
        ind_dir = sys.argv[2]
        print("\nProcessing: " + tags_file + " against " + ind_dir)
        processor = ProcessYaml(tags_file, ind_dir)

