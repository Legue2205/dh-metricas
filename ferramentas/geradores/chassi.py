"""Regras comuns das builds de CHASSI (mini-mutirão de 22/11/2026). Ver calibracao/convencoes-passada1.md, seção "Chassi".

Ideia: comparar subclasses sem o ruído das escolhas de build do RPGBot (raça, multiclasse, feats).
  - Sem multiclasse, sem features raciais, compra padrão 15/14/13/12/10/8 + 2/+1 de raça genérica (Tasha's).
  - A SUBCLASSE escolhe posição (uma das 6 abaixo), arma, armadura, estilo de luta e a ordem dos atributos.
  - Duas variantes por subclasse: "sem-feat" (todo ASI no atributo principal, depois no secundário) e "feat"
    (o 1º ASI vira o feat da subclasse; o resto igual). O feat da subclasse = o 1º feat NÃO racial da build do
    RPGBot daquela subclasse; sem build, o natural, registrado na descrição. Até 2 feats (2 variantes "feat").
  - Conjuradores plenos: só "sem-feat" (a quebra de concentração não é modelada, então War Caster/Resilient Con
    dariam zero).
  - Fatias 7 e 11 (níveis de calibração).
Id: chassi-<classe>-<subclasse> (sem feat) e chassi-<classe>-<subclasse>-f-<feat> (com feat). Grupo "Chassi".
"""
import json
import sys

sys.path.insert(0, 'ferramentas/geradores')
from wiz import _anula  # noqa: E402

OUT = 'progressoes/'
NIV = (7, 11)
ATRS = ('for', 'des', 'con', 'int', 'sab', 'car')
PADRAO = (15, 14, 13, 12, 10, 8)

# Posição = entrada do motor de atenção (Corpo/Controle). Mesmos campos das builds existentes.
POSICOES = {
    'defensor':   {"papel": "tank", "front": True, "soft": 0.15},
    'striker':    {"papel": "striker", "front": True, "soft": 0.15},
    'skirmisher': {"papel": "striker", "front": False, "acc_m": [0.9, 0.95, 1.0]},   # entra e sai: fora da linha, alcançável
    'atirador':   {"papel": "atirador", "front": False, "acc_m": [0.7, 0.8, 1.0]},   # = atirador de referência
    'meia':       {"papel": "conjurador", "front": False, "acc_m": [0.9, 0.95, 1.0], "conc": True},  # conjurador perto da frente
    'retaguarda': {"papel": "conjurador", "front": False, "acc_m": [0.8, 0.9, 1.0], "conc": True},   # = conjurador de referência
}
# Linhas que de fato ficam no corpo a corpo (Spirit Guardians, forma do Moon) podem declarar "front": true na linha.

ASI = {'fighter': (4, 6, 8, 12, 14, 16, 19), 'rogue': (4, 8, 10, 12, 16, 19)}
ASI_PADRAO = (4, 8, 12, 16, 19)


def pb(L): return 2 + (L - 1) // 4
def mod(x): return (x - 10) // 2


def atributos(classe, L, ordem, feat=None, meio_feat=None):
    """Atributos no nível L. ordem = os 6 atributos do mais ao menos importante (ex.: ('des','con','sab','car','int','for')).
    +2 no 1º e +1 no 2º (raça genérica). ASIs: +2 no principal até 20, depois no secundário até 20.
    feat: o 1º ASI vira feat; meio_feat: atributo que o feat sobe (+1), se for meio-feat."""
    s = dict(zip(ordem, PADRAO)); s[ordem[0]] += 2; s[ordem[1]] += 1
    asis = [n for n in ASI.get(classe, ASI_PADRAO) if n <= L]
    for i, _ in enumerate(asis):
        if feat and i == 0:
            if meio_feat: s[meio_feat] = min(20, s[meio_feat] + 1)
            continue
        pts = 2
        for a in ordem[:2]:
            sobe = min(pts, 20 - s[a]); s[a] += sobe; pts -= sobe
    return {a: s[a] for a in ATRS}


def mods(s): return {a: mod(v) for a, v in s.items()}


def hp(dado, L, con):
    """Dado de vida fixo da classe: máximo no 1º, média arredondada para cima depois."""
    return dado + con + (L - 1) * (dado // 2 + 1 + con)


def sv(L, m, profs): return {k: m[k] + (pb(L) if k in profs else 0) for k in m}


def atencao(posicao, dpr='auto', **extra):
    a = dict(POSICOES[posicao], dpr=dpr); a.update(extra); return a


def slug(feat): return feat.lower().replace("'", '').replace(' ', '-')


def escrever(classe, sub, posicao, fat, build, desc, feat=None, url=None):
    """fat = {7: {"corpo", "recursos", "linhas"[, "_texto"]}, 11: {...}}. A 1ª linha da fatia 7 vira a principal."""
    id_ = f"chassi-{classe}-{sub}" + (f"-f-{slug(feat)}" if feat else '')
    b = fat[NIV[0]]
    b['linhas'][0].update(principal=True, custo=b['linhas'][0].get('custo', 'gratuita'))
    base = dict(build=build, corpo=b['corpo'], recursos=b['recursos'], linhas=b['linhas'],
                planos={"padrao": "auto", "combate_unico": "auto"}, descricao=desc)
    niv = {str(NIV[0]): {"_texto": b.get('_texto', '')}}
    ant = json.loads(json.dumps(dict(corpo=base['corpo'], recursos=base['recursos'], linhas=base['linhas'])))
    for L in NIV[1:]:
        f = fat[L]
        cur = json.loads(json.dumps(dict(corpo=f['corpo'], recursos=f['recursos'], linhas=f['linhas'])))
        niv[str(L)] = dict(_texto=f.get('_texto', ''), **_anula(ant, json.loads(json.dumps(cur))))
        ant = cur
    fonte = {"tipo": "chassi", "url": url or f"https://rpgbot.net/dnd5/characters/classes/{classe}/subclasses/",
             "nota": "Chassi comum (22/11): sem multiclasse, sem raça, a subclasse escolhe posição/equipamento/feat."}
    P = dict(id=id_, nome=f"{sub.replace('-', ' ').title()} {classe.title()} — chassi" + (f" + {feat}" if feat else ''),
             grupo="Chassi", fonte=fonte, classe=classe, subclasse=sub, posicao=posicao, feat=feat,
             variante='feat' if feat else 'sem-feat', base=base, niveis=niv)
    assert posicao in POSICOES, posicao
    with open(OUT + id_ + '.json', 'w') as fh: json.dump(P, fh, ensure_ascii=False, indent=1)
    print('ok', id_)
    return id_
