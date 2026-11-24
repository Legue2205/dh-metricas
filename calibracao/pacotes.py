"""Piloto A3 (24/11): pacotes de otimização dos marciais, aplicados por regra a todo chassi sem feat compatível.

Pergunta: o τ do dano melhora se cada subclasse marcial for medida também com o "pacote clássico" do 2014
(feats de poder em dupla)? O pacote respeita a POSIÇÃO que a subclasse escolheu (não muda o arquétipo):
  - atirador de arco/besta (Fighter, Ranger, Rogue, Paladin)  → CBE + SS: besta de mão (1d6), ataque bônus de 1d6;
    Rogue troca o Steady Aim pelo ataque bônus (vantagem 0).
  - striker/defensor de arma de duas mãos (Fighter, Barbarian, Paladin, Ranger) → PAM + GWM: glaive (1d10; GWF vira
    +0,8 no lugar de +1,33), ataque bônus de 1d4 (GWF +0,5).
  - fica de fora: espada e escudo (defensores que escolheram escudo), Rune Knight (agarrar), Soulknife e Drakewarden
    (ação bônus já usada), Beast (garras), Monk.
Número de feats = ASIs do nível (Fighter 2 no 7 e no 11 — o 3º ASI do 11 fica no atributo; demais 1 no 7 e 2 no 11),
na ordem [CBE, SS] / [PAM, GWM]. Os feats tiram primeiro dos ASIs que tinham ido para o atributo secundário; só depois
do principal (o modificador perdido sai do acerto, do dano fixo e, à distância, da CA).
Frações do ataque bônus (premissas do piloto, só aqui): Barbarian 0,75 (1º round vai na fúria), Ranger 0,9 (Hunter's
Mark), Paladin 0,9, demais 1.

Uso (da raiz): python calibracao/pacotes.py  → escreve builds/pacote-<classe>-<sub>-<pacote>-<nv>.json (grupo "Pacote").
Depois: dh validar → commit (o CI calcula) → python calibracao/teto_subclasse.py (fonte "pacote").
"""
import ast
import glob
import json
import math
import os
import re

RAIZ = os.path.join(os.path.dirname(__file__), '..')
CLASSES = ('fighter', 'barbarian', 'paladin', 'ranger', 'rogue')
FORA = {('fighter', 'rune-knight'), ('rogue', 'soulknife'), ('ranger', 'drakewarden'), ('barbarian', 'beast')}
FRACAO_BONUS = {'barbarian': 0.75, 'ranger': 0.9, 'paladin': 0.9}
NAO_ARMA = re.compile(r'spiritual|bolt|drake|companion|psychic|blast|companheiro|invoca', re.I)


def asis(classe, nv): return (2 if nv >= 6 else 1) + (1 if nv >= 8 else 0) if classe == 'fighter' else (1 if nv < 8 else 2)


def n_feats(classe, nv): return min(2, asis(classe, nv))


def atributos(classe, sub, nv):
    p = json.load(open(os.path.join(RAIZ, 'progressoes', f'chassi-{classe}-{sub}.json'), encoding='utf-8'))
    for k in sorted(p['niveis'], key=int):
        if int(k) <= nv:
            m = re.search(r"atributos (\{[^}]*\})", p['niveis'][k].get('_texto', ''))
            if m: s = ast.literal_eval(m.group(1))
    return s


def mod(x): return (x - 10) // 2


def delta_mod(classe, nv, main, k):
    """Modificador perdido no atributo principal ao trocar k ASIs por feats (os ASIs do secundário saem primeiro)."""
    no_main = math.ceil(max(0, main - 17) / 2)
    do_main = max(0, k - (asis(classe, nv) - no_main))
    return mod(max(17, main - 2 * do_main)) - mod(main)


def pacote_de(b):
    texto = str(b.get('build', '')).lower()
    a0 = (b['linhas'][0].get('dano') or {}).get('ataques') or []
    if not a0: return None
    die = re.match(r'(\d+d\d+)', a0[0]['dano']); die = die.group(1) if die else ''
    if b['posicao'] == 'atirador' and re.search(r'arco|besta|mosquete', texto): return 'cbe-ss'
    if 'escudo' in texto: return None
    if die in ('2d6', '1d12', '1d10') and b['posicao'] in ('striker', 'defensor'): return 'pam-gwm'
    return None


def troca(a, novo, dm, gwf):
    a = dict(a)
    d = re.sub(r'^\d+d\d+', novo, a['dano'])
    d = re.sub(r'^(\d+d\d+)\+(\d+)', lambda m: f"{m.group(1)}+{int(m.group(2)) + dm}", d)
    if gwf: d = d.replace('+1.33', '+0.8')
    a['dano'] = d; a['bonus'] = a['bonus'] + dm
    if 'dados_crit' in a: a['dados_crit'] = f'{novo}+{novo}'
    return a


def aplicar(b, classe, nv, pac):
    s = atributos(classe, b['subclasse'], nv)
    main = s['des'] if pac == 'cbe-ss' else s['for']
    k = n_feats(classe, nv)
    feats = (['Crossbow Expert', 'Sharpshooter'] if pac == 'cbe-ss' else ['Polearm Master', 'Great Weapon Master'])[:k]
    dm = delta_mod(classe, nv, main, k)
    poder = (pac == 'cbe-ss' and 'Sharpshooter' in feats) or (pac == 'pam-gwm' and 'Great Weapon Master' in feats)
    novo, bonus_die = ('1d6', '1d6') if pac == 'cbe-ss' else ('1d10', '1d4')
    gwf = '+1.33' in b['linhas'][0]['dano']['ataques'][0]['dano']
    wb = b['linhas'][0]['dano']['ataques'][0]['bonus']
    b = json.loads(json.dumps(b))
    for l in b['linhas']:
        atq = (l.get('dano') or {}).get('ataques')
        if not atq: continue
        novos, tem_bonus, modelo = [], False, None
        for a in atq:
            if a.get('bonus') == wb and not NAO_ARMA.search(a.get('nota', '')):
                a = troca(a, novo, dm, gwf)
                if poder: a['poder'] = [-5, 10]
                if classe == 'rogue' and isinstance(a.get('vantagem'), dict): a['vantagem'] = 0.0   # Steady Aim (premissa) sai
                if modelo is None and not a.get('round1'): modelo = a
            if re.search(r'ação bônus|flurry of blows', a.get('nota', ''), re.I): tem_bonus = True
            novos.append(a)
        if not tem_bonus and modelo:
            # o ataque bônus herda o que vale por acerto no 1º ataque de arma da linha (fúria, Hunter's Mark, Improved
            # Divine Smite…), trocando só o dado da arma
            extra = {"n": FRACAO_BONUS.get(classe, 1.0), "bonus": modelo['bonus'],
                     "dano": re.sub(r'^\d+d\d+', bonus_die, modelo['dano']).replace('+0.8', '+0.5'),
                     "nota": f"{feats[0]} (ação bônus)"}
            for k in ('poder', 'vantagem', 'dados_crit'):
                if k in modelo: extra[k] = modelo[k] if k != 'dados_crit' else f'{bonus_die}+{bonus_die}'
            novos.append(extra)
        l['dano']['ataques'] = novos
    if pac == 'cbe-ss' and dm:
        b['corpo']['ca'] = b['corpo']['ca'] + dm
    base = b['id'].rsplit('-', 1)[0].replace('chassi-', 'pacote-', 1)
    b.update(id=f'{base}-{pac}-{nv}', nome=f"{b['nome']} — pacote {'+'.join(feats)}", grupo='Pacote',
             feat='+'.join(feats), variante='pacote', gerado_de=None)
    b['descricao'] = dict(b.get('descricao') or {}, pacote=(
        f"Piloto A3 (24/11): chassi sem feat + {'+'.join(feats)} (calibracao/pacotes.py); modificador {dm:+d} no atributo "
        f"principal pelos ASIs trocados; arma {novo} + ataque bônus {bonus_die}."))
    b.pop('gerado_de', None)
    return b


def main():
    feitos = 0
    for f in sorted(glob.glob(os.path.join(RAIZ, 'builds', 'chassi-*.json'))):
        b = json.load(open(f, encoding='utf-8'))
        if b.get('variante') != 'sem-feat' or b['classe'] not in CLASSES or (b['classe'], b['subclasse']) in FORA: continue
        pac = pacote_de(b)
        if not pac: continue
        nv = b['nivel']
        out = aplicar(b, b['classe'], nv, pac)
        open(os.path.join(RAIZ, 'builds', out['id'] + '.json'), 'w', encoding='utf-8').write(
            json.dumps(out, ensure_ascii=False, indent=1) + '\n')
        feitos += 1
    print(feitos, 'builds de pacote')


if __name__ == '__main__':
    main()
