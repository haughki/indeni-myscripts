## resolve_requires.py usage:

It's written in Python 3, and it depends on pyyaml, so you need to:
```
pip3 install pyyaml
```
The script you need is 'resolve_requires.py'. There are a bunch of other scripts in that repo -- just some of my personal Indeni scripts -- you can delete them.

If you are going to modify anything in the script, you will also need to have the 'resolverequriestests' directory, and make sure to run/update the tests accordingly. To run the tests, you will need resolve_requires.py in your sys.path (PYTHONPATH), and it needs to be in a package structure with the tests -- the 'resolve_requires_test.py' file depends on the resolve_requires module.
You will need to pip3 install pyyaml and also pytest. Test cases are pytest. To run tests:
```
Tug:~/projects/indeni/myscripts (master)$ python3 -m pytest
=========================================== test session starts ======================
platform linux -- Python 3.5.2, pytest-4.4.1, py-1.8.0, pluggy-0.11.0
rootdir: /home/hawk/projects/indeni/myscripts
collected 21 items                                                                                         

resolverequirestests/resolve_requires_test.py .....................                                  [100%]

======================================== 21 passed in 0.33 seconds ===================
```
To run the script:
```
Tug:~/projects/indeni/myscripts (master)$ python3 -m resolve_requires ~/tmp/temptags.tags /home/hawk/projects/indeni/indeni-knowledge/parsers/src/checkpoint/firewall

Processing: /home/hawk/tmp/temptags.tags against /home/hawk/projects/indeni/indeni-knowledge/parsers/src/checkpoint/firewall
.../parsers/src/checkpoint/firewall/checkpoint-interrogation/checkpoint-interrogation.ind.yaml
.../parsers/src/checkpoint/firewall/clusterid-md5sum-local-sicname/clusterid-md5sum-local-sicname.ind.yaml
...
.../parsers/src/checkpoint/firewall/vsx-stat-monitoring/vsx-stat-monitoring.ind.yaml
```
Like I said: it needs thorough testing against the actual checkpoint script directories -- there definitely could be some bugs. If you find a bug, you can tell me and I'll fix, or you can create a new unit test for it, and fix yourself. Let me know if you want to push something, and I can give you access to the repo.
