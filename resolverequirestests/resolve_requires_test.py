import resolve_requires, pytest
from pathlib import Path

def test_basic_meets_requires():
    p = resolve_requires.ProcessYaml()
    p.requires = {'requires': {
        'vendor': 'checkpoint', 
        'os.name': 'gaia'
        }}
    p.tags = { 'vendor': 'checkpoint', 
            'os.name': 'gaia' }

    assert p.meetsRequirements() == True

def test_more_tags_meets_requires():
    p = resolve_requires.ProcessYaml()
    p.requires = {'requires': {
        'vendor': 'checkpoint', 
        'os.name': 'gaia'
        }}
    p.tags = { 'vendor': 'checkpoint', 
            'os.name': 'gaia',
            'hostname': 'CP-R80.20-GW8-1'}

    assert p.meetsRequirements() == True

def test_not_meets_requires():
    p = resolve_requires.ProcessYaml()
    p.requires = {'requires': {
        'vendor': 'checkpoint', 
        'os.name': 'gaia',
        'role-firewall': 'true'
        }}
    p.tags = { 'vendor': 'checkpoint', 
            'os.name': 'gaia' }

    assert p.meetsRequirements() == False

def test_or_meets_requires():
    p = resolve_requires.ProcessYaml()
    p.requires = {'requires': {
        'vendor': 'checkpoint',
        'or': [{'os.name': 'gaia'},
            {'os.name': 'ipso'},
            {'role-firewall': 'true'}] }}
    p.tags = { 'vendor': 'checkpoint', 
            'os.name': 'gaia' }

    assert p.meetsRequirements() == True

def test_or_not_meets_requires_explicit():
    p = resolve_requires.ProcessYaml()
    p.requires = {'requires': {
        'vendor': 'checkpoint',
        'role-management': 'true',
        'or': [{'os.name': 'gaia'},
            {'os.name': 'ipso'},
            {'role-firewall': 'true'}] }}
    p.tags = { 'vendor': 'checkpoint', 
            'role-management': 'true',
            'os.name': 'secureplatform' }

    assert p.meetsRequirements() == False

def test_or_not_meets_requires():
    p = resolve_requires.ProcessYaml()
    p.requires = {'requires': {
        'vendor': 'checkpoint',
        'role-management': 'true',
        'or': [{'os.name': 'gaia'},
            {'os.name': 'ipso'},
            {'role-firewall': 'true'}] }}
    p.tags = { 'vendor': 'checkpoint', 
            'role-management': 'true'}

    assert p.meetsRequirements() == False


def test_neq_meets_requires():
    p = resolve_requires.ProcessYaml()
    p.requires = {'requires': {
        'vendor': 'checkpoint',
        'role-firewall': 'true',
        'vsx': {'neq': 'true'} },
        }
    p.tags = { 'vendor': 'checkpoint', 
            'role-firewall': 'true' }

    assert p.meetsRequirements() == True

def test_neq_not_meets_requires_order_matters():
    p = resolve_requires.ProcessYaml()
    p.requires = {'requires': {
        'vendor': 'checkpoint',
        'vsx': {'neq': 'true'},
        'role-firewall': 'true' }}
    p.tags = { 'vendor': 'checkpoint', 
            'role-firewall': 'true',
            'mds': 'true' }

    assert p.meetsRequirements() == True

def test_neq_meets_requires_explicit():
    p = resolve_requires.ProcessYaml()
    p.requires = {'requires': {
        'vendor': 'checkpoint',
        'role-firewall': 'true',
        'vsx': {'neq': 'true'} }}
    p.tags = { 'vendor': 'checkpoint', 
            'role-firewall': 'true',
            'vsx': 'false' }

    assert p.meetsRequirements() == True

def test_neq_not_meets_requires():
    p = resolve_requires.ProcessYaml()
    p.requires = {'requires': {
        'vendor': 'checkpoint',
        'role-firewall': 'true',
        'vsx': {'neq': 'true'} }}
    p.tags = { 'vendor': 'checkpoint', 
               'role-firewall': 'true',
               'vsx': 'true' }

    assert p.meetsRequirements() == False

def test_and_neq_meets_requires_explicit():
    p = resolve_requires.ProcessYaml()
    p.requires = {'requires': {
        'and': [{'os.version': {'neq': 'R80.10'}},
                {'os.version': {'neq': 'R80.20'}}],
        'vendor': 'checkpoint'}}
    p.tags = {
        'vendor': 'checkpoint', 
        'os.version': 'R77.30' }

    assert p.meetsRequirements() == True

def test_and_neq_meets_requires():
    p = resolve_requires.ProcessYaml()
    p.requires = {'requires': {
        'and': [{'os.version': {'neq': 'R80.10'}},
                {'os.version': {'neq': 'R80.20'}}],
        'vendor': 'checkpoint',
        'role-firewall': 'true' }}
    p.tags = {
        'vendor': 'checkpoint', 
        'role-firewall': 'true' }

    assert p.meetsRequirements() == True

def test_and_neq_not_meets_requires_explicit():
    p = resolve_requires.ProcessYaml()
    p.requires = {'requires': {
        'and': [{'os.version': {'neq': 'R80.10'}},
                {'os.version': {'neq': 'R80.20'}}],
        'vendor': 'checkpoint'}}
    p.tags = {
        'vendor': 'checkpoint', 
        'os.version': 'R80.10' }

    assert p.meetsRequirements() == False

def test_and_or_meets_requires_explicit():
    p = resolve_requires.ProcessYaml()
    p.requires = {'requires': {
        'and': [
            { 'or': [{'os.name': 'gaia'},
                    {'os.name': 'secureplatform'}]
            },
            { 'or': [{'os.version': 'R80.10'},
                    {'os.version': 'R80.20'}]}
        ],
        'vendor': 'checkpoint'}}

    p.tags = {
        'vendor': 'checkpoint', 
        'os.name': 'secureplatform',
        'os.version': 'R80.10' }

    assert p.meetsRequirements() == True

def test_and_or_meets_only_one_requires():
    p = resolve_requires.ProcessYaml()
    p.requires = {'requires': {
        'and': [
            { 'or': [{'os.name': 'gaia'},
                    {'os.name': 'secureplatform'}]
            },
            { 'or': [{'os.version': 'R80.10'},
                    {'os.version': 'R80.20'}]}
        ],
        'vendor': 'checkpoint'}}

    p.tags = {
        'vendor': 'checkpoint', 
        'os.name': 'secureplatform' }

    assert p.meetsRequirements() == False

def test_and_or_does_not_meet_one_requires():
    p = resolve_requires.ProcessYaml()
    p.requires = {'requires': {
        'and': [
            { 'or': [{'os.name': 'gaia'},
                    {'os.name': 'secureplatform'}]
            },
            { 'or': [{'os.version': 'R80.10'},
                    {'os.version': 'R80.20'}]}
        ],
        'vendor': 'checkpoint'}}

    p.tags = {
        'vendor': 'checkpoint', 
        'os.name': 'secureplatform',
        'os.version': 'R77.30' }

    assert p.meetsRequirements() == False

# This is a convoluted set of requirements: there's no need for the 'and' clause here -- it is implied. But, I found
# it in a script, so I'm going to test for it.
def test_and_or_neq_meets_requires():
    p = resolve_requires.ProcessYaml()
    p.requires = {'requires': {
        'and': [
            {'os.name': 'ipso'},
            { 'or': [
                {'vsx': {'neq': 'true'} },
                {'mds': 'true'}]}
        ],
        'vendor': 'checkpoint'}}

    p.tags = {
        'vendor': 'checkpoint', 
        'os.name': 'ipso',
        'os.version': 'R77.30',
        'vsx': 'true' }

    assert p.meetsRequirements() == False

# This is a convoluted set of requirements: there's no need for the 'and' clause here -- it is implied. But, I found
# it in a script, so I'm going to test for it.
def test_and_or_neq_meets_requires_special():
    p = resolve_requires.ProcessYaml()
    p.requires = {'requires': {
        'and': [
            {'os.name': 'ipso'},
            { 'or': [
                {'vsx': {'neq': 'true'} },
                {'mds': 'true'}]}
        ],
        'vendor': 'checkpoint'}}

    p.tags = {
        'vendor': 'checkpoint', 
        'os.name': 'ipso',
        'os.version': 'R77.30',
        'mds': 'true' }

    assert p.meetsRequirements() == True

# I'm pretty sure this 'eq' switch is unnecessary -- maybe even a bug. But, I found
# it in a script, so I'm going to test for it.
def test_eq_meets_requires():
    p = resolve_requires.ProcessYaml()
    p.requires = {'requires': {
        'or': [
                {'os.version': {'eq': 'R80.10'} },
                {'os.version': {'eq': 'R80.20'} }
        ],
        'vendor': 'checkpoint',
        'role-firewall': 'true',
        'os.name': {'neq': 'gaia'} }
        }

    p.tags = {
        'vendor': 'checkpoint', 
        'os.name': 'ipso',
        'os.version': 'R80.10',
        'role-firewall': 'true' }

    assert p.meetsRequirements() == True



# Following tests run against actual .yaml files -- 'full file' tests
test_files_base = Path("./resolverequirestests/files")
def test_files_basic():
    p = resolve_requires.ProcessYaml()
    p.tags_file = test_files_base / "basic/basic_meets_requires.tags"
    p.yaml_dir = test_files_base / "basic"
    p._getFilesMatchingRequirements()
    assert len(p.scripts) == 1
    assert test_files_base / "basic/basic_meets_requires.ind.yaml" == p.scripts[0]

def test_files_one_in_one_out():
    p = resolve_requires.ProcessYaml()
    p.tags_file = test_files_base / "one_in_one_out/one_in_one_out.tags"
    p.yaml_dir = test_files_base / "one_in_one_out"
    p._getFilesMatchingRequirements()
    assert len(p.scripts) == 1
    assert test_files_base / "one_in_one_out/this_one_is_in.ind.yaml" == p.scripts[0]

def test_files_no_comments_section():
    p = resolve_requires.ProcessYaml()
    test_files_path = test_files_base / "no_comments_section"
    p.tags_file = test_files_path / "basic_meets_requires.tags"
    p.yaml_dir = test_files_path
    p._getFilesMatchingRequirements()
    assert len(p.scripts) == 1
    assert test_files_path / "no_comments_section.ind.yaml" == p.scripts[0]

def test_and_or_some_in_some_out():
    p = resolve_requires.ProcessYaml()
    test_files_path = test_files_base / "and_or_some_in_some_out"
    p.tags_file = test_files_path / "and_or_some_in_some_out.tags"
    p.yaml_dir = test_files_path
    p._getFilesMatchingRequirements()
    assert len(p.scripts) == 2
    found_expected_2 = False
    found_expected_1 = False
    for s in p.scripts:
        if s == test_files_path / "and_or_in.ind.yaml":
            found_expected_1 = True
        if s == test_files_path / "neq_in.ind.yaml":
            found_expected_2 = True
    assert found_expected_1 == True
    assert found_expected_2 == True


def test_blank_line_eof_error():
    p = resolve_requires.ProcessYaml()
    test_files_path = test_files_base / "blank_line_eof_error"
    p.tags_file = test_files_path / "basic_meets_requires.tags"
    p.yaml_dir = test_files_path
    p._getFilesMatchingRequirements()
    assert len(p.scripts) == 1
    assert test_files_path / "blank_line_eof_error.ind.yaml" == p.scripts[0]

def test_this_tag_disables_this_script():
    p = resolve_requires.ProcessYaml()
    test_files_path = test_files_base / "this_tag_disables_this_script"
    p.tags_file = test_files_path / "super_basic.tags"
    p.yaml_dir = test_files_path
    p._getFilesMatchingRequirements()
    assert len(p.scripts) == 0
