"""Pacote C (27/11): mecânicas de subclasse nas progressões rpgbot-* cujos geradores não reproduzem mais o arquivo
(wiz_builds.py e fighter_lote2.py ficaram para trás das edições à mão). Edita o JSON da progressão, nível a nível,
escrevendo só o que muda em cada linha; idempotente. Rodar da raiz: python ferramentas/geradores/c_mecanicas.py
e depois python -m dh expandir <progressões>.

  - Bladesinging: o Bladesong sai das linhas "canto" (gasto e CA próprios) e vira patches_linhas com cobertura
    (PB usos/dia ÷ lutas; +Int na CA em todas as linhas), como no chassi_wizard.
  - Abjuration (a partir do Wizard 6): Projected Ward em todas as linhas (chassi_wizard.PROJECTED_WARD).
  - Divination: Portent dividido entre controle e suporte (chassi_wizard.portent).
  - Psi Warrior: linha "campo-protetor" (chassi_fighter.PROTECTIVE_FIELD).
Order's Wrath não entra nas builds do RPGBot: o gatilho é o Divine Strike com arma, e elas usam truque (Blessed Strikes).
"""
import copy
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, '.')
from dh.progressao import fatias  # noqa: E402
from dh.premissas import P  # noqa: E402

PASTA = Path('progressoes')


def pb(L): return 2 + (L - 1) // 4


def _dif(a, b):
    """Valor novo para o merge recursivo da progressão: dict ganha None nas chaves que sumiram."""
    if isinstance(a, dict) and isinstance(b, dict):
        out = {k: _dif(a.get(k), v) for k, v in b.items()}
        out.update({k: None for k in a if k not in b})
        return out
    return copy.deepcopy(b)


def _junta(a, b):
    """Duas entradas da mesma linha no mesmo patch numa só (merge recursivo; None = apaga, fica marcado)."""
    for k, v in b.items():
        if isinstance(v, dict) and isinstance(a.get(k), dict): _junta(a[k], v)
        else: a[k] = copy.deepcopy(v)


def _sem_none(d):
    for k in [k for k, v in d.items() if v is None]: d.pop(k)
    for v in d.values():
        if isinstance(v, dict): _sem_none(v)


def _grava_linhas(prog, nv, antes, depois):
    """Escreve no patch do nível as chaves de linha que mudaram (valor inteiro; None apaga)."""
    patch = prog['niveis'].setdefault(str(nv), {})
    ls = patch.setdefault('linhas', [])
    a = {l['id']: l for l in antes}
    for l in depois:
        o = a.get(l['id'])
        if o is None:
            ls.append(copy.deepcopy(l)); continue
        mud = {k: _dif(o.get(k), v) for k, v in l.items() if o.get(k) != v}
        mud.update({k: None for k in o if k not in l})
        if mud: ls.append(dict(id=l['id'], **mud))
    if not ls: patch.pop('linhas')


def _limpa(b):
    """Linha resolvida → forma de progressão (tira o que o resolver acrescenta)."""
    for l in b['linhas']: l.pop('_patches', None)
    return b


def aplicar(nome, fn, patches=None, recursos=None):
    """fn(nv, build) muda as linhas da fatia; patches(nv, build) -> lista de patches_linhas do pacote C (ou None)."""
    arq = PASTA / f'{nome}.json'; prog = json.loads(arq.read_text(encoding='utf-8')); antes = json.dumps(prog, sort_keys=True)
    fs = fatias(copy.deepcopy(prog))
    for nv in sorted(fs):
        b = _limpa(fs[nv]); novo = copy.deepcopy(b)
        if fn: fn(nv, novo)
        _grava_linhas(prog, nv, b['linhas'], novo['linhas'])
        patch = prog['niveis'][str(nv)]
        if patches:
            ps = [x for x in patch.get('patches_linhas', []) if x.get('origem') not in ORIGENS_C]
            ps += patches(nv, novo) or []
            if ps: patch['patches_linhas'] = ps
        if recursos: recursos(nv, patch, b)
    # entradas de linha repetidas (rodar duas vezes) não mudam o resultado, mas o arquivo cresce: compacta por id
    antes_ids = set(l['id'] for l in prog['base'].get('linhas', []))
    for nv in sorted(prog['niveis'], key=int):
        patch = prog['niveis'][nv]
        if 'linhas' in patch:
            visto = {}
            for l in patch['linhas']:
                if l['id'] in visto: _junta(visto[l['id']], l)
                else: visto[l['id']] = copy.deepcopy(l)
            for i, l in visto.items():
                if i not in antes_ids: _sem_none(l)   # linha nova neste nível: não há o que apagar
            patch['linhas'] = list(visto.values())
            antes_ids |= set(visto)
    if json.dumps(prog, sort_keys=True) != antes:
        arq.write_text(json.dumps(prog, ensure_ascii=False, indent=1) + '\n', encoding='utf-8'); print('ok', nome)


ORIGENS_C = ('Bladesong', 'Projected Ward', 'Volley')


# ---------------- Bladesinging ----------------
def _int(b): return b['corpo']['saves']['sv']['int'] - pb(b['nivel'])


def bladesong_linhas(nv, b):
    ca = b['corpo']['ca']
    for l in b['linhas']:
        if not l['id'].startswith('canto'): continue
        g = dict(l.get('gasta') or {}); g.pop('bladesong', None); l['gasta'] = g
        l.pop('corpo', None)
        if l['id'] == 'canto-haste': l['corpo'] = {"ca": ca + 2}
        l['hipotese'] = re.sub(r'^Bladesong \+ ', '', l.get('hipotese', l['id']))


def bladesong_patches(nv, b):
    return [{"origem": "Bladesong", "cobertura": {"usos": pb(nv), "volta": "longo"}, "corpo": {"ca": _int(b)}}]


def bladesong_recursos(nv, patch, b):
    if 'bladesong' in (b.get('recursos', {}).get('outros') or {}):
        patch.setdefault('recursos', {}).setdefault('outros', {})['bladesong'] = None


# ---------------- Abjuration ----------------
def ward(b):
    m = re.search(r'Arcane Ward (\d+)', b.get('descricao', {}).get('progressao', ''))
    return int(m.group(1)) if m else None


def projected(wiz_nv):
    def f(nv, b):
        if wiz_nv(nv) < 6 or not ward(b): return []
        fr = {"$p": "suporte.padroes.ward_projetado_fracao"}; w = ward(b)
        return [{"origem": "Projected Ward", "fator": fr, "corpo": {"pv": -w},
                 "reacao": {"uso": "Projected Ward", "fracao": {"$p": "suporte.padroes.ward_projetado_reacao"}, "eixos": ["suporte"]},
                 "anexar": {"suporte.fontes": [{"nome": "Projected Ward (Arcane Ward num aliado)", "lado": "def",
                                                "modelo": "pv_temporario", "pv": w, "usos_luta": 1, "fator": fr}]}}]
    return f


# ---------------- Divination ----------------
def portent_linhas(nv, b, dados=2):
    fr = {"$p": "suporte.padroes.portent_fracao_controle"}
    for l in b['linhas']:
        sp = l.get('suporte') or {}
        if any(x.get('nome', '').startswith('Portent') for x in sp.get('fontes', [])): continue
        com = [x for x in (l.get('controle') or {}).get('fontes', []) if x.get('forcar_falha')]
        if com:
            l['controle'] = copy.deepcopy(l['controle'])
            for x in l['controle']['fontes']:
                if x.get('forcar_falha'): x['forcar_falha_fator'] = fr
        fonte = {"nome": "Portent (rolagens de aliados e inimigos)", "lado": "def", "modelo": "dado_multiuso",
                 "vira": {"$p": "suporte.padroes.portent_vira"}, "mix": {"$p": "suporte.padroes.portent_mix"},
                 "acao": "nenhuma", "usos_luta": round(dados / 4, 3)}
        if com: fonte.update(fator=fr, complemento=True)
        l['suporte'] = dict(sp, fontes=list(sp.get('fontes', [])) + [fonte])


# ---------------- Psi Warrior ----------------
def campo_protetor(nv, b):
    if any(l['id'] == 'campo-protetor' for l in b['linhas']): return
    pr = next(l for l in b['linhas'] if l.get('principal'))
    d = copy.deepcopy(pr['dano']); ps = [x for x in d.get('por_luta', []) if x.get('nota', '').startswith('Psionic Strike')]
    if not ps: return
    x = ps[0]; d['por_luta'] = [y for y in d['por_luta'] if y is not x]
    if not d['por_luta']: d.pop('por_luta')
    m = re.fullmatch(r'1d(\d+)\+(\d+)', x['dano']); faces, mi = int(m.group(1)), int(m.group(2))
    u = round(x['usos_dia'] / 4, 3)
    ctl = copy.deepcopy(pr.get('controle') or {})
    ctl['fontes'] = [f for f in ctl.get('fontes', []) if 'Psionic Strike' not in f.get('nome', '')]
    b['linhas'].append({"id": "campo-protetor", "herda": "principal",
                        "hipotese": "dados psiônicos da luta no Protective Field (reação), sem Psionic Strike",
                        "dano": d, "controle": ctl,
                        "suporte": {"fontes": [{"nome": "Protective Field (reduz o dano de um aliado)", "lado": "def",
                                                "modelo": "pv_temporario", "pv": round((faces + 1) / 2 + mi, 2), "usos_luta": u}]},
                        "reacao": [{"uso": "Protective Field", "fracao": round(min(1.0, u / P('base.rounds_por_luta')), 3),
                                    "eixos": ["suporte"]}]})


def _nm(nome, tirar):
    arq = PASTA / f'{nome}.json'; prog = json.loads(arq.read_text(encoding='utf-8'))
    d = prog['base'].get('descricao', {}); t = d.get('nao_modelado', '')
    for x in tirar: t = t.replace(x, '')
    t = re.sub(r'\s*;\s*;', ';', t).strip('; ').replace(' ;', ';')
    if t != d.get('nao_modelado'):
        d['nao_modelado'] = t; arq.write_text(json.dumps(prog, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')


if __name__ == '__main__':
    aplicar('rpgbot-wizard-bladesinging', bladesong_linhas, bladesong_patches, bladesong_recursos)
    aplicar('rpgbot-wizard-abjuration', None, projected(lambda nv: nv - 1))       # Artificer 1 / Wizard nv − 1
    aplicar('rpgbot-wizard-abjuration-puro', None, projected(lambda nv: nv))
    aplicar('rpgbot-wizard-divination', portent_linhas)
    aplicar('rpgbot-fighter-psi-warrior', campo_protetor)
    _nm('rpgbot-wizard-abjuration', [' e Projected Ward'])
    _nm('rpgbot-wizard-abjuration-puro', [' e Projected Ward'])
    _nm('rpgbot-wizard-divination', ["Portent nos aliados (ataques e saves) e nos ataques inimigos (só entra forçando falha no save das magias); "])
    _nm('rpgbot-fighter-psi-warrior', ['Protective Field (todos os dados foram para o Psionic Strike); '])
