"""build.json: carregar, validar e calcular uma impressão digital (para só recalcular o que mudou)."""
import hashlib
import json
from pathlib import Path

from .controle.campo import MAGIAS
from .controle.efeitos import TIPOS as TIPOS_FONTE
from . import orcamento, planos
from .defesa import REACOES
from .suporte import MODELOS

PAPEIS = {'tank', 'striker', 'frontliner', 'atirador', 'conjurador'}   # tank e striker = vaga de frontliner (19/11)
EIXOS = ('dano', 'defesa', 'controle', 'saves', 'area', 'suporte')


class ErroBuild(ValueError):
    pass


def carregar(caminho):
    from .premissas import resolver as _premissas
    from .invocacoes import aplicar as _invocacoes
    b = _invocacoes(_premissas(json.loads(Path(caminho).read_text(encoding='utf-8'))))
    erros = validar(b)
    if erros: raise ErroBuild(f'{caminho}:\n  - ' + '\n  - '.join(erros))
    return b


def _magias_usadas(f):
    if 'magia' in f: yield f['magia']
    yield from f.get('magias', [])
    for a in f.get('acoes', []): yield a['magia']
    if 'solo' in f: yield f['solo']['magia']
    for op in f.get('opcoes', []): yield from _magias_usadas(op)


def _reacoes_magicas(b, linhas):
    """M1 (23/11): "reacoes_magicas" da build viram linhas "reacao-<magia>" = principal + os campos da reação
    (tabela _reacoes_magicas do magias.json). Idempotente; respeita "desde" (nível mínimo)."""
    rm = b.get('reacoes_magicas') or []
    if not rm or not b.get('linhas'): return
    from pathlib import Path
    tab = json.loads((Path(__file__).parent / 'controle' / 'magias.json').read_text(encoding='utf-8')).get('_reacoes_magicas', {})
    base = next((l for l in b['linhas'] if l.get('principal')), b['linhas'][0])
    for r in rm:
        m = r if isinstance(r, str) else r.get('magia')
        if m not in tab or (isinstance(r, dict) and b.get('nivel', 99) < r.get('desde', 1)): continue
        lid = 'reacao-' + m.replace('_', '-')
        if lid in linhas: continue
        nova = {k: json.loads(json.dumps(v)) for k, v in base.items() if k not in ('id', 'principal', 'hipotese', 'herdou', 'custo')}
        for eixo, campos in tab[m].items():
            if isinstance(campos, dict): nova[eixo] = dict(nova.get(eixo) or {}, **campos)
        nova.update(id=lid, hipotese=f"{base.get('hipotese', base['id'])} + {tab[m].get('rotulo', m)} (reação)",
                    herdou=base['id'])
        b['linhas'].append(nova); linhas[lid] = nova


def _patches_linhas(b):
    """M3 (23/11): "patches_linhas" da build = features que valem em várias linhas (Second Wind, Indomitable, Relentless
    Rage…): [{"origem": texto, "quando_gasta": "furia" (opcional), "eixos": {"defesa": {"cura_luta": 7}}}]. Número soma
    ao que a linha (ou, nos saves, o corpo) já tem; dict mescla num sub-dict que a linha já tem; o resto substitui. Idempotente (marca as origens já aplicadas)."""
    for p in b.get('patches_linhas') or []:
        for l in b.get('linhas', []):
            if p.get('origem') in l.get('_patches', []): continue
            if p.get('quando_gasta') and p['quando_gasta'] not in (l.get('gasta') or {}): continue
            for eixo, campos in p.get('eixos', {}).items():
                atual = dict(l.get(eixo) or {})
                for k, v in campos.items():
                    if isinstance(v, dict):   # D13 (24/11): sub-dict existente é mesclado (controle.atencao.redireciona)
                        if isinstance(atual.get(k), dict): atual[k] = {**atual[k], **v}
                        continue                # sem o sub-dict na linha (ex.: linha sem atenção): não cria
                    base = atual.get(k, (b.get('corpo', {}).get('saves', {}) if eixo == 'saves' else {}).get(k, 0))
                    atual[k] = round(base + v, 4) if isinstance(v, (int, float)) and isinstance(base, (int, float)) else v
                l[eixo] = atual
            l.setdefault('_patches', []).append(p.get('origem'))


def resolver(b):
    """Linhas com "herda": "<id>" recebem os eixos e campos que não declararam da linha-mãe (idempotente)."""
    linhas = {l['id']: l for l in b.get('linhas', []) if 'id' in l}
    for l in b.get('linhas', []):
        visto = set()
        while 'herda' in l and l['herda'] in linhas and l['herda'] not in visto:
            mae = linhas[l['herda']]; visto.add(l.pop('herda')); l['herdou'] = mae['id']
            for k, v in mae.items():
                if k not in l and k not in ('id', 'principal', 'hipotese', 'herdou'): l[k] = json.loads(json.dumps(v))
    _reacoes_magicas(b, linhas)
    _patches_linhas(b)
    for l in b.get('linhas', []):      # "dpr": "auto" na atenção = DPR da própria linha na CA da premissa
        at = (l.get('controle') or {}).get('atencao') or {}
        if at.get('dpr') == 'auto':
            from .dano import dpr
            from .premissas import valor
            at['dpr'] = round(dpr(l['dano'], valor('controle.atencao.ca_dpr_auto')), 1) if l.get('dano') else 0.0
    return b


LIMITE_TEXTO = 500   # caracteres; "resumo" é mais curto
LIMITE_RESUMO = 300


def _textos(d, caminho='descricao'):
    for k, v in d.items():
        if isinstance(v, dict): yield from _textos(v, f'{caminho}.{k}')
        elif isinstance(v, str): yield f'{caminho}.{k}', v, (LIMITE_RESUMO if k == 'resumo' else LIMITE_TEXTO)


def validar(b):
    e = []; resolver(b)
    for onde, txt, lim in _textos(b.get('descricao', {})):
        if len(txt) > lim: e.append(f'{onde}: {len(txt)} caracteres (máximo {lim})')
    for tag, p in b.get('planos', {}).items():
        if len(p.get('descricao', '')) > LIMITE_TEXTO: e.append(f'planos.{tag}.descricao: máximo {LIMITE_TEXTO} caracteres')
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
    for l in b['linhas']:
        if 'herda' in l: e.append(f"linha {l.get('id')}: herda de linha inexistente \"{l['herda']}\"")
    if not e: e += orcamento.checar(b, MAGIAS)[0] + planos.checar(b, MAGIAS)
    return e


def avisos(b):
    return orcamento.checar(b, MAGIAS)[1] + _avisos_suporte(b)


def _avisos_suporte(b):
    """Fonte de suporte em combate com usos por dia não pode aparecer em mais lutas do plano do que tem usos."""
    out = []; linhas = {l['id']: l for l in b['linhas']}
    for tag, p in b.get('planos', {}).items():
        if not isinstance(p, dict): continue
        cont = {}
        for c in p.get('combates', []):
            lid = c if isinstance(c, str) else c.get('linha')
            for f in (linhas.get(lid, {}).get('suporte') or {}).get('fontes', []):
                if 'usos_dia' in f and f.get('quando') != 'entre_lutas' and 'usos_luta' not in f:
                    k = f.get('nome', f['modelo']); cont[k] = (cont.get(k, (0, f['usos_dia']))[0] + 1, f['usos_dia'])
        for k, (n, u) in cont.items():
            if n > u: out.append(f'plano {tag}: suporte "{k}" ({u:g}/dia, usado inteiro na luta) aparece em {n} lutas')
    return out


def impressao(b):
    return hashlib.sha1(json.dumps(b, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:10]
