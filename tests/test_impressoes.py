"""Invalidação por eixo (19/11, tarefa 3): só recalcula o eixo cuja impressão digital mudou, e o que é reaproveitado é
idêntico a um recálculo completo."""
import json
import shutil
from pathlib import Path

import pytest

from dh import impressoes as I
from dh import motor

B = Path(__file__).resolve().parents[1] / 'builds'
BUILDS = ['kael-7', 'tinbin-7', 'amadeus-7']     # todos os eixos; motor tático; área com magias


@pytest.fixture(scope='module')
def base(tmp_path_factory):
    """Recálculo completo (do zero) das 3 builds, uma vez: é a referência dos testes."""
    d = tmp_path_factory.mktemp('base'); mp = pytest.MonkeyPatch()
    mp.setattr(motor, 'RESULTADOS', d); I.SOBRESCREVER.clear(); I.limpar()
    res = {bid: motor.avaliar(B / f'{bid}.json', 'rapido')[1] for bid in BUILDS}
    mp.undo()
    return d, res


@pytest.fixture
def tmp_res(tmp_path, monkeypatch, base):
    d = tmp_path / 'resultados'; shutil.copytree(base[0], d)
    monkeypatch.setattr(motor, 'RESULTADOS', d)
    monkeypatch.setattr(I, 'SOBRESCREVER', {})
    I.limpar()
    yield d
    I.limpar()


def _limpo(res):
    fora = ('segundos', 'impressoes', '_cache', '_recalculados')
    return json.loads(json.dumps({k: v for k, v in res.items() if k not in fora}))


def _mexe(rel):
    I.SOBRESCREVER[rel] = 'mexido'; I.limpar()


def _calculados(res):
    return {lid: sorted(set(es)) for lid, es in res.get('_recalculados', {}).items() if es}


@pytest.mark.parametrize('bid', BUILDS)
def test_sem_mudanca_nada_recalcula(tmp_res, base, bid):
    assert _calculados(base[1][bid])            # a referência calculou de verdade
    _, r = motor.avaliar(B / f'{bid}.json', 'rapido')
    assert r.get('_cache') is True


@pytest.mark.parametrize('bid', BUILDS)
def test_horda_so_recalcula_area_e_bate_com_recalculo_completo(tmp_res, base, bid):
    _mexe('horda.py')
    _, r = motor.avaliar(B / f'{bid}.json', 'rapido')
    assert not r.get('_cache')
    calc = _calculados(r)
    assert calc and all(es == ['area'] for es in calc.values()), calc
    assert _limpo(r) == _limpo(base[1][bid])     # reaproveitado + recalculado = recálculo do zero
    _, r2 = motor.avaliar(B / f'{bid}.json', 'rapido')
    assert r2.get('_cache') is True


def test_tatico_leve_bate_com_recalculo_completo(tmp_res, base):
    """Só a defesa muda: o motor tático não roda (expansão leve) e o orçamento sai igual."""
    _mexe('defesa.py')
    _, r = motor.avaliar(B / 'tinbin-7.json', 'rapido')
    assert {e for es in _calculados(r).values() for e in es} == {'defesa'}
    assert _limpo(r) == _limpo(base[1]['tinbin-7'])


def test_dependencias_por_eixo(tmp_res):
    assert 'horda.py' in I.arquivos('area') and 'dano.py' in I.arquivos('area')
    assert 'horda.py' not in I.arquivos('dano') and 'horda.py' not in I.arquivos('controle')
    assert 'controle/magias.json' in I.arquivos('controle')
    assert 'premissas.py' not in I.arquivos('dano') and 'eixos.py' in I.arquivos('suporte')
    _mexe('dano.py')
    _, r = motor.avaliar(B / 'kael-7.json', 'rapido')
    assert {e for es in _calculados(r).values() for e in es} == {'dano', 'area'}
    _mexe('controle/campo.py')
    _, r = motor.avaliar(B / 'kael-7.json', 'rapido')
    assert {e for es in _calculados(r).values() for e in es} == {'controle'}


def test_tatico_puxa_dano_area_controle(tmp_res):
    from dh.build import carregar
    b = carregar(B / 'tinbin-7.json'); imp = motor.impressao(b)
    antes = I.da_build(b, 'rapido', imp)
    _mexe('tatico.py')
    depois = I.da_build(b, 'rapido', imp)
    for l in b['linhas']:
        mudou = {e for e in antes[l['id']] if antes[l['id']][e] != depois[l['id']][e]}
        assert mudou == ({'tatico', 'dano', 'area', 'controle'} if 'tatico' in l else set()), (l['id'], mudou)


def test_build_mexida_so_no_eixo_mexido(tmp_res, tmp_path):
    b = json.loads((B / 'kael-7.json').read_text(encoding='utf-8'))
    l = next(l for l in b['linhas'] if 'defesa' in l)
    l['defesa'] = dict(l['defesa'], pv_efetivo=l['defesa'].get('pv_efetivo', b['corpo']['pv']) + 5)
    arq = tmp_path / 'entrada' / 'kael-7.json'; arq.parent.mkdir(); arq.write_text(json.dumps(b), encoding='utf-8')
    _, r = motor.avaliar(arq, 'rapido')
    calc = _calculados(r)   # linhas que herdam a defesa mudam junto
    assert l['id'] in calc and all(es == ['defesa'] for es in calc.values()), calc


def test_versao_forca_tudo(tmp_res, base, monkeypatch):
    monkeypatch.setattr(motor, 'VERSAO', 'outra')
    _, r = motor.avaliar(B / 'kael-7.json', 'rapido')
    assert _calculados(r) == _calculados(base[1]['kael-7'])


def test_resultado_antigo_sem_impressoes_e_aproveitado(tmp_res):
    arq = tmp_res / 'kael-7.json'
    d = json.loads(arq.read_text(encoding='utf-8')); imps = d.pop('impressoes')
    arq.write_text(json.dumps(d), encoding='utf-8')
    _, r = motor.avaliar(B / 'kael-7.json', 'rapido')
    assert r.get('_cache') is True
    assert json.loads(arq.read_text(encoding='utf-8'))['impressoes'] == imps


def test_so_segundos_nao_regrava(tmp_res):
    arq = tmp_res / 'kael-7.json'; antes = arq.read_text(encoding='utf-8')
    motor.avaliar(B / 'kael-7.json', 'rapido', forcar=True)
    assert arq.read_text(encoding='utf-8') == antes


def test_planos_nao_dependem_de_numpy(tmp_res):
    """Eixo recém-calculado (numpy.float64) e reaproveitado do JSON (float) dão o mesmo plano."""
    import numpy as np
    from dh import base, planos
    from dh.build import carregar
    from dh.controle import campo
    b = carregar(B / 'rpgbot-fighter-battle-master-3.json')
    _, r = motor.avaliar(B / 'rpgbot-fighter-battle-master-3.json', 'rapido')
    def np_(x):
        if isinstance(x, dict): return {k: np_(v) for k, v in x.items()}
        if isinstance(x, list): return [np_(v) for v in x]
        return np.float64(x) if isinstance(x, float) else x
    linhas = json.loads(json.dumps(r['linhas']))
    for l in linhas.values(): l['controle']['nivel_atencao'] = 0.45        # empate no arredondamento
    a = planos.agregar(b, linhas, campo.MAGIAS, base.letra)
    c = planos.agregar(b, np_(linhas), campo.MAGIAS, base.letra)
    assert json.loads(json.dumps(a)) == json.loads(json.dumps(c, default=float))
