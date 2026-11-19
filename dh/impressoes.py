"""Impressão digital por eixo (19/11, tarefa 3): o motor só recalcula o eixo cuja impressão mudou.

Impressão de um eixo numa linha = hash de
  1. os arquivos-fonte de que o eixo depende: os módulos-raiz abaixo + tudo o que eles importam dentro de dh/
     (levantado pelos `from . import …` do próprio código, inclusive imports dentro de funções), mais os arquivos de
     dados (magias.json) e dh/eixos.py (a ligação de cada eixo, comum a todos);
  2. os valores das premissas sob os prefixos do eixo;
  3. a parte da linha (e da build) que o eixo lê — e o modo (rápido/completo) para os eixos que dependem dele.

Linha com "tatico": dano, área e controle saem do motor tático, então a impressão deles inclui também a do tático.
Ficam de fora (não mudam número): premissas.py (só a leitura; os valores entram pelo item 2), arquivos.py (escrita
atômica), __init__.py. A orquestração e o cache (motor.py, este arquivo) também não entram: quem mexer neles de um
jeito que mude número deve subir VERSAO (dh/__init__.py), que continua forçando o recálculo de tudo.
"""
import ast
import hashlib
import json
from functools import lru_cache
from pathlib import Path

PACOTE = Path(__file__).resolve().parent
FORA = {'premissas.py', 'arquivos.py', '__init__.py'}
COMUNS = ('eixos.py',)
DADOS = {'controle/campo.py': ('controle/magias.json',)}

# Eixo -> módulos-raiz (o resto vem pelos imports). "_planos" = agregado de planos/anéis (sempre refeito quando a
# build é processada; a impressão dele só decide se uma build sem mudança nenhuma pode ser pulada inteira).
RAIZES = {
    'tatico': ('tatico',),
    'dano': ('dano',),
    'defesa': ('defesa', 'orcamento'),
    'saves': ('saves', 'orcamento'),
    'area': ('horda', 'area', 'dano'),
    'suporte': ('suporte',),
    'controle': ('controle.total', 'controle.efeitos', 'controle.atencao', 'controle.campo'),
    '_planos': ('planos', 'orcamento', 'aneis'),
}
# Eixo -> prefixos de premissas (largos de propósito: "base." entra em todos)
PREFIXOS = {
    'tatico': ('base.', 'tatico.'),
    'dano': ('base.', 'dano.'),
    'defesa': ('base.', 'defesa.'),
    'saves': ('base.', 'saves.'),
    'area': ('base.', 'area.', 'dano.'),
    'suporte': ('base.', 'suporte.'),
    'controle': ('base.', 'controle.'),
    '_planos': ('base.', 'planos.', 'eixos.', 'controle.'),
}
DO_TATICO = ('dano', 'area', 'controle')

# Para testes: {caminho relativo a dh/: hash fingido} (simula mexer num arquivo sem mexer)
SOBRESCREVER = {}


def _arquivo(mod):
    """'controle.total' -> Path de dh/controle/total.py (ou do __init__ do pacote); None se não existir."""
    p = PACOTE.joinpath(*mod.split('.'))
    if p.with_suffix('.py').is_file(): return p.with_suffix('.py')
    if (p / '__init__.py').is_file(): return p / '__init__.py'
    return None


@lru_cache(maxsize=None)
def _imports(mod):
    """Módulos de dh/ importados por mod (relativos, em qualquer lugar do arquivo)."""
    arq = _arquivo(mod)
    if arq is None: return ()
    pkg = mod.split('.')[:-1] if arq.name != '__init__.py' else mod.split('.')
    out = set()
    for no in ast.walk(ast.parse(arq.read_text(encoding='utf-8'))):
        if not isinstance(no, ast.ImportFrom) or not no.level: continue
        base = pkg[:len(pkg) - (no.level - 1)] + (no.module.split('.') if no.module else [])
        if base and _arquivo('.'.join(base)): out.add('.'.join(base))
        for n in no.names:
            sub = '.'.join(base + [n.name])
            if _arquivo(sub): out.add(sub)
    return tuple(sorted(out))


@lru_cache(maxsize=None)
def modulos(eixo):
    """Fecho dos imports a partir das raízes do eixo."""
    visto, pilha = set(), list(RAIZES[eixo])
    while pilha:
        m = pilha.pop()
        if m in visto: continue
        visto.add(m); pilha += _imports(m)
    return tuple(sorted(visto))


def arquivos(eixo):
    """Caminhos (relativos a dh/) que entram na impressão do eixo."""
    out = set(COMUNS)
    for m in modulos(eixo):
        rel = _arquivo(m).relative_to(PACOTE).as_posix()
        if Path(rel).name in FORA: continue
        out.add(rel); out.update(DADOS.get(rel, ()))
    return tuple(sorted(out))


@lru_cache(maxsize=None)
def _hash_arquivo(rel):
    if rel in SOBRESCREVER: return SOBRESCREVER[rel]
    return hashlib.sha1((PACOTE / rel).read_bytes()).hexdigest()


@lru_cache(maxsize=None)
def _hash_codigo(eixo):
    return _h([(r, _hash_arquivo(r)) for r in arquivos(eixo)])


def _hash_premissas(eixo):
    from .premissas import _dados
    pref = PREFIXOS[eixo]
    return _h({k: v['valor'] for k, v in sorted(_dados().items()) if k.startswith(pref)})


def limpar():
    """Esquece os hashes de arquivo guardados (depois de mexer em SOBRESCREVER ou num arquivo)."""
    for f in (_imports, modulos, _hash_arquivo, _hash_codigo): f.cache_clear()


def _h(x):
    return hashlib.sha1(json.dumps(x, sort_keys=True, ensure_ascii=False, default=str).encode()).hexdigest()[:12]


def parte(eixo, b, linha, modo):
    """O que o eixo lê da linha e da build (a linha crua, antes do motor tático)."""
    g = linha.get; corpo = dict(b['corpo'], **linha.get('corpo', {}))
    if eixo == 'tatico': return dict(build=b.get('tatico'), linha=g('tatico'))
    if eixo == 'dano': return dict(dano=g('dano'), inv=g('invocacoes'), lutas=b.get('recursos', {}).get('lutas_dia', 4))
    if eixo == 'defesa': return dict(defesa=g('defesa'), corpo=corpo, reacao=g('reacao'))
    if eixo == 'saves': return dict(saves=g('saves'), corpo=corpo, reacao=g('reacao'))
    if eixo == 'area': return dict(area=g('area'), dano=g('dano'), inv=g('invocacoes'), modo=modo)
    if eixo == 'suporte': return dict(suporte=g('suporte'), nivel=b['nivel'])
    if eixo == 'controle': return dict(controle=g('controle'), inv=g('invocacoes'), corpo=corpo, nivel=b['nivel'], modo=modo)
    raise KeyError(eixo)


def do_eixo(eixo, b, linha, modo):
    x = [eixo, _hash_codigo(eixo), _hash_premissas(eixo), parte(eixo, b, linha, modo)]
    if 'tatico' in linha and eixo in DO_TATICO: x.append(do_eixo('tatico', b, linha, modo))
    return _h(x)


def da_linha(b, linha, modo):
    from .eixos import presentes
    return {e: do_eixo(e, b, linha, modo) for e in presentes(linha)}


def da_build(b, modo, imp):
    """{"_planos": …, <id da linha>: {eixo: impressão}}; imp = impressão da build inteira (planos leem tudo)."""
    out = {'_planos': _h(['_planos', _hash_codigo('_planos'), _hash_premissas('_planos'), imp])}
    for l in b['linhas']: out[l['id']] = da_linha(b, l, modo)
    return out
