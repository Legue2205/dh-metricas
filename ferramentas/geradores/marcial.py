"""Funções comuns dos geradores de marciais (Barbarian, Monk). Extraídas de bar.py em 21/11."""
import json, re, sys
sys.path.insert(0, 'ferramentas/geradores')
from wiz import _anula

OUT = 'progressoes/'
NIV = (3, 5, 7, 9, 11)
CLASSE = 'barbarian'
NOTA = "Build exemplo do guia de subclasse (2014). Passada 1 cega: só mecânica; premissas congeladas."


def pb(L): return 2 + (L - 1) // 4
def M(f, d, c, i, w, ch): return {"for": f, "des": d, "con": c, "int": i, "sab": w, "car": ch}
def mod(x): return (x - 10) // 2
def furias(bl): return 2 if bl < 3 else 3 if bl < 6 else 4 if bl < 12 else 5
def rdano(bl): return 2 if bl < 9 else 3 if bl < 16 else 4
def hp(dados, con):   # dados: lista dos dados de vida por nível, na ordem
    return sum((d if i == 0 else d // 2 + 1) + con for i, d in enumerate(dados))


def sv(L, m, profs=('for', 'con')): return {k: m[k] + (pb(L) if k in profs else 0) for k in m}


def crit(dano, arma, extra):
    """dados_crit = todos os dados da string + `extra` dados da arma (Brutal Critical, Savage Attacks)."""
    ds = re.findall(r'(\d+)d(\d+)', dano)
    out = [f"{n}d{f}" for n, f in ds]
    if extra:
        n, f = re.match(r'(\d+)d(\d+)', arma).groups(); out.append(f"{extra}d{f}")
    return '+'.join(out)


def A(n, bonus, arma, fixo, extra='', bc=0, **k):
    d = f"{arma}+{fixo}{extra}"
    a = dict(n=round(n, 4), bonus=bonus, dano=d, **k)
    if bc: a['dados_crit'] = crit(d, arma, bc)
    return a


def ctrl(papel, extra=()): return {"atencao": {"papel": papel, "soft": 0.15, "dpr": "auto"},
                                   "fontes": list(extra) + [{"tipo": "ameaca", "nome": "Corpo (ameaça)"}]}


def linha(id_, hip, dano, defesa, saves=None, controle=None, papel='striker', gasta=None, suporte=None,
          area=None, reacao=None, plano=None):
    l = {"id": id_, "hipotese": hip, "dano": dano, "defesa": defesa, "controle": controle or ctrl(papel),
         "saves": saves or {}}
    if gasta: l['gasta'] = gasta
    if suporte: l['suporte'] = {"fontes": suporte}
    if area: l['area'] = area
    if reacao: l['reacao'] = reacao
    if plano: l['plano'] = plano
    return l


def escrever(id_, slug, nome, build, desc, fat, grupo="RPGBot", fonte=None):
    b = fat[3]
    b['linhas'][0].update(principal=True, custo='gratuita')
    base = dict(build=build, corpo=b['corpo'], recursos=b['recursos'], linhas=b['linhas'],
                planos={"padrao": "auto", "combate_unico": "auto"}, descricao=desc)
    niv = {'3': {"_texto": b.get('_texto', '')}}
    if b.get('patches_linhas'): niv['3']['patches_linhas'] = b['patches_linhas']   # 27/11: features em várias linhas
    ant = json.loads(json.dumps(dict(corpo=base['corpo'], recursos=base['recursos'], linhas=base['linhas'])))
    tem = bool(b.get('patches_linhas'))
    for L in NIV[1:]:
        f = fat[L]
        cur = json.loads(json.dumps(dict(corpo=f['corpo'], recursos=f['recursos'], linhas=f['linhas'])))
        niv[str(L)] = dict(_texto=f.get('_texto', ''), **_anula(ant, json.loads(json.dumps(cur))))
        if f.get('patches_linhas') or tem: niv[str(L)]['patches_linhas'] = f.get('patches_linhas', []); tem = True
        ant = cur
    fonte = fonte or {"tipo": "rpgbot", "url": f"https://rpgbot.net/dnd5/characters/classes/{CLASSE}/subclasses/{slug}/",
                      "nota": NOTA}
    P = dict(id=id_, nome=nome, grupo=grupo, fonte=fonte, base=base, niveis=niv)
    import m1_reacoes, m3_sobrevivencia; m1_reacoes.aplicar(P); m3_sobrevivencia.aplicar(P)   # M1/M3 (23/11)
    with open(OUT + id_ + '.json', 'w') as fh: json.dump(P, fh, ensure_ascii=False, indent=1)
    print('ok', id_)


def MAO_CURA(usos, pv, L):
    """Mercy: Hand of Healing usos vezes na luta (toque, no Flurry). Até suporte.h.P_CAIDO usos levantam um caído
    (cura_na_luta); o resto cura um aliado de pé ("cura" com o acesso do toque). Physician's Touch (6): a mesma mão tira
    uma condição (resgate sem save)."""
    import sys; sys.path.insert(0, '.'); from dh.premissas import P  # noqa: E402
    pc = P('suporte.h.P_CAIDO'); base = {"lado": "def", "alcance": "toque", "pv": pv}
    out = [dict(base, nome="Hand of Healing (levanta um caído)", modelo="cura_na_luta", acao="bonus", usos_luta=usos),
           dict(base, nome="Hand of Healing (aliado de pé)", modelo="cura", usos_luta=round(max(0.0, usos - pc), 3))]
    if L >= 6:
        out.append({"nome": "Physician's Touch (tira a condição na Hand of Healing)", "lado": "def", "modelo": "resgate_condicao",
                    "p_save": 1.0, "vantagem": False})
    return out
