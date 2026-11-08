"""Controle total = campo + atenção na moeda "vidas da party poupadas", calibrado contra o conjurador de referência.

Porta de control_total.py e da função total()/absoluto() do patch do Jamal/Virgil, com duas mudanças:
  - a régua (melhor magia do conjurador de referência de nível k, por encontro e topologia) fica em
    cache/regua-<hash>.json, então só é calculada uma vez por versão do motor;
  - avalia UMA linha por vez (não roda todos os personagens de novo).
"""
import hashlib
import json
from pathlib import Path

import numpy as np

from .. import base
from ..base import PESO_TIPO, NIVEIS_TESTE, TOPO, TOPOS, encontro
from . import atencao as A
from . import campo as C

N_REGUA = 8000
CACHE = Path(__file__).resolve().parents[2] / 'cache'


def _hash_motor():
    h = hashlib.sha1()
    for p in (Path(base.__file__), Path(C.__file__), C.ARQ_MAGIAS):
        h.update(p.read_bytes())
    h.update(str(N_REGUA).encode())
    return h.hexdigest()[:10]


class Regua:
    """Vetores de negação da régua, persistidos em disco."""
    def __init__(self):
        self.arq = CACHE / f'regua-{_hash_motor()}.json'
        self.d = json.loads(self.arq.read_text()) if self.arq.exists() else {}
        self.sujo = False

    def vetor(self, tipo, L, ti, k):
        chave = f'{tipo}|{L}|{ti}|{k}'
        if chave not in self.d:
            self._calcula(tipo, L)
        return np.array(self.d[chave])

    def _calcula(self, tipo, L):
        """Calcula a régua inteira de (tipo, L): 3 topologias × k = 1..20, com N fixo."""
        N0, rng0 = C.N, C.rng
        C.configurar(N_REGUA, 11)
        E = encontro(tipo, L)
        horda = [C.magia(n) for n, m in C.MAGIAS.items() if m.get('regua') == 'area']
        unico = [C.magia(n) for n, m in C.MAGIAS.items() if m.get('regua') == 'unico']
        for ti, topo in enumerate(TOPOS):
            for k in range(1, 21):
                cd, sm = CD_REF[k], slot_max(k)
                best = C.sleep(E, topo) if len(E) > 1 else C.zero(E)
                for m in horda:
                    if m['nivel'] <= sm:
                        v = C.area(E, m['alvos'], C.f_area(cd, m), topo, m.get('mult', 'area'))
                        if C.tot(E, v) > C.tot(E, best): best = v
                for m in unico:
                    if m['nivel'] <= sm:
                        sl = tuple(s for s in top4(k) if s >= m['nivel'])
                        v = C.unico(E, lambda c, m=m, sl=sl: C.seq1(C.ckey(c), cd, sl, (C._tupla(m),))[0])
                        if C.tot(E, v) > C.tot(E, best): best = v
                self.d[f'{tipo}|{L}|{ti}|{k}'] = [round(float(x), 5) for x in best]
        C.configurar(N0); C.rng = rng0
        self.sujo = True

    def salva(self):
        if self.sujo:
            CACHE.mkdir(exist_ok=True); self.arq.write_text(json.dumps(self.d)); self.sujo = False


CD_REF = {1: 13, 2: 13, 3: 13, 4: 14, 5: 15, 6: 15, 7: 15, 8: 16, 9: 16, 10: 17, 11: 17, 12: 17,
          13: 18, 14: 18, 15: 18, 16: 18, 17: 19, 18: 19, 19: 19, 20: 19}
SLOTS_CHEIO = {1: [2], 2: [3], 3: [4, 2], 4: [4, 3], 5: [4, 3, 2], 6: [4, 3, 3], 7: [4, 3, 3, 1],
               8: [4, 3, 3, 2], 9: [4, 3, 3, 3, 1], 10: [4, 3, 3, 3, 2], 11: [4, 3, 3, 3, 2, 1],
               12: [4, 3, 3, 3, 2, 1], 13: [4, 3, 3, 3, 2, 1, 1], 14: [4, 3, 3, 3, 2, 1, 1],
               15: [4, 3, 3, 3, 2, 1, 1, 1], 16: [4, 3, 3, 3, 2, 1, 1, 1], 17: [4, 3, 3, 3, 2, 1, 1, 1, 1],
               18: [4, 3, 3, 3, 3, 1, 1, 1, 1], 19: [4, 3, 3, 3, 3, 2, 1, 1, 1], 20: [4, 3, 3, 3, 3, 2, 2, 1, 1]}


def slot_max(k): return min(9, (k + 1) // 2)


def top4(k):
    s = []
    for lv, q in enumerate(SLOTS_CHEIO[k], 1): s += [lv] * q
    return tuple(sorted(s, reverse=True)[:4])


def nivel(g, curva):
    curva = np.maximum.accumulate(np.asarray(curva))
    if g <= curva[0]:
        return max(0.0, (g / curva[0]) if curva[0] > 0 else 0.0)
    if g >= curva[-1]:  # acima do teto: estende com a inclinação média até onde a régua parou de subir
        kp = int(np.argmax(curva >= curva[-1] - 1e-9)) + 1
        return float(min(20.0, kp + (g - curva[-1]) / (curva[-1] / kp)))
    return float(np.interp(g, curva, np.arange(1, 21)))


def avaliar_nivel(fn, ficha, L, regua):
    """Controle total, só campo e só atenção de uma linha num nível L (party e encontros desse nível)."""
    out = {}
    for tipo in PESO_TIPO:
        E = encontro(tipo, L)
        acc = {k: np.zeros(20) if k == 'curva' else 0.0 for k in ('curva', 'total', 'campo', 'aten')}
        fontes7 = {}
        for ti, tp in enumerate(TOPOS):
            w = TOPO[tp]['peso']
            pref = A.party_com(A.ref(ficha['papel'], L), L); px = A.party_com(ficha, L)
            fontes = fn(E, tp); neg = C.jv(*fontes.values())
            base = A.vida(E, pref, ti)
            acc['total'] += w * (base - A.vida(E, px, ti, neg))
            acc['campo'] += w * (base - A.vida(E, pref, ti, neg))
            acc['aten'] += w * (base - A.vida(E, px, ti))
            acc['curva'] += w * np.array([base - A.vida(E, pref, ti, regua.vetor(tipo, L, ti, k)) for k in range(1, 21)])
            if tp == 'Ruínas ou cidade': fontes7 = {k: round(C.tot(E, v), 4) for k, v in fontes.items()}
        out[tipo] = dict(vidas_total=acc['total'], vidas_campo=acc['campo'], vidas_atencao=acc['aten'],
                         nivel_total=nivel(acc['total'], acc['curva']), nivel_campo=nivel(acc['campo'], acc['curva']),
                         nivel_atencao=nivel(acc['aten'], acc['curva']), negacao_por_fonte=fontes7)
    geral = {k: sum(PESO_TIPO[t] * out[t][k] for t in PESO_TIPO)
             for k in ('vidas_total', 'vidas_campo', 'vidas_atencao', 'nivel_total', 'nivel_campo', 'nivel_atencao')}
    return geral, out


def avaliar(fn, ficha, L, absoluto=False, regua=None):
    regua = regua or Regua()
    geral, tipos = avaliar_nivel(fn, ficha, L, regua)
    res = dict(nivel_eq=round(geral['nivel_total'], 2), rank=base.letra(geral['nivel_total']),
               nivel_campo=round(geral['nivel_campo'], 2), rank_campo=base.letra(geral['nivel_campo']),
               nivel_atencao=round(geral['nivel_atencao'], 2), rank_atencao=base.letra(geral['nivel_atencao']),
               vidas_total=round(geral['vidas_total'], 3), vidas_campo=round(geral['vidas_campo'], 3),
               vidas_atencao=round(geral['vidas_atencao'], 3),
               por_tipo={t: round(v['nivel_total'], 2) for t, v in tipos.items()},
               negacao_por_fonte={t: v['negacao_por_fonte'] for t, v in tipos.items()})
    if absoluto:
        niveis = [avaliar_nivel(fn, ficha, t, regua)[0]['nivel_total'] for t in NIVEIS_TESTE]
        res['nivel_absoluto'] = round(float(np.median(niveis)), 2)
        res['rank_absoluto'] = base.letra(res['nivel_absoluto'])
    regua.salva()
    return res
