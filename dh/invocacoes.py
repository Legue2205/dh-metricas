"""Tipos de invocação e quanto cada um conta (24/11, decisão D15).

Cada item de "invocacoes" numa linha pode declarar "tipo"; sem ele, o tipo vem do nome:
  numerosa    — modelo antigo de conjuração (muitas criaturas, muita economia de ação: Conjure Animals / Woodland Beings /
                Minor Elementals / Elemental, Animate Dead e o ciclo de mortos-vivos do necromante)
  summon      — magias "Summon X" (Tasha): uma criatura com bloco que escala com o espaço — já vieram balanceadas
  companheiro — feature de subclasse (Drake, Primal Companion, Steel Defender, Eldritch Cannon, Wildfire Spirit…)

Premissa invocacao.peso.<tipo> (0–1) multiplica a "quantidade" no dano; invocacao.peso_corpo.<tipo> (26/11) no corpo
(PV que atrai ataques) — quando o corpo pesa mais, a criatura entra com o peso do corpo e "peso_dano" desconta o dano; a build pode fixar o seu com
"pesos_invocacao": {"<tipo>": peso} (ex.: personagens da party, que jogam com as criaturas de verdade). Peso 0 tira a criatura; se isso esvazia uma linha que
só existe para invocar (a criatura não está na linha principal), a linha sai do plano e dos anéis.
"""
import re

TIPOS = ('numerosa', 'summon', 'companheiro')
_NUMEROSA = re.compile(r'conjure|animate dead|esqueleto|undead thrall|zumbi', re.I)


def tipo(inv):
    t = inv.get('tipo')
    if t: return t
    nome = inv.get('nome', '')
    if _NUMEROSA.search(nome): return 'numerosa'
    if nome.lower().startswith('summon'): return 'summon'
    return 'companheiro'


def aplicar(b):
    """Aplica os pesos por tipo nas linhas da build (in place). Só lê premissas se a build tiver invocações."""
    linhas = b.get('linhas') or []
    if not any(l.get('invocacoes') for l in linhas): return b
    from .premissas import P
    principal = next((l for l in linhas if l.get('principal')), linhas[0] if linhas else {})
    nomes_principal = {i.get('nome') for i in principal.get('invocacoes') or []}
    for l in linhas:
        invs = l.get('invocacoes') or []
        if not invs: continue
        novas = []
        for i in invs:
            t = tipo(i)
            pb = (b.get('pesos_invocacao') or {}).get(t)
            pd = pb if pb is not None else P(f'invocacao.peso.{t}')
            # 26/11 (usuário): peso do corpo separado do dano — Animate Dead não conta no dano (D15) mas os corpos
            # ainda atraem ataques. A build que fixa pesos_invocacao fixa os dois, salvo pesos_invocacao_corpo.
            pc = (b.get('pesos_invocacao_corpo') or {}).get(t, pb if pb is not None else P(f'invocacao.peso_corpo.{t}'))
            if i.get('corpo', True) is False: pc = pd
            q = max(pd, pc)
            if q <= 0: continue
            if q < 1: i = dict(i, quantidade=i.get('quantidade', 1) * q)
            if pd < q: i = dict(i, peso_dano=pd / q)   # o dano da criatura conta só pd (dano.dpr lê peso_dano)
            novas.append(i)
        if len(novas) == len(invs) and all(n is o for n, o in zip(novas, invs)): continue
        if novas: l['invocacoes'] = novas
        else:
            l.pop('invocacoes')
            if l is not principal and not ({i.get('nome') for i in invs} & nomes_principal):
                l['plano'] = False; l['aneis'] = False
                l['hipotese'] = l.get('hipotese', l['id']) + ' [fora: invocação com peso 0]'
    return b
