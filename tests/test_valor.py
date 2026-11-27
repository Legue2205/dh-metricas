"""P3 v0 (27/11): o valor do dia soma o DE da linha de cada luta do plano, com o peso da luta."""
from dh import moeda, valor as V


def test_valor_soma_as_lutas(monkeypatch):
    tab = {'a': 10.0, 'b': 4.0}
    monkeypatch.setattr(moeda, 'de_linha', lambda x, nv: dict(dano=tab[x['k']], suporte=0.0, controle=0.0, area=0.0, total=tab[x['k']]))
    res = {'id': 'x', 'nivel': 7, 'linhas': {'a': {'k': 'a'}, 'b': {'k': 'b'}},
           'planos': {'padrao': {'combates': [{'linha': 'a', 'peso': 1}, {'linha': 'b', 'peso': 2}]}}}
    v = V.valor(res)
    assert v['dia'] == 18.0 and v['parcelas']['dano'] == 18.0 and v['luta_unica'] == 10.0
