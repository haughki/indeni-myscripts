from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

class ProcessYaml:
    def __init__(self, input_file=""):
        if input_file:
            f = open(input_file, "r")
            self.requires = load(f, Loader=Loader)
            self.requires_str = dump(self.requires, Dumper=Dumper)
            print(self.requires)
            print(self.requires_str)
            self.tags = {}
    
    def requiresCompare(self):
        print(self.requires)
        print(self.tags)
        required = self.requires['requires']
        meets_requirements = True
        for req in required:
            if req in self.tags:
                if required[req] != self.tags[req]:
                    meets_requirements = False
                    break
            else:
                meets_requirements = False
                break
        print(meets_requirements)
        # for each required key
            # if key is in tags
                # if tag key value doesn't equal required key value
                    # will run = false
                    # break
            # else
                # will run = false
                # break


def test_basic_meets_requires():
    p = ProcessYaml()
    p.requires = {'requires': {'os.name': 'gaia'}}
    p.tags = { 'os.name': 'gaia'}
    p.requiresCompare()

if __name__ == "__main__":
    processor = ProcessYaml("yaml_input.yaml")

