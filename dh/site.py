"""Gera o site estático (docs/index.html) a partir de builds/*.json e resultados/*.json. Um arquivo, sem servidor.

Entradas por aba: nas abas de plano (padrao, combate_unico, dia_longo) há uma entrada por build com plano;
na aba "legado", uma entrada "principal" por build (cada eixo vem da linha principal daquele eixo) e uma por linha.
Eixos do painel: Dano, Defesa Física, Defesa Mágica, Controle, Área, Suporte (ver base.defesa_fisica/magica).
"""
import json
from pathlib import Path

from . import base
from .build import carregar
from .planos import CATEGORIAS, TAGS

RAIZ = Path(__file__).resolve().parents[1]
MODELO = Path(__file__).with_name('site.html')
RES = ('dano', 'defesa', 'saves', 'controle', 'area', 'suporte')


def _eixos(get):
    """get(chave, sub=None) -> nível equivalente ou None."""
    r = get('saves', 'resiliencia')
    vals = dict(dano=get('dano'), deff=base.defesa_fisica(get('defesa'), r), defm=base.defesa_magica(get('saves', 'vontade'), r),
                controle=get('controle'), area=get('area'), suporte=get('suporte'))
    return {k: dict(n=round(x, 1), r=base.letra(x)) for k, x in vals.items() if x is not None}


def _nv(l, k, sub=None):
    x = (l or {}).get(k)
    if x is None: return None
    return (x[sub] if sub else x).get('nivel_eq')


def _plano_eixos(pe):
    def de(cat):
        def get(k, sub=None):
            x = pe.get(sub or k)
            if x is None: return None
            return x['nivel_eq'] if cat is None else x['por_categoria'].get(cat)
        return _eixos(get)
    e = de(None)
    cats = [c for c in CATEGORIAS if any(c in v['por_categoria'] for v in pe.values())]
    if len(cats) > 1:
        for c in cats:
            for k, x in de(c).items():
                if k in e: e[k].setdefault('c', {})[c] = x['n']
    return e


def _cds(fontes):
    out = set()
    for f in fontes:
        if 'cd' in f: out.add(f['cd'])
        out |= _cds(f.get('opcoes', []))
    return out


def _linha(b, spec, res):
    corpo = dict(b['corpo'], **spec.get('corpo', {}))
    sv = dict(corpo.get('saves', {})); sv.update(spec.get('saves') or {})
    c = spec.get('controle', {})
    r = {k: res[k] for k in RES + ('orcamento',) if k in res}
    if 'controle' in r: r['controle'] = {k: v for k, v in r['controle'].items() if k != 'negacao_por_fonte'}
    return dict(hipotese=res.get('hipotese', ''), principal=res.get('principal', []), pv=corpo['pv'], ca=corpo['ca'],
                saves=sv if 'saves' in spec else None, res=r,
                spec=dict(dano=spec.get('dano'), invocacoes=spec.get('invocacoes', []), area=spec.get('area', []),
                          defesa=spec.get('defesa'), cds=sorted(_cds(c.get('fontes', []))),
                          fontes=[f.get('nome', f['tipo']) for f in c.get('fontes', [])]
                          + [f"Corpo ({i['quantidade']} {i['nome']})" for i in spec.get('invocacoes', []) if i.get('corpo', True)],
                          papel=c.get('atencao', {}).get('papel')))


def _entrada(b, linhas, fonte, **k):
    ld = linhas.get(fonte.get('defesa')) or {}
    dano = (linhas.get(fonte.get('dano')) or {}).get('res', {}).get('dano')
    return dict(b=b['id'], fonte=fonte, pv=ld.get('pv', b['corpo']['pv']), ca=ld.get('ca', b['corpo']['ca']),
                dpr15=dano['dpr']['CA 15'] if dano else None, **k)


def dados():
    builds, entradas = {}, {t: [] for t in list(TAGS) + ['legado']}
    for f in sorted((RAIZ / 'resultados').glob('*.json')):
        res = json.loads(f.read_text(encoding='utf-8')); arq = RAIZ / 'builds' / f.name
        if not arq.exists(): continue
        b = carregar(arq); specs = {l['id']: l for l in b['linhas']}
        linhas = {lid: _linha(b, specs[lid], r) for lid, r in res['linhas'].items() if lid in specs}
        builds[b['id']] = dict(nome=b['nome'], grupo=b['grupo'], nivel=b['nivel'], build=b.get('build', ''),
                               descricao=b.get('descricao', {}), linhas=linhas)
        # legado: principal por eixo
        fonte = {}
        for k in RES:
            lid = next((i for i, l in linhas.items() if k in l['principal'] and k in l['res']), None)
            if lid: fonte[k] = lid
        entradas['legado'].append(_entrada(b, linhas, fonte, id=b['id'], tipo='principal', rotulo='linha principal',
                                           eixos=_eixos(lambda k, s=None: _nv(linhas.get(fonte.get(k), {}).get('res'), k, s))))
        # legado: uma entrada por linha
        for lid, l in linhas.items():
            fl = {k: lid for k in RES if k in l['res']}
            entradas['legado'].append(_entrada(b, linhas, fl, id=f"{b['id']}:{lid}", tipo='linha', rotulo=lid,
                                               estrela=bool(l['principal']), eixos=_eixos(lambda k, s=None: _nv(l['res'], k, s))))
        # planos do dia
        for tag, p in res.get('planos', {}).items():
            ordem = sorted(p['combates'], key=lambda c: -c['peso'])
            fp = {}
            for k in RES:
                lid = next((c['linha'] for c in ordem if k in linhas.get(c['linha'], {}).get('res', {})), None)
                if lid: fp[k] = lid
            plano = dict(combates=p['combates'], sobra=p['sobra'], hypercharged=p['hypercharged'],
                         descricao=b['planos'][tag].get('descricao', ''))
            entradas[tag].append(_entrada(b, linhas, fp, id=b['id'], tipo='plano', rotulo='plano do dia', plano=plano,
                                          eixos=_plano_eixos(p['eixos'])))
    return dict(builds=builds, entradas=entradas, abas=list(TAGS) + ['legado'], categorias=CATEGORIAS, rampa=base.RAMPA)


def gerar(destino=None):
    html = MODELO.read_text(encoding='utf-8').replace('/*DADOS*/null', json.dumps(dados(), ensure_ascii=False).replace('</', '<\\/'))
    destino = Path(destino or RAIZ / 'docs' / 'index.html'); destino.parent.mkdir(exist_ok=True)
    destino.write_text(html, encoding='utf-8')
    return destino
