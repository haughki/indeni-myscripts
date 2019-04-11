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

def test_or_not_meets_requires():
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