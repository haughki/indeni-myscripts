## resolve_requires.py usage:

This script tries to determine, for a given set of device tags, which scripts Indeni would run, given a directory of Indeni .ind.yaml scripts. More simply: which scripts indeni would run against a given device.

It's written in Python 3, and it depends on pyyaml, so you need to:
```
pip3 install pyyaml
```
The script you need is 'resolve_requires.py'. There are a bunch of other scripts in that repo -- just some of my personal Indeni scripts -- you can delete them.

If you are going to modify anything in the script, you will also need to have the 'resolverequriestests' directory, and make sure to run/update the tests accordingly. To run the tests, you will need resolve_requires.py in your sys.path (PYTHONPATH), and it needs to be in a package structure with the tests -- the 'resolve_requires_test.py' file depends on the resolve_requires module.
You will need to `pip3 install pyyaml` and also `pip3 install pytest`. Test cases are pytest.

### To Run Tests
```
Windows:   D:\projects\indeni\myscripts>py -3 pytest
Linux:     Tug:~/projects/indeni/myscripts (master)$ python3 -m pytest
=========================================== test session starts ======================
platform linux -- Python 3.5.2, pytest-4.4.1, py-1.8.0, pluggy-0.11.0
rootdir: /home/hawk/projects/indeni/myscripts
collected 21 items                                                                                         

resolverequirestests/resolve_requires_test.py .....................                                  [100%]

======================================== 21 passed in 0.33 seconds ===================
```
### To Run the Script
The script requires two commandline args: the path to a file with some tags in it (see example below) and a directory with some `*.ind.yaml` files in it. The script will print a list of the scripts in the directory (and sub-directories) that Indeni would run, based on the tags file.

Linux:
```
Tug:~/projects/indeni/myscripts (master)$ python3 -m resolve_requires ~/tmp/temptags.tags /home/hawk/projects/indeni/indeni-knowledge/parsers/src/checkpoint/firewall

Processing: /home/hawk/tmp/temptags.tags against /home/hawk/projects/indeni/indeni-knowledge/parsers/src/checkpoint/firewall
.../parsers/src/checkpoint/firewall/checkpoint-interrogation/checkpoint-interrogation.ind.yaml
.../parsers/src/checkpoint/firewall/clusterid-md5sum-local-sicname/clusterid-md5sum-local-sicname.ind.yaml
...
```

Windows:
```
D:\projects\indeni\myscripts>py -3 -m resolve_requires some_input_tags.txt D:\projects\indeni\indeni-knowledge\parsers\src\checkpoint\firewall

Processing: some_input_tags.txt against D:\projects\indeni\indeni-knowledge\parsers\src\checkpoint\firewall
...parsers\src\checkpoint\firewall\checkpoint-interrogation\checkpoint-interrogation.ind.yaml
...parsers\src\checkpoint\firewall\clusterid-md5sum-local-sicname\clusterid-md5sum-local-sicname.ind.yaml
...
```
Here is an example of a tags input file. *It should be formatted exactly this way:*
```
{
    "cluster-id": "d54ac2b34461876261a53d2b00131744",
    "clusterxl": "true",
    "device-id": "01c6c1a5-8373-459c-82de-3935e0f523a3",
    "device-ip": "10.11.94.49",
    "device-name": "CP-R80.20-GW8-1",
    "high-availability": "true",
    "hostname": "CP-R80.20-GW8-1",
    "https": "true",
    "linux-based": "true",
    "model": "VMware Virtual Platform",
    "nice-path": "/bin/nice",
    "os.name": "gaia",
    "os.version": "R80.20",
    "role-firewall": "true",
    "routing-bgp": "true",
    "ssh": "true",
    "vendor": "checkpoint"
}
```
Like I said: it needs thorough testing against the actual checkpoint script directories -- there definitely could be some bugs. If you find a bug, you can tell me and I'll fix, or you can create a new unit test for it and fix yourself. Let me know if you want to push something, and I can give you access to the repo.
