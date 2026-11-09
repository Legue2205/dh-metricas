"""Onde cada resultado vai nas planilhas de rank (só colunas de VALOR; as de fórmula ficam intocadas).

Uso pelo Claude (poucos tokens):
  1. python -m dh linhas builds/<id>.json --json   -> lista de {planilha, aba, chave, celulas}
  2. Para cada item: get_values só na coluna-chave da aba (ex.: 'Personagens!T2:T200' e a de hipótese)
     para achar a linha; se existir, update_values célula a célula (ou por blocos contíguos);
     se não existir, append_values numa linha nova com as mesmas colunas.
"""
from .base import PESO_TIPO

PLANILHAS = {
    'dano': '19yFTkRxlr6IYswuMrXpY0tD1OQu0SFhLWv-ztYwh0Ys',
    'defesa': '13YWdMVb1_H4xU647JK-J6S8sxkPJgPWAsenrPdo1Zn0',
    'controle': '1BZqiMKf6t08iX_QE_kMqsWjnf1vFZFWwQvLa3WS3sVU',
    'area': '1LgPV3haDGmqDJhuTkrOmQF3fU9mWyrQ_g4Jf53tDw2M',
    'suporte': '1Ry83Cdexf0revKWTKG2VABbtTArjNN3qh5OX2B625MM',
    'central': '1u64I_OfITW0E3V_cEVVELCUzdSnr0mFF94yZN5fJGL0',
}
# coluna de ID e coluna de hipótese/rótulo usadas para achar a linha certa
CHAVES = {'dano': ('Personagens', 'T', 'D'), 'defesa': ('Personagens', 'P', 'D'), 'controle': ('Controle total', 'V', 'A')}


def _col(i): return chr(ord('A') + i)


def itens(b, res):
    out = []
    for lid, l in res['linhas'].items():
        sim = lambda e: 'Sim' if e in l['principal'] else 'Não'
        rotulo = b['nome'] if lid == 'principal' else f"{b['nome']} ({l['hipotese'][:40]})"
        if 'dano' in l:
            vals = [b['nome'], b['grupo'], b.get('build', ''), l['hipotese'], *l['dano']['dpr'].values()]
            cel = {_col(i): v for i, v in enumerate(vals)}; cel.update(S=sim('dano'), T=b['id'])
            out.append(dict(eixo='dano', planilha=PLANILHAS['dano'], aba='Personagens', id=b['id'], hipotese=l['hipotese'], celulas=cel))
        if 'defesa' in l:
            d = l['defesa']
            cel = dict(A=b['nome'], B=b['grupo'], C=b.get('build', ''), D=l['hipotese'], E=d['pv_efetivo'], F=d['ca'],
                       G=d['blindagem'], H=d['durabilidade'], O=sim('defesa'), P=b['id'])
            out.append(dict(eixo='defesa', planilha=PLANILHAS['defesa'], aba='Personagens', id=b['id'], hipotese=l['hipotese'], celulas=cel))
        if 'controle' in l:
            c = l['controle']
            cel = dict(A=rotulo, B=b['grupo'], C=sim('controle'), D=b['nivel'])
            cel.update({_col(4 + i): round(c['por_tipo'][t], 2) for i, t in enumerate(PESO_TIPO)})
            cel.update(M=round(c['nivel_campo'], 2), O=round(c['nivel_atencao'], 2), Q=c['vidas_total'],
                       R=c['vidas_campo'], S=c['vidas_atencao'], V=b['id'])
            if 'nivel_absoluto' in c: cel['W'] = c['nivel_absoluto']
            out.append(dict(eixo='controle', planilha=PLANILHAS['controle'], aba='Controle total', id=b['id'], hipotese=rotulo, celulas=cel))
    return out
