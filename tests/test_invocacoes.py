"""D15 (24/11): pesos por tipo de invocação."""
from dh import invocacoes


def _b():
    lobos = {'nome': 'Conjure Animals (8 lobos)', 'quantidade': 8, 'pv': 11, 'ca': 13}
    thralls = {'nome': 'esqueletos (Undead Thralls)', 'quantidade': 4, 'pv': 15, 'ca': 13}
    aberr = {'nome': 'Summon Aberration (4º)', 'quantidade': 1, 'pv': 40, 'ca': 15}
    return {'linhas': [
        {'id': 'principal', 'principal': True, 'invocacoes': [dict(thralls)]},
        {'id': 'conjurar', 'invocacoes': [dict(lobos)]},
        {'id': 'controle', 'invocacoes': [dict(thralls)]},
        {'id': 'summon', 'invocacoes': [dict(aberr)]},
        {'id': 'drake', 'invocacoes': [{'nome': 'Drake Companion', 'quantidade': 1, 'pv': 30, 'ca': 16}]},
    ]}


def test_tipos():
    assert invocacoes.tipo({'nome': 'Conjure Animals (8 lobos)'}) == 'numerosa'
    assert invocacoes.tipo({'nome': 'Summon Beast (Land, 4º)'}) == 'summon'
    assert invocacoes.tipo({'nome': 'Drake Companion'}) == 'companheiro'
    assert invocacoes.tipo({'nome': 'Conjure Animals', 'tipo': 'summon'}) == 'summon'   # campo explícito vence


def test_peso_zero_tira_numerosa(monkeypatch):
    from dh import premissas   # 26/11: com o corpo também em 0 (o padrão agora é 0,5 no corpo)
    orig = premissas.P
    monkeypatch.setattr(premissas, 'P', lambda n, padrao=None: 0.0 if n == 'invocacao.peso_corpo.numerosa' else orig(n, padrao))
    b = invocacoes.aplicar(_b()); L = {l['id']: l for l in b['linhas']}
    assert L['conjurar'].get('plano') is False and L['conjurar'].get('aneis') is False and 'invocacoes' not in L['conjurar']
    # criatura persistente (também na principal): só sai a criatura, a linha fica
    assert 'invocacoes' not in L['principal'] and L['principal'].get('plano', True) is not False
    assert 'invocacoes' not in L['controle'] and L['controle'].get('plano', True) is not False
    assert L['summon']['invocacoes'][0]['quantidade'] == 1 and L['drake']['invocacoes']


def test_peso_fracionario(monkeypatch):
    from dh import premissas
    orig = premissas.P
    monkeypatch.setattr(premissas, 'P', lambda n, padrao=None: 0.5 if n == 'invocacao.peso.numerosa' else orig(n, padrao))
    b = invocacoes.aplicar(_b()); L = {l['id']: l for l in b['linhas']}
    assert L['conjurar']['invocacoes'][0]['quantidade'] == 4


def test_peso_corpo_separado_do_dano():
    """26/11: numerosa com dano 0 e corpo 0,5 fica na linha com metade da quantidade e sem dano."""
    from dh import invocacoes
    from dh.dano import dpr
    b = {'linhas': [{'id': 'principal', 'principal': True, 'dano': {'ataques': []},
                     'invocacoes': [{'nome': 'esqueletos (Animate Dead)', 'quantidade': 4, 'pv': 20, 'ca': 13,
                                     'ataque': {'bonus': 4, 'dano': '1d6+2'}}]}],
         'pesos_invocacao': None}
    b.pop('pesos_invocacao')
    invocacoes.aplicar(b)
    inv = b['linhas'][0]['invocacoes'][0]
    assert inv['quantidade'] == 2 and inv['peso_dano'] == 0
    assert dpr({'ataques': []}, 15, invocacoes=[inv]) == 0
    b2 = {'pesos_invocacao': {'numerosa': 1.0}, 'linhas': [{'id': 'p', 'principal': True, 'invocacoes': [
        {'nome': 'Conjure Animals', 'quantidade': 8, 'pv': 13, 'ca': 11}]}]}
    invocacoes.aplicar(b2)
    assert b2['linhas'][0]['invocacoes'][0]['quantidade'] == 8 and 'peso_dano' not in b2['linhas'][0]['invocacoes'][0]
