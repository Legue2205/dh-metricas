"""M1 (23/11): reações mágicas (Counterspell, Absorb Elements) declaradas nas progressões.

O motor cria a linha "reacao-<magia>" a partir de "reacoes_magicas" da build (dh/build.py, tabela _reacoes_magicas do
magias.json); o plano por rendimento (D5/D9) decide quando gastar o espaço nela.

- Chassis: lista RAW da classe/subclasse, com o nível em que a magia fica disponível.
- Builds do RPGBot (e outras): só se o "nao_modelado" cita a magia (o guia a escolheu); a menção sai do "nao_modelado".

Idempotente. Chamado pelo chassi.escrever; para as outras progressões, rode depois de qualquer gerador:
    python ferramentas/geradores/m1_reacoes.py
"""
import json
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
NOMES = {'counterspell': 'Counterspell', 'absorb_elements': 'Absorb Elements'}
# desde = nível de personagem em que a magia entra na lista (RAW 5e 2014)
CLASSE = {
    'counterspell': {'wizard': 5, 'sorcerer': 5, 'warlock': 5, 'fighter/eldritch-knight': 13},
    'absorb_elements': {'wizard': 1, 'sorcerer': 1, 'druid': 1, 'artificer': 1, 'ranger': 2, 'fighter/eldritch-knight': 3},
}


def _classe_sub(prog):
    c, s = prog.get('classe'), prog.get('subclasse')
    if not c:
        m = re.match(r'(?:rpgbot|chassi)-([a-z]+)-(.*)', prog.get('id', ''))
        if m: c, s = m.group(1), m.group(2)
    return c or '', s or ''


def _desde(magia, c, s):
    t = CLASSE[magia]
    if f'{c}/{s}' in t: return t[f'{c}/{s}']
    for k, v in t.items():
        if '/' in k and k.split('/')[0] == c and s.startswith(k.split('/')[1]): return v
    return t.get(c)


def _textos_nm(prog):
    """Todas as strings de nao_modelado (base e patches), com um setter para reescrever."""
    def visita(d):
        if not isinstance(d, dict): return
        desc = d.get('descricao')
        if isinstance(desc, dict) and isinstance(desc.get('nao_modelado'), str):
            yield desc
    yield from visita(prog.get('base', {}))
    for p in prog.get('niveis', {}).values(): yield from visita(p)


def _limpa(txt, nome):
    """Tira do nao_modelado só os itens (separados por ';') que são apenas a magia; o resto fica como está."""
    def so_ela(it):
        r = re.sub(rf'\b{re.escape(nome)}\b', '', it, flags=re.I)
        return not re.sub(r'(como reação|\(reação\)|reação|[\s.,;:()])', '', r, flags=re.I)
    return '; '.join(i.strip() for i in txt.split(';') if i.strip() and not so_ela(i))


def aplicar(prog):
    """Põe "reacoes_magicas" na base da progressão (e limpa o nao_modelado). Devolve True se mudou."""
    c, s = _classe_sub(prog)
    chassi = prog.get('id', '').startswith('chassi-')
    txt = ' '.join(d['nao_modelado'] for d in _textos_nm(prog))
    lista = []
    for m, nome in NOMES.items():
        d = _desde(m, c, s)
        if chassi and d: lista.append({'magia': m, 'desde': d})
        elif not chassi and nome.lower() in txt.lower(): lista.append({'magia': m, 'desde': d or 1})
    antes = json.dumps(prog, sort_keys=True)
    if lista: prog['base']['reacoes_magicas'] = lista
    else: prog['base'].pop('reacoes_magicas', None)
    for r in lista:
        for d in _textos_nm(prog): d['nao_modelado'] = _limpa(d['nao_modelado'], NOMES[r['magia']])
    if lista:
        prog['base'].setdefault('descricao', {})['reacoes_modeladas'] = (
            'Reações modeladas (M1, 23/11): ' + ', '.join(f"{NOMES[r['magia']]} (desde o {r['desde']})" for r in lista)
            + '; o plano decide quando gastar o espaço nelas.')
    return json.dumps(prog, sort_keys=True) != antes


if __name__ == '__main__':
    n = 0
    for p in sorted((RAIZ / 'progressoes').glob('*.json')):
        if p.name.startswith('exemplo'): continue
        prog = json.loads(p.read_text(encoding='utf-8'))
        if aplicar(prog):
            p.write_text(json.dumps(prog, ensure_ascii=False, indent=1) + '\n', encoding='utf-8'); n += 1
    print(f'{n} progressões com reações mágicas atualizadas')
