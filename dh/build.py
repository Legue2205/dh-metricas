"""build.json: carregar, validar e calcular uma impressão digital (para só recalcular o que mudou)."""
import hashlib
import json
from pathlib import Path

from .controle.campo import MAGIAS
from .controle.efeitos import TIPOS as TIPOS_FONTE
from . import orcamento
from .defesa import REACOES
from .suporte import MODELOS

PAPEIS = {'tank', 'striker', 'atirador', 'conjurador'}
EIXOS = ('dano', 'defesa', 'controle', 'saves', 'area', 'suporte')


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
    if not any(l.get('principal') for l in b['linhas']): e.append('nenhuma linha com "principal" (true ou lista de eixos)')
    for l in b['linhas']:
        pr = l.get('principal')
        if isinstance(pr, list) and not set(pr) <= set(EIXOS): e.append(f"linha {l.get('id')}: principal deve listar eixos de {EIXOS}")
    ids = [l.get('id') for l in b['linhas']]
    if len(ids) != len(set(ids)): e.append('ids de linha repetidos')
    for l in b['linhas']:
        nome = f"linha {l.get('id')}"
        if not any(x in l for x in EIXOS): e.append(f'{nome}: nenhum eixo ({"/".join(EIXOS)})')
        for r in (l.get('defesa') or {}).get('reacoes', []):
            if r.get('tipo') not in REACOES: e.append(f'{nome}: reação de defesa desconhecida "{r.get("tipo")}"')
        if 'saves' in l and 'sv' not in l['saves'] and 'sv' not in b['corpo'].get('saves', {}):
            e.append(f'{nome}: saves sem os bônus "sv" (ponha em corpo.saves.sv)')
        for f in (l.get('suporte') or {}).get('fontes', []):
            if f.get('modelo') not in MODELOS: e.append(f'{nome}: suporte com modelo desconhecido "{f.get("modelo")}"')
            if f.get('lado') not in ('of', 'def'): e.append(f'{nome}: fonte de suporte sem "lado" (of/def)')
        if l.get('cenario', 'dia_padrao') not in ('dia_padrao', 'luta_prioritaria'): e.append(f'{nome}: cenario inválido')
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
    if not e: e += orcamento.checar(b, MAGIAS)[0]
    return e


def avisos(b):
    return orcamento.checar(b, MAGIAS)[1]


def impressao(b):
    return hashlib.sha1(json.dumps(b, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:10]
