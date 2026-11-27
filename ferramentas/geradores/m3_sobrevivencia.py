"""M3 (23/11): sobrevivência marcial como "patches_linhas" nas progressões (o resolver aplica em todas as linhas).

- Fighter: Second Wind (1d10 + nível, 1 por descanso curto ≈ 2 por dia → 0,5 por luta) → defesa.cura_luta;
  Indomitable (9: 1, 13: 2, 17: 3 por descanso longo ÷ 4 lutas) → saves.rerolagens.
- Barbarian 11+: Relentless Rage (cai a 1 PV com save de Con CD 10, 15, 20…) ≈ 1,5 golpe extra depois de zerar o PV,
  só nas linhas que gastam fúria → defesa.golpes_extras_a_0pv.

Valem por nível: o patch vai em cada fatia ("niveis"), não na base. Idempotente; ligado ao chassi.escrever e ao
marcial.escrever; para os outros geradores, rode depois deles: python ferramentas/geradores/m3_sobrevivencia.py
"""
import json
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
ORIGENS = ('Second Wind', 'Indomitable', 'Relentless Rage', 'Divine Allegiance', 'Aura of the Guardian', 'Protective Bond')
# D13 (24/11): puxar para si o dano mirado num aliado = taunt forte no corpo (controle.atencao.redireciona; premissas
# controle.atencao.redireciona.*: fração dos turnos contra aliados que passa para a build). (classe, sub): (nível, origem, premissa)
REDIRECIONA = {('paladin', 'crown'): (7, 'Divine Allegiance', 'adjacente'),
               ('paladin', 'redemption'): (7, 'Aura of the Guardian', 'aura'),
               ('cleric', 'peace'): (6, 'Protective Bond', 'aura')}
# 26/11 (G2): no Protective Bond quem teleporta e leva o dano é o aliado ligado mais resistente, não necessariamente o clérigo
PARA_RESISTENTE = {'Protective Bond'}


def _classe(prog):
    if prog.get('classe'): return prog['classe']
    m = re.match(r'(?:rpgbot|chassi)-([a-z]+)-', prog.get('id', ''))
    return m.group(1) if m else ''


def _sub(prog):
    if prog.get('subclasse'): return prog['subclasse']
    c = _classe(prog)
    for (cl, sb) in REDIRECIONA:
        if cl == c and re.match(rf'(?:rpgbot|chassi)-{cl}-{sb}(?:-|$)', prog.get('id', '')): return sb
    return ''


def patches(classe, L, sub=''):
    out = []
    r = REDIRECIONA.get((classe, sub))
    if r and L >= r[0]:
        at = {"redireciona": {"$p": f"controle.atencao.redireciona.{r[2]}"}}
        if r[1] in PARA_RESISTENTE: at["redireciona_para"] = "mais_resistente"
        out.append({"origem": r[1], "eixos": {"controle": {"atencao": at}}})
    if classe == 'fighter':
        out.append({"origem": "Second Wind", "eixos": {"defesa": {"cura_luta": round(0.5 * (5.5 + L), 2)}}})
        if L >= 9:
            n = 1 if L < 13 else 2 if L < 17 else 3
            out.append({"origem": "Indomitable", "eixos": {"saves": {"rerolagens": round(n / 4, 3)}}})
    if classe == 'barbarian' and L >= 11:
        out.append({"origem": "Relentless Rage", "quando_gasta": "furia", "eixos": {"defesa": {"golpes_extras_a_0pv": 1.5}}})
    return out


def _so_ela(item):
    r = item
    for o in ORIGENS: r = re.sub(rf'\b{re.escape(o)}\b', '', r, flags=re.I)
    return not re.sub(r'[\s.,;:()]', '', r)


def aplicar(prog):
    c = _classe(prog); sb = _sub(prog); antes = json.dumps(prog, sort_keys=True)
    for nv, patch in prog.get('niveis', {}).items():
        # 27/11 (pacote C): patches de outras origens (features de subclasse escritas pelo gerador) ficam
        outros = [x for x in patch.get('patches_linhas', []) if x.get('origem') not in ORIGENS]
        ps = outros + patches(c, int(nv), sb)
        if ps: patch['patches_linhas'] = ps
        else: patch.pop('patches_linhas', None)
    if c in ('fighter', 'barbarian') or (c, sb) in REDIRECIONA:
        for d in [prog.get('base', {})] + list(prog.get('niveis', {}).values()):
            desc = d.get('descricao') if isinstance(d, dict) else None
            if isinstance(desc, dict) and isinstance(desc.get('nao_modelado'), str):
                desc['nao_modelado'] = '; '.join(i.strip() for i in desc['nao_modelado'].split(';') if i.strip() and not _so_ela(i))
    return json.dumps(prog, sort_keys=True) != antes


if __name__ == '__main__':
    n = 0
    for p in sorted((RAIZ / 'progressoes').glob('*.json')):
        if p.name.startswith('exemplo'): continue
        prog = json.loads(p.read_text(encoding='utf-8'))
        if aplicar(prog):
            p.write_text(json.dumps(prog, ensure_ascii=False, indent=1) + '\n', encoding='utf-8'); n += 1
    print(f'{n} progressões com sobrevivência marcial atualizadas')
