import pprint
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

class ProcessYaml:
    def __init__(self, input_file=''):
        if input_file:
            f = open(input_file, 'r')
            self.requires = load(f, Loader=Loader)
            self.requires_str = dump(self.requires, Dumper=Dumper)
            pp = pprint.PrettyPrinter(width=1)
            pp.pprint(self.requires)
            #print(self.requires_str)
            self.tags = {}
    
    def meetsRequirements(self):
        print(self.requires)
        print(self.tags)
        required = self.requires['requires']
        for req in required:
            if req == 'or':
                or_clauses = required[req]
                satisfies_or_clauses = False
                for or_clause in or_clauses:
                    for or_option in or_clause:
                        if or_option in self.tags:
                            if or_clause[or_option] == self.tags[or_option]:
                                satisfies_or_clauses = True
                                break
                    if satisfies_or_clauses == True:
                        break

                if satisfies_or_clauses == False:
                    return satisfies_or_clauses
            elif req == 'and':
                and_clauses = required[req]
                for and_clause in and_clauses:
                    if type(and_clause) is not dict:
                        raise RuntimeError("And clause type should always be dict, but is: " + str(type(and_clause)))
                    clause_key = next(iter(and_clause))  # get the first (and should be only) key in the dict
                    clause_val = and_clause[clause_key]
                    if type(clause_val) is not dict:
                        raise RuntimeError("And clause value type should always be dict, but is: " + str(type(clause_val)))

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
    processor = ProcessYaml('yaml_input.yaml')

