import pprint, sys, re, os
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

class ProcessYaml:
    def __init__(self, tags_file='', ind_dir=''):
        self.requires = {}
        self.requires_str = ""
        self.tags = {}
        
        if ind_dir:
            for dirpath, dirs, files in os.walk(ind_dir):	
                for filename in files:
                    #print(filename)
                    if filename.endswith('.ind'):
                        fname = os.path.join(dirpath,filename)
                        print('-' * 80)
                        print(fname)
                        
                        file_str = ""
                        with open(fname) as f:
                            line = f.readline().strip()
                            #print(line)
                            while line != "#! META":
                                line = f.readline().rstrip()

                            #print("here")
                            while True:
                                line = f.readline().rstrip()
                                if not line:  # EOF
                                    break
                                if line.startswith('#! '):  # next section -- might not be #! COMMENTS, so we break on anything
                                    break
                                line = re.sub(r':\s*true', r': "true"', line)
                                file_str = file_str + line +'\n'

                        self.requires = load(file_str, Loader=Loader)
                        self.requires_str = dump(self.requires, Dumper=Dumper)

                        pp = pprint.PrettyPrinter(width=1)
                        pp.pprint(self.requires)
    
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
        print(self.requires)
        print(self.tags)
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
    if len(sys.argv) < 2:
        print("Need input file as first param.")
    else:
        ind_dir = sys.argv[1]
        processor = ProcessYaml(ind_dir=ind_dir)

