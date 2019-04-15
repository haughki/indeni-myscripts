import resolve_requires, pytest

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
        'vsx': {'neq': 'true'} }}
    p.tags = { 'vendor': 'checkpoint', 
            'role-firewall': 'true' }

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

def test_and_or_not_meets_one_requires():
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

# File Input Tests
def test_files_basic():
    p = resolve_requires.ProcessYaml()
    p.tags_file = r".\resolverequirestests\files\basic\basic_meets_requires.tags"
    p.ind_dir = r'.\resolverequirestests\files\basic'
    p._getFilesMatchingRequirements()
    assert len(p.scripts) == 1
    assert r".\resolverequirestests\files\basic\basic_meets_requires.ind" == p.scripts[0]

def test_files_one_in_one_out():
    p = resolve_requires.ProcessYaml()
    p.tags_file = r".\resolverequirestests\files\one_in_one_out\one_in_one_out.tags"
    p.ind_dir = r'.\resolverequirestests\files\one_in_one_out'
    p._getFilesMatchingRequirements()
    assert len(p.scripts) == 1
    assert r".\resolverequirestests\files\one_in_one_out\this_one_is_in.ind" == p.scripts[0]

def test_files_no_comments_section():
    p = resolve_requires.ProcessYaml()
    test_dir_path = r".\resolverequirestests\files\no_comments_section"
    p.tags_file = test_dir_path + r"\basic_meets_requires.tags"
    p.ind_dir = test_dir_path
    p._getFilesMatchingRequirements()
    assert len(p.scripts) == 1
    assert test_dir_path + r"\no_comments_section.ind" == p.scripts[0]

def test_and_or_some_in_some_out():
    p = resolve_requires.ProcessYaml()
    test_dir_path = r".\resolverequirestests\files\and_or_some_in_some_out"
    p.tags_file = test_dir_path + r"\and_or_some_in_some_out.tags"
    p.ind_dir = test_dir_path
    p._getFilesMatchingRequirements()
    assert len(p.scripts) == 2
    for s in p.scripts:
        print(s)
    #assert test_dir_path + r"\no_comments_section.ind" == p.scripts[0]

def test_blank_line_eof_error():
    p = resolve_requires.ProcessYaml()
    test_dir_path = r".\resolverequirestests\files\blank_line_eof_error"
    p.tags_file = test_dir_path + r"\basic_meets_requires.tags"
    p.ind_dir = test_dir_path
    p._getFilesMatchingRequirements()
    assert len(p.scripts) == 1
    assert test_dir_path + r".\blank_line_eof_error.ind" == p.scripts[0]

def test_notsure():
    p = resolve_requires.ProcessYaml()
    test_dir_path = r".\resolverequirestests\files\new_test"
    p.tags_file = test_dir_path + r"\super_basic.tags"
    p.ind_dir = test_dir_path
    p._getFilesMatchingRequirements()
    assert len(p.scripts) == 1
    assert test_dir_path + r"\this_test.ind" == p.scripts[0]
