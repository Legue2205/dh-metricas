"""Motor tático: decisão turno a turno de um combatente que alterna esconderijo e linha de frente.

Pergunta que responde: em cada turno, o que fazer? Ficar nas sombras, ficar no corpo a corpo ou fazer a transição?
Modelo (genérico; os parâmetros vêm do bloco "tatico" da build):

ESTADO no início do turno dele: round r, distância x até o alvo, se está num esconderijo (`esc`) e se está escondido
(`hid`), distância H do alvo até o esconderijo mais próximo (sorteada por alvo, conforme a topologia), aliado colado
no alvo (sorteado a cada round), e se ele age antes do alvo (só no round 1: Assassinate / vantagem de iniciativa).

AÇÕES (deslocamento S; Dash dá mais S; o ataque escondido tem vantagem só no 1º golpe; Sneak Attack 1×/turno num
golpe com vantagem ou com aliado colado; arremesso só até o alcance normal):
  melee_lurker   vai até o alvo, ataca, volta ao esconderijo e se esconde (x + H ≤ S)
  melee_dasher   vai, ataca, Dash para longe (para no esconderijo se alcançar, mas exposto)
  frontline      vai (ou Dash e vai) e fica colado; vantagem por Steady Aim (sem andar) ou escondendo-se no início
  thrower_lurker sai do esconderijo até o alcance normal, arremessa, volta e se esconde
  thrower_dasher vai até o alcance normal, arremessa, Dash para longe
  ranged_lurker  dispara de dentro do esconderijo e se esconde de novo
  sniper         Steady Aim + disparo, sem andar, exposto
  reposicionar   anda/Dash até o esconderijo do alvo e se esconde (sem atacar)
  aproximar      Dash duplo em direção ao alvo, sem atacar
DANO de cada ação: dh.dano.dpr (mesmas fórmulas do eixo de dano).
EXPOSIÇÃO: dano recebido no turno inimigo depois do dele = fração do dano inimigo da régua (escondido, exposto à
distância ou colado no alvo), conforme a COMPOSIÇÃO da party (3 cenários em COMPOSICOES).
OBJETIVO: dano causado − custo do PV perdido. Custo convexo pelo orçamento de PV por luta ((pv + recuperação)/lutas):
dentro dele 1 PV vale w (razão de piscinas: w > 1 quando os inimigos têm mais vida que a party, como hordas e dragões),
acima vale w × excesso, e cair custa "queda". O PV já perdido na luta faz parte do estado: quem ficou escondido tem
orçamento sobrando e pode ir para a frente depois (o "luxo").
ALVO: morre (troca) com prob. (dano dele + dano dos aliados no alvo) / PV do alvo; o novo alvo tem nova distância e
novo esconderijo; ele mantém o estado de escondido.
Saída: dano por round, dano recebido por luta, % de cada ação (rounds 1 e 2–4 separados) por topologia.
"""
import random
from functools import lru_cache

from . import dano as D
from .base import TOPO

PADRAO_ANTIGO = dict(
    deslocamento=30, rounds=4, ca=15,     # "ataques" (melee, arremesso, distancia) e "sneak" vêm da build
    steady_aim=True, p_agir_antes=0.7, p_comeca_escondido=0.3,
    p_aliado={'r1': 0.2, 'depois': 0.7},
    dano_inimigo_round=54.5,                       # régua de suporte, nível 7 (dano inimigo por round contra a party)
    composicao='segundo_frontliner', reducao_exposto=1.0,   # reducao_exposto: Uncanny Dodge etc. (fator < 1)
    # Orçamento de PV: (pv + recuperação do dia) / lutas. Dentro do orçamento, 1 PV custa w; acima, w × excesso;
    # cair (PV acumulado ≥ pv) custa o valor de "queda". Isto dá o "luxo": quem ficou escondido pode ir para a frente.
    pv=50, recuperacao_dia=20, lutas_dia=4, excesso=3.0, queda=60,
    alvo={'pv': 60, 'dano_aliados_colado': 25, 'dano_aliados_longe': 12},
    topologias={
        'Sala de dungeon': {'esconderijo': {15: 0.6, 30: 0.3, 50: 0.1}, 'inicial': {30: 0.5, 50: 0.5}, 'proximo': {10: 0.4, 25: 0.4, 45: 0.2}},
        'Ruínas ou cidade': {'esconderijo': {15: 0.4, 30: 0.4, 50: 0.2}, 'inicial': {40: 0.5, 70: 0.5}, 'proximo': {15: 0.3, 30: 0.4, 50: 0.3}},
        'Campo aberto': {'esconderijo': {15: 0.15, 30: 0.35, 50: 0.5}, 'inicial': {60: 0.5, 100: 0.5}, 'proximo': {20: 0.3, 40: 0.4, 60: 0.3}},
    })

# Fração do dano inimigo por round que vai para ele, por situação no fim do turno e composição da party.
COMPOSICOES_ANTIGO = {
    'terceiro_melee':     dict(escondido=0.04, longe=0.10, colado=0.20, nota='tanque + outro corpo a corpo na frente + ele + 1 de trás'),
    'segundo_frontliner': dict(escondido=0.05, longe=0.15, colado=0.32, nota='tanque + ele na frente + 2 de trás'),
    'sem_tanque':         dict(escondido=0.06, longe=0.20, colado=0.45, nota='ele é o único corpo a corpo'),
}

from .premissas import valor as _p
PADRAO = _p('tatico.padrao')            # premissas (os *_ANTIGO acima só como referência)
COMPOSICOES = _p('tatico.composicoes')

POLITICAS = {
    'otima': None,
    'sombras': {'melee_lurker', 'thrower_lurker', 'ranged_lurker', 'reposicionar', 'aproximar'},
    'frontline': {'frontline', 'aproximar'},
}
NOMES = dict(melee_lurker='Melee Lurker', melee_dasher='Melee Dasher', frontline='Frontline',
             thrower_lurker='Thrower Lurker', thrower_dasher='Thrower Dasher', ranged_lurker='Ranged Lurker',
             sniper='Sniper', reposicionar='Reposicionar e esconder', aproximar='Aproximar (Dash)')


def _cfg(spec):
    c = {k: (dict(v) if isinstance(v, dict) else v) for k, v in PADRAO.items()}
    for k, v in (spec or {}).items(): c[k] = v
    c['topologias'] = {t: {kk: {int(a): b for a, b in vv.items()} for kk, vv in d.items()} for t, d in c['topologias'].items()}
    return c


def _q5(x): return int(min(120, max(0, 5 * round(x / 5))))


class Modelo:
    def __init__(self, spec=None, ca=None):
        self.c = _cfg(spec)
        if 'ataques' not in self.c: raise ValueError('tatico: declare "ataques" (melee, arremesso, distancia)')
        self.c.setdefault('sneak', '0'); self.ca = ca or self.c['ca']; self.S = self.c['deslocamento']

    # ---------- dano de uma ação (motor de dano) ----------
    @lru_cache(maxsize=None)
    def golpes(self, arma, n, adv, aliado, adv_todos=False):
        a = self.c['ataques'][arma]; n = min(n, a['n']) if n else a['n']
        atk = lambda v: {'n': 1, 'bonus': a['bonus'], 'dano': a['dano'], 'vantagem': v}
        sa = [{'dano': self.c['sneak']}] if self.c['sneak'] not in ('0', 0, None) else []
        if adv_todos: return D.dpr({'ataques': [atk(1)] * n, 'por_turno': sa}, self.ca)
        if aliado: return D.dpr({'ataques': [atk(1 if adv else 0)] + [atk(0)] * (n - 1), 'por_turno': sa}, self.ca)
        if adv: return D.dpr({'ataques': [atk(1)], 'por_turno': sa}, self.ca) + (D.dpr({'ataques': [atk(0)] * (n - 1)}, self.ca) if n > 1 else 0)
        return D.dpr({'ataques': [atk(0)] * n}, self.ca)

    # ---------- ações possíveis num estado ----------
    def acoes(self, x, esc, hid, H, aliado, antes):
        S = self.S; out = []
        at = self.c['ataques']; rng_t = at['arremesso']['alcance']; rng_d = at['distancia']['alcance']
        adv = hid
        def g(arma, adv_, n=None): return self.golpes(arma, n, adv_, aliado, antes)
        if x + H <= S:
            out.append(('melee_lurker', g('melee', adv), dict(x=H, esc=True, hid=True), 'escondido'))
        if x <= S:
            sobra = 2 * S - x
            fim = dict(x=H, esc=True, hid=False) if H <= sobra else dict(x=_q5(min(sobra, 60)), esc=False, hid=False)
            out.append(('melee_dasher', g('melee', adv), fim, 'longe'))
        if x <= 2 * S:                                     # frontline: fica colado
            vant = adv or (x == 0 and self.c['steady_aim']) or (esc and not hid and x <= S)
            if x > S: vant = adv                          # precisou do Dash: sem Steady Aim nem Hide
            out.append(('frontline', g('melee', vant), dict(x=0, esc=False, hid=False), 'colado'))
        if esc and x > 0 and 2 * max(0, x - rng_t) <= S:
            out.append(('thrower_lurker', g('arremesso', adv), dict(x=x, esc=True, hid=True), 'escondido'))
        m = max(0, x - rng_t)
        if x > 0 and m <= S:
            sobra = 2 * S - m; d_esc = abs(min(x, rng_t) - H)
            fim = dict(x=H, esc=True, hid=False) if d_esc <= sobra else dict(x=_q5(min(rng_t + sobra, 60)), esc=False, hid=False)
            out.append(('thrower_dasher', g('arremesso', adv), fim, 'longe'))
        if esc and 0 < x <= rng_d:
            out.append(('ranged_lurker', g('distancia', adv), dict(x=x, esc=True, hid=True), 'escondido'))
        if x > 0 and x <= rng_d and self.c['steady_aim']:
            out.append(('sniper', g('distancia', True), dict(x=x, esc=esc, hid=False), 'longe'))
        if abs(x - H) <= 2 * S:
            out.append(('reposicionar', 0.0, dict(x=H, esc=True, hid=True), 'escondido'))
        if x > 2 * S or not out:
            out.append(('aproximar', 0.0, dict(x=_q5(max(0, x - 2 * S)), esc=False, hid=False), 'longe'))
        return out

    def recebido(self, exp):
        expo = self.c.get('exposicao') or COMPOSICOES[self.c['composicao']]
        f = expo[exp] * self.c['dano_inimigo_round']
        return f if exp == 'escondido' else f * self.c['reducao_exposto']

    def orcamento(self):
        return (self.c['pv'] + self.c['recuperacao_dia']) / self.c['lutas_dia']

    def custo(self, g, w):
        """Custo acumulado de ter perdido g PV na luta."""
        B = self.orcamento(); c = w * min(g, B) + w * self.c['excesso'] * max(0.0, g - B)
        return c + (self.c['queda'] if g >= self.c['pv'] else 0.0)

    def p_troca(self, dano, aliado):
        a = self.c['alvo']; return min(0.9, (dano + (a['dano_aliados_colado'] if aliado else a['dano_aliados_longe'])) / a['pv'])

    # ---------- programação dinâmica ----------
    def resolver(self, topo, w=1.0, politica='otima'):
        T = self.c['topologias'][topo]; R = self.c['rounds']; perm = POLITICAS[politica]
        pa = self.c['p_aliado']

        qg = lambda g: round(g * 2) / 2              # PV perdido, em passos de 0,5

        @lru_cache(maxsize=None)
        def V(r, x, esc, hid, H, g):     # valor esperado antes de sortear o aliado do round r (r ≥ 2)
            if r > R: return 0.0
            p = pa['depois']
            return p * Q(r, x, esc, hid, H, True, False, g)[0] + (1 - p) * Q(r, x, esc, hid, H, False, False, g)[0]

        @lru_cache(maxsize=None)
        def Q(r, x, esc, hid, H, aliado, antes, g=0.0):
            best = None
            for nome, dmg, fim, exp in self.acoes(x, esc, hid, H, aliado, antes):
                if perm is not None and nome not in perm: continue
                L = self.recebido(exp); g2 = qg(g + L)
                v = dmg - (self.custo(g2, w) - self.custo(g, w))
                pt = self.p_troca(dmg, aliado)
                cont = (1 - pt) * V(r + 1, fim['x'], fim['esc'], fim['hid'], H, g2)
                if pt > 0 and r < R:
                    for xn, px in T['proximo'].items():
                        for Hn, ph in T['esconderijo'].items():
                            cont += pt * px * ph * V(r + 1, xn, fim['esc'], fim['hid'], Hn, g2)
                v += cont
                if best is None or v > best[0]: best = (v, nome, dmg, fim, exp, pt)
            return best
        return Q

    # ---------- simulação da política ----------
    def simular(self, topo, w=1.0, politica='otima', n=20000, semente=7, cas=None):
        Q = self.resolver(topo, w, politica); T = self.c['topologias'][topo]; R = self.c['rounds']; pa = self.c['p_aliado']
        rnd = random.Random(semente)
        def sorteia(d):
            u = rnd.random(); acc = 0
            for k, p in d.items():
                acc += p
                if u <= acc: return k
            return k
        cont = {'r1': {}, 'r2_4': {}}; dano_t = rec_t = 0.0; escondido_fim = 0; colado_fim = 0; acima = 0
        outros = {ca: 0.0 for ca in (cas or [])}; modelos = {ca: Modelo(self._spec_bruto(), ca) for ca in outros}
        for _ in range(n):
            x = sorteia(T['inicial']); H = sorteia(T['esconderijo'])
            hid = rnd.random() < self.c['p_comeca_escondido']; esc = hid; g = 0.0
            for r in range(1, R + 1):
                aliado = rnd.random() < (pa['r1'] if r == 1 else pa['depois'])
                antes = r == 1 and rnd.random() < self.c['p_agir_antes']
                _, nome, dmg, fim, exp, pt = Q(r, x, esc, hid, H, aliado, antes, round(g * 2) / 2)
                g += self.recebido(exp)
                k = 'r1' if r == 1 else 'r2_4'; cont[k][nome] = cont[k].get(nome, 0) + 1
                dano_t += dmg; rec_t += self.recebido(exp); escondido_fim += fim['hid']; colado_fim += exp == 'colado'
                for ca, m in modelos.items():
                    outros[ca] += next((d for nm, d, *_ in m.acoes(x, esc, hid, H, aliado, antes) if nm == nome), 0.0)
                x, esc, hid = fim['x'], fim['esc'], fim['hid']
                if rnd.random() < pt: x = sorteia(T['proximo']); H = sorteia(T['esconderijo'])
            acima += g > self.orcamento()
        pct = lambda d: {NOMES[k]: round(100 * v / sum(d.values()), 1) for k, v in sorted(d.items(), key=lambda kv: -kv[1])}
        return dict(dpr=round(dano_t / (n * R), 1), recebido_luta=round(rec_t / n, 1),
                    escondido_fim_turno=round(100 * escondido_fim / (n * R), 1),
                    lutas_acima_do_orcamento=round(100 * acima / n, 1), colado_fim_turno=round(100 * colado_fim / (n * R), 1),
                    acoes_r1=pct(cont['r1']), acoes_r2_4=pct(cont['r2_4']),
                    dpr_por_ca={f'CA {ca}': round(v / (n * R), 1) for ca, v in outros.items()})

    def _spec_bruto(self):
        return {k: v for k, v in self.c.items() if k != 'topologias'} | {'topologias': {t: {kk: {str(a): b for a, b in vv.items()} for kk, vv in d.items()} for t, d in self.c['topologias'].items()}}


def avaliar(spec, w=1.0, politicas=('otima', 'sombras', 'frontline'), n=20000, cas=None, composicao=None):
    """{politica: {topologia: simulação, 'media': médias ponderadas pelo peso da topologia}}."""
    if composicao: spec = dict(spec, composicao=composicao)
    m = Modelo(spec); out = {}
    for pol in politicas:
        res = {t: m.simular(t, w, pol, n, cas=cas) for t in m.c['topologias']}
        pesos = {t: TOPO[t]['peso'] for t in res}; tot = sum(pesos.values())
        media = {k: round(sum(pesos[t] * res[t][k] for t in res) / tot, 1)
                 for k in ('dpr', 'recebido_luta', 'escondido_fim_turno', 'lutas_acima_do_orcamento', 'colado_fim_turno')}
        if cas: media['dpr_por_ca'] = {k: round(sum(pesos[t] * res[t]['dpr_por_ca'][k] for t in res) / tot, 1) for k in res[next(iter(pesos))]['dpr_por_ca']}
        res['media'] = media; out[pol] = res
    return out


# Posição da party de referência que cada composição ocupa (motor de atenção):
#   terceiro_melee: ele ocupa o lugar do atirador, mas pode ir para a frente (o striker de referência continua lá);
#   segundo_frontliner: o lugar do striker; sem_tanque: o lugar do tanque (teste de estresse).
PAPEL = {'terceiro_melee': 'atirador', 'segundo_frontliner': 'striker', 'sem_tanque': 'tank'}


def linha(spec_build, spec_linha, cas):
    """Bloco "tatico" de uma linha -> (dano medido nas CAs, atenção para o controle de corpo, resumo)."""
    comp = spec_linha.get('composicao', spec_build.get('composicao', PADRAO['composicao']))
    pol = spec_linha.get('politica', 'otima')
    r = avaliar(spec_build, w=spec_linha.get('w', 1.0), politicas=(pol,), n=spec_linha.get('n', 6000), cas=cas,
                composicao=comp)[pol]
    m = r['media']
    aten = dict(papel=PAPEL[comp], front=round(m['colado_fim_turno'] / 100, 3), oculto=round(m['escondido_fim_turno'] / 100, 3),
                dpr=m['dpr'], soft=spec_linha.get('soft', 0.15), acc_m=[0.7, 0.8, 1.0])
    resumo = dict(politica=pol, composicao=comp, **{k: v for k, v in m.items() if k != 'dpr_por_ca'},
                  acoes={t: dict(r1=v['acoes_r1'], r2_4=v['acoes_r2_4']) for t, v in r.items() if t != 'media'})
    return [m['dpr_por_ca'][f'CA {ca}'] for ca in cas], aten, resumo
