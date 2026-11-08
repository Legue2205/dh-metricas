"""build.json: carregar, validar e calcular uma impressão digital (para só recalcular o que mudou)."""
import hashlib
import json
from pathlib import Path

from .controle.campo import MAGIAS
from .controle.efeitos import TIPOS as TIPOS_FONTE

PAPEIS = {'tank', 'striker', 'atirador', 'conjurador'}
EIXOS = ('dano', 'defesa', 'controle')


class ErroBuild(ValueError):
    pass


def carregar(caminho):
    b = json.loads(Path(caminho).read_text(encoding='utf-8'))
    erros = validar(b)
    if erros: raise ErroBuild(f'{caminho}:\n  - ' + '\n  - '.join(erros))
    return b


def _magias_usadas(f):
    if 'magia' in f: yield f['magia']
    yield from f.get('magias', [])
    for a in f.get('acoes', []): yield a['magia']
    if 'solo' in f: yield f['solo']['magia']
    for op in f.get('opcoes', []): yield from _magias_usadas(op)


def validar(b):
    e = []
    for k in ('id', 'nome', 'grupo', 'nivel', 'corpo', 'linhas'):
        if k not in b: e.append(f'falta "{k}"')
    if e: return e
    for k in ('ca', 'pv'):
        if k not in b['corpo']: e.append(f'corpo: falta "{k}"')
    if not any(l.get('principal') for l in b['linhas']): e.append('nenhuma linha com "principal": true')
    ids = [l.get('id') for l in b['linhas']]
    if len(ids) != len(set(ids)): e.append('ids de linha repetidos')
    for l in b['linhas']:
        nome = f"linha {l.get('id')}"
        if not any(x in l for x in EIXOS): e.append(f'{nome}: nenhum eixo (dano/defesa/controle)')
        d = l.get('dano')
        if d is not None:
            if 'medido' in d and len(d['medido']) != 9: e.append(f'{nome}: dano.medido precisa de 9 valores (CA 11…25)')
            for a in d.get('ataques', []):
                for k in ('bonus', 'dano'):
                    if k not in a: e.append(f'{nome}: ataque sem "{k}"')
        c = l.get('controle')
        if c is not None:
            at = c.get('atencao', {})
            if at.get('papel') not in PAPEIS: e.append(f'{nome}: controle.atencao.papel deve ser um de {sorted(PAPEIS)}')
            if 'dpr' not in at: e.append(f'{nome}: controle.atencao.dpr faltando')
            for f in c.get('fontes', []):
                if f.get('tipo') not in TIPOS_FONTE: e.append(f'{nome}: fonte de tipo desconhecido "{f.get("tipo")}"')
                for m in _magias_usadas(f):
                    if m not in MAGIAS: e.append(f'{nome}: magia "{m}" não está em magias.json')
    return e


def impressao(b):
    return hashlib.sha1(json.dumps(b, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:10]
