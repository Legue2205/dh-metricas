"""Motor de saves v2 — DragonHeist. Resiliência (For/Des/Con) e Vontade (Int/Sab/Car).

Monte Carlo, 4 rounds, foco total, um conjurador pleno de nível L contra o personagem.

Conjurador:
- Slots reais da tabela de conjurador pleno; a cada round usa o slot mais alto que sobrou
  e sorteia uma magia daquele nível. Sem slot: cantrip (Mind Sliver / Frostbite).
- Uma concentração por vez. Com concentração ativa, só sorteia magias sem concentração
  (do nível do slot ou abaixo); se não houver, usa o cantrip e guarda o slot.
- Magias de concentração "de ação" (Eyebite, Dragon's Breath) ocupam a ação dele todo round.
- Não quebra um controle que acaba com dano (sono, Hypnotic Pattern, Dominate): fica parado.
- Counterspell do alvo anula a magia (automático até 3º nível; acima, teste).

Alvo: turnos livres = 4 − turnos perdidos. 0 PV perde todos os turnos seguintes.
"""
import numpy as np
from dataclasses import dataclass

rng = np.random.default_rng(11)
N = 6000
R = 4
ELEM = {"fogo", "frio", "eletrico", "trovao", "acido"}
SLOTS = {1: [2], 3: [4, 2], 4: [4, 3], 5: [4, 3, 2], 7: [4, 3, 3, 1], 8: [4, 3, 3, 2],
         10: [4, 3, 3, 3, 2], 11: [4, 3, 3, 3, 2, 1], 13: [4, 3, 3, 3, 2, 1, 1], 16: [4, 3, 3, 3, 2, 1, 1, 1]}
TESTES = [1, 3, 4, 5, 7, 8, 10, 11, 13, 16]


def M(nome, nivel, save, **k):
    k.update(nome=nome, nivel=nivel, save=save)
    return k


# tipo de efeito (ef):
#  None       só dano
#  'turno'    perde este turno (Command, Psychic Lance)
#  'fim'      dura até passar no save do fim do turno (peso w)
#  'luta'     resto da luta (peso w)
#  'sono'     resto da luta, acaba com dano (o conjurador não ataca)
#  'contido'  peso w até escapar (teste de For/Des no fim do turno)
# conc=True: concentração. area=True: efeito se repete todo round enquanto ele concentra.
# acao=True: a magia ocupa a ação do conjurador todo round (Eyebite, Dragon's Breath).
MENTAIS = [
    M("Sleep", 1, None, sono_hp=(5, 8), ef="sono", w=1, sono=True),
    M("Tasha's Hideous Laughter", 1, "sab", ef="fim", w=1, conc=True),
    M("Command", 1, "sab", ef="turno", w=1),
    M("Hold Person", 2, "sab", ef="fim", w=1, conc=True, humanoide=True),
    M("Phantasmal Force", 2, "int", ef="fim", w=1, conc=True, tick=(1, 6, "psiquico")),
    M("Suggestion", 2, "sab", ef="luta", w=1, conc=True, encanto=True, stillness=True),
    M("Slow", 3, "sab", ef="fim", w="slow", conc=True),
    M("Fear", 3, "sab", ef="fim", w=1, conc=True, medo=True, stillness=True),
    M("Hypnotic Pattern", 3, "sab", ef="sono", w=1, conc=True, encanto=True),
    M("Banishment", 4, "car", ef="luta", w=1, conc=True),
    M("Polymorph", 4, "sab", ef="luta", w=1, conc=True),
    M("Raulothim's Psychic Lance", 4, "int", dano=(7, 6, 0), tipo="psiquico", metade=True, ef="turno", w=1),
    M("Dominate Person", 5, "sab", ef="sono", w=1, conc=True, humanoide=True, encanto=True, stillness=True),
    M("Synaptic Static", 5, "int", dano=(8, 6, 0), tipo="psiquico", metade=True, ef="fim", w=0.2),
    M("Modify Memory", 5, "sab", ef="sono", w=1, conc=True, encanto=True, vant_save=True),
    M("Mass Suggestion", 6, "sab", ef="luta", w=1, encanto=True, stillness=True),
    M("Eyebite (dormir)", 6, "sab", ef="sono", w=1, conc=True, acao=True, sono=True),
    M("Mental Prison", 6, "int", dano=(5, 10, 0), tipo="psiquico", nada_no_sucesso=True, ef="luta", w=0.5, conc=True),
    M("Divine Word", 7, "car", limiar=True),
    M("Plane Shift (ofensivo)", 7, "car", ataque=True, ef="luta", w=1),
    M("Symbol (atordoamento)", 7, "sab", ef="luta", w=1),
    M("Feeblemind", 8, "int", dano=(4, 6, 0), tipo="psiquico", sempre_dano=True, ef="luta", w=0.3, w_conj=1),
    M("Antipathy (medo)", 8, "sab", ef="fim", w=1, medo=True, stillness=True),
    M("Maddening Darkness", 8, "sab", dano=(8, 8, 0), tipo="psiquico", metade=True, conc=True, area=True),
]
CANTRIPS_MENTAIS = [M("Mind Sliver", 0, "int", dano=("cantrip", 6, 0), tipo="psiquico", nada_no_sucesso=True, sliver=True),
                    M("Vicious Mockery", 0, "sab", dano=("cantrip", 4, 0), tipo="psiquico", nada_no_sucesso=True, ef="turno", w="mockery")]

FISICAS = [
    M("Burning Hands", 1, "des", dano=(3, 6, 0), tipo="fogo", metade=True),
    M("Thunderwave", 1, "con", dano=(2, 8, 0), tipo="trovao", metade=True),
    M("Entangle", 1, "for", ef="contido", w=0.5, conc=True, escape="for"),
    M("Dragon's Breath", 2, "des", dano=(3, 6, 0), tipo="dragao", metade=True, conc=True, acao=True),
    M("Shatter", 2, "con", dano=(3, 8, 0), tipo="trovao", metade=True),
    M("Web", 2, "des", ef="contido", w=0.5, conc=True, area=True, escape="for"),
    M("Fireball", 3, "des", dano=(8, 6, 0), tipo="fogo", metade=True),
    M("Lightning Bolt", 3, "des", dano=(8, 6, 0), tipo="eletrico", metade=True),
    M("Hunger of Hadar", 3, "des", dano=(2, 6, 0), tipo="acido", nada_no_sucesso=True, auto=(2, 6, "frio"),
      ef="area_peso", w=0.5, conc=True, area=True),
    M("Evard's Black Tentacles", 4, "des", dano=(3, 6, 0), tipo="fisico", nada_no_sucesso=True, ef="contido", w=0.75,
      conc=True, area=True, tick=(3, 6, "fisico"), escape="forte"),
    M("Wall of Fire (de pé nela)", 4, "des", dano=(5, 8, 0), tipo="fogo", metade=True, conc=True, area=True),
    M("Ice Storm", 4, "des", dano=(2, 8, 0), tipo="fisico", metade=True, extra=(4, 6, "frio")),
    M("Watery Sphere", 4, "for", ef="contido", w=0.75, conc=True, escape="for"),
    M("Cloudkill", 5, "con", dano=(5, 8, 0), tipo="veneno", metade=True, conc=True, area=True),
    M("Cone of Cold", 5, "con", dano=(8, 8, 0), tipo="frio", metade=True),
    M("Wall of Light", 5, "con", dano=(4, 8, 0), tipo="radiante", metade=True, ef="fim", w=0.3, conc=True),
    M("Chain Lightning", 6, "des", dano=(10, 8, 0), tipo="eletrico", metade=True),
    M("Disintegrate", 6, "des", dano=(10, 6, 40), tipo="forca", nada_no_sucesso=True),
    M("Circle of Death", 6, "con", dano=(8, 6, 0), tipo="necrotico", metade=True),
    M("Delayed Blast Fireball", 7, "des", dano=(12, 6, 0), tipo="fogo", metade=True),
    M("Finger of Death", 7, "con", dano=(7, 8, 30), tipo="necrotico", metade=True),
    M("Prismatic Spray", 7, "des", dano=(10, 6, 0), tipo="prisma", metade=True),
    M("Whirlwind", 7, "des", dano=(10, 6, 0), tipo="fisico", metade=True, ef="contido", w=0.5, conc=True, area=True,
      escape="for"),
    M("Sunburst", 8, "con", dano=(12, 6, 0), tipo="radiante", metade=True, ef="fim", w=0.3),
    M("Incendiary Cloud", 8, "des", dano=(10, 8, 0), tipo="fogo", metade=True, conc=True, area=True),
    M("Abi-Dalzim's Horrid Wilting", 8, "con", dano=(12, 8, 0), tipo="necrotico", metade=True),
]
CANTRIPS_FISICOS = [M("Frostbite", 0, "con", dano=("cantrip", 6, 0), tipo="frio", nada_no_sucesso=True),
                    M("Sacred Flame", 0, "des", dano=("cantrip", 8, 0), tipo="radiante", nada_no_sucesso=True)]


@dataclass
class S:
    nome: str
    pv: float
    ca: float
    sv: dict
    adv: tuple = ()
    evasion: bool = False
    res: tuple = ()
    imune: tuple = ()             # 'encanto', 'medo', 'sono', 'veneno'
    adv_encanto: bool = False     # Fey Ancestry
    adv_mental_magia: bool = False
    humanoide: bool = True
    conjurador: bool = False
    barrado: int = 0
    absorb: int = 0
    contra: int = 0
    contra_mod: int = 0
    contra_nivel: int = 3          # nível do slot usado no Counterspell (anula automático até ele)
    rerolagens: int = 0
    stillness: bool = False       # Stillness of Mind
    bonus_prob: float = 0.0       # chance de +1 em todos os saves (carga do Ravin)
    cura_round: float = 0.0       # cura própria por round enquanto age
    ataques: int = 2              # ataques por turno (ação + ação bônus), para pesar Slow e Vicious Mockery


def peso(d, m):
    """Fração do turno perdida pelo efeito, conforme o personagem."""
    w = m.get("w", 1)
    if w == "slow":       # uma ação OU ação bônus, 1 ataque só, sem reação, metade do movimento
        if d.conjurador:
            return 0.6        # 50% de chance de a magia atrasar + perde a ação bônus
        return min(0.9, max(0.25, 1 - 1 / d.ataques + 0.05))
    if w == "mockery":    # desvantagem no próximo ataque
        return 0.05 if d.conjurador else 0.3 / d.ataques
    return w


def dados(n, d, size):
    return rng.integers(1, d + 1, (n, size)).sum(0).astype(float) if n else np.zeros(size)


def tipos_de(t, size):
    if t == "dragao":
        return rng.choice(np.array(["acido", "frio", "fogo", "eletrico", "veneno"], dtype=object), size)
    if t == "prisma":
        return rng.choice(np.array(["fogo", "acido", "eletrico", "veneno", "frio"], dtype=object), size)
    return np.full(size, t, dtype=object)


def conj(L):
    p = 2 + (L - 1) // 4
    mod = 3 if L <= 3 else 4 if L <= 7 else 5
    seq = []
    for nivel in range(len(SLOTS[L]), 0, -1):
        seq += [nivel] * SLOTS[L][nivel - 1]
    return 8 + p + mod, seq, p + mod


def cantrip_dados(L):
    return 1 if L < 5 else 2 if L < 11 else 3 if L < 17 else 4


class Luta:
    def __init__(self, d: S, lista, cantrips, L):
        self.d, self.lista, self.L = d, lista, L
        self.cd, self.seq, self.atk = conj(L)
        self.allsp = lista + cantrips
        self.ic = len(lista)                       # índices dos cantrips: ic, ic+1
        self.hp = np.full(N, float(d.pv)); self.zh = np.zeros(N); self.down = np.zeros(N, bool)
        self.absorb = np.full(N, float(d.absorb)); self.contra = np.full(N, float(d.contra))
        self.reroll = np.full(N, float(d.rerolagens)); self.ptr = np.zeros(N, int)
        self.conc = np.full(N, -1)                 # magia de concentração ativa
        self.ctrl = np.zeros(N, bool)              # controle da concentração ativo no alvo
        self.luta_w = np.zeros(N)                  # efeitos sem concentração que duram a luta
        self.luta_still = np.zeros(N, bool)
        self.fim_nc = np.zeros(N, bool); self.fim_nc_w = np.zeros(N); self.fim_nc_attr = np.full(N, "", dtype=object)
        self.fim_nc_still = np.zeros(N, bool)
        self.turno = np.zeros(N)
        self.pen = np.zeros(N, bool)               # Mind Sliver: −1d4 no próximo save
        self.lost = np.zeros(N)

    # ---------- utilidades ----------
    def imune(self, m):
        d = self.d
        return bool((m.get("humanoide") and not d.humanoide) or (m.get("encanto") and "encanto" in d.imune)
                    or (m.get("medo") and "medo" in d.imune) or (m.get("sono") and "sono" in d.imune))

    def save(self, attr, m, mask):
        d = self.d
        b = d.sv[attr] + (rng.random(N) < d.bonus_prob)
        b = b - np.where(self.pen, rng.integers(1, 5, N), 0)
        self.pen = self.pen & ~mask
        adv = (attr in d.adv) or (m.get("encanto") and d.adv_encanto) or \
              (d.adv_mental_magia and attr in ("int", "sab", "car")) or bool(m.get("vant_save")) or \
              (m.get("sono") and "sono_adv" in d.imune)
        r1 = rng.integers(1, 21, N); r2 = rng.integers(1, 21, N)
        roll = np.maximum(r1, r2) if adv else r1
        ok = roll + b >= self.cd
        use = (~ok) & (self.reroll > 0) & mask
        ok = ok | (use & (rng.integers(1, 21, N) + b >= self.cd))
        self.reroll = self.reroll - use
        return ok

    def dano(self, q, tipos, mask):
        d = self.d
        q = np.where(mask, q, 0.0)
        res = np.array([t in d.res for t in tipos])
        imu = np.array([t == "veneno" and "veneno" in d.imune for t in tipos])
        elem = np.array([t in ELEM for t in tipos])
        ab = elem & ~res & (self.absorb > 0) & (q > 0)
        self.absorb = self.absorb - ab
        q = q * np.where(imu, 0.0, np.where(res | ab, 0.5, 1.0))
        z = self.hp <= 0
        self.hp = self.hp - q
        if d.barrado:
            self.zh = self.zh + (z & (q > 0))
            self.down = self.down | (self.zh > d.barrado)
        else:
            self.down = self.down | (self.hp <= 0)
        # dano acorda quem está dormindo / dominado (efeitos 'sono' da concentração)
        hit = q > 0
        for i, m in enumerate(self.lista):
            if m.get("ef") == "sono":
                acorda = hit & (self.conc == i) & self.ctrl
                self.ctrl = self.ctrl & ~acorda
        self.luta_sono_dano(hit)

    def luta_sono_dano(self, hit):
        if hasattr(self, "sleep"):
            self.sleep = self.sleep & ~hit

    def aplicar(self, i, mask, nova=True):
        """Resolve a magia i (lançada agora ou repetindo pela área) nos alvos de mask."""
        if not mask.any():
            return
        m = self.allsp[i]; d = self.d
        if self.imune(m):
            return
        alvo = mask.copy()
        if m.get("ataque"):
            p = min(0.95, max(0.05, (21 - (d.ca - self.atk)) / 20))
            alvo = alvo & (rng.random(N) < p)
        if m.get("auto"):
            n_, dd, t = m["auto"]
            self.dano(dados(n_, dd, N), tipos_de(t, N), alvo)
        if m.get("sono_hp"):
            n_, dd = m["sono_hp"]
            pega = alvo & (dados(n_, dd, N) >= self.hp)
            self.sleep = getattr(self, "sleep", np.zeros(N, bool)) | pega
            return
        if m.get("limiar"):
            ok = self.save(m["save"], m, alvo)
            falha = alvo & ~ok
            self.luta_w = np.maximum(self.luta_w, np.where(falha & (self.hp <= 30), 1.0, 0))
            self.luta_w = np.maximum(self.luta_w, np.where(falha & (self.hp > 30) & (self.hp <= 40), 0.3, 0))
            return
        ok = self.save(m["save"], m, alvo) if m.get("save") else np.zeros(N, bool)
        if m.get("dano"):
            n_, dd, fx = m["dano"]
            if n_ == "cantrip":
                n_ = cantrip_dados(self.L)
            base = dados(n_, dd, N) + fx
            if m.get("sempre_dano"):
                q = base
            elif m.get("nada_no_sucesso"):
                q = np.where(ok, 0, base)
            elif d.evasion and m["save"] == "des":
                q = np.where(ok, 0, base / 2)
            else:
                q = np.where(ok, base / 2, base)
            self.dano(q, tipos_de(m["tipo"], N), alvo)
            if m.get("extra"):
                n2, d2, t2 = m["extra"]
                b2 = dados(n2, d2, N)
                q2 = np.where(ok, 0 if d.evasion else b2 / 2, b2 / 2 if d.evasion else b2)
                self.dano(q2, tipos_de(t2, N), alvo)
        if m.get("sliver"):
            self.pen = self.pen | (alvo & ~ok)
        falha = alvo & ~ok & ~self.down
        ef = m.get("ef")
        if ef is None:
            return
        w = peso(d, m)
        if m.get("w_conj") and d.conjurador:
            w = m["w_conj"]
        if ef == "area_peso":
            self.area_peso = getattr(self, "area_peso", np.zeros(N)) + np.where(alvo, w, 0)
            return
        if m.get("conc"):
            self.ctrl = self.ctrl | falha
        elif ef == "turno":
            self.turno = np.maximum(self.turno, np.where(falha, w, 0))
        elif ef == "luta":
            self.luta_w = np.maximum(self.luta_w, np.where(falha, w, 0))
            self.luta_still = self.luta_still | (falha & bool(m.get("stillness")))
        elif ef == "fim":
            self.fim_nc = self.fim_nc | falha
            self.fim_nc_w = np.where(falha, np.maximum(self.fim_nc_w, w), self.fim_nc_w)
            self.fim_nc_attr = np.where(falha, m["save"], self.fim_nc_attr)
            self.fim_nc_still = self.fim_nc_still | (falha & bool(m.get("stillness")))
        elif ef == "sono":
            self.sleep = getattr(self, "sleep", np.zeros(N, bool)) | falha

    def parado(self):
        """Alvo fora da luta: o conjurador não gasta nada (e não quebra o controle com dano)."""
        sleep = getattr(self, "sleep", np.zeros(N, bool))
        c_sono = np.zeros(N, bool); c_luta = np.zeros(N, bool)
        for i, m in enumerate(self.lista):
            if m.get("ef") == "sono":
                c_sono |= (self.conc == i) & self.ctrl
            if m.get("ef") == "luta" and peso(self.d, m) >= 1:
                c_luta |= (self.conc == i) & self.ctrl
        return self.down | sleep | c_sono | c_luta | (self.luta_w >= 1)

    def rodar(self):
        lst, L = self.lista, self.L
        niveis = np.array([m["nivel"] for m in lst])
        sem_conc = np.array([not m.get("conc") for m in lst])
        for r in range(R):
            # ---- conjurador ----
            para = self.parado()
            # concentração de ação: a ação do round vai para ela
            acao_ativa = np.zeros(N, bool)
            for i, m in enumerate(lst):
                if m.get("acao"):
                    a = (self.conc == i) & ~para
                    if m.get("ef") == "sono":
                        a = a & ~self.ctrl            # dorme? então não precisa reaplicar
                        self.aplicar(i, a)
                        acao_ativa |= (self.conc == i)
                    else:
                        self.aplicar(i, a)
                        acao_ativa |= a
            livre = ~para & ~acao_ativa
            slot = np.array([self.seq[p] if p < len(self.seq) else 0 for p in self.ptr])
            tem_conc = self.conc >= 0
            escolha = self.ic + rng.integers(0, 2, N)
            u = rng.random(N)
            for s in range(1, 10):
                for so_nc in (False, True):
                    sel = livre & (slot == s) & (tem_conc == so_nc)
                    if not sel.any():
                        continue
                    # candidatas: nível s (só sem concentração se já concentra); se não houver, desce
                    cand = []
                    for nv in range(s, 0, -1):
                        cand = [i for i in range(len(lst)) if niveis[i] == nv and (sem_conc[i] or not so_nc)]
                        if cand:
                            break
                    if cand:
                        k = np.minimum((u * len(cand)).astype(int), len(cand) - 1)
                        escolha = np.where(sel, np.array(cand)[k], escolha)
            usa_slot = livre & (escolha < self.ic)
            # Counterspell
            cs = usa_slot & (self.contra > 0)
            nv_e = np.where(usa_slot, niveis[np.minimum(escolha, len(lst) - 1)], 0)
            p_cs = np.where(nv_e <= self.d.contra_nivel, 1.0, np.clip((21 - (10 + nv_e - self.d.contra_mod)) / 20, 0, 1))
            anul = cs & (rng.random(N) < p_cs)
            self.contra = self.contra - cs
            self.ptr = self.ptr + usa_slot
            efetiva = livre & ~anul
            # nova concentração substitui a anterior
            nova_conc = efetiva & usa_slot & ~sem_conc[np.minimum(escolha, len(lst) - 1)]
            self.conc = np.where(nova_conc, escolha, self.conc)
            self.ctrl = self.ctrl & ~nova_conc
            for i in range(len(self.allsp)):
                msk = efetiva & (escolha == i)
                self.aplicar(i, msk)
            # áreas de concentração que continuam (não lançadas agora)
            for i, m in enumerate(lst):
                if m.get("area"):
                    cont = (self.conc == i) & ~(efetiva & (escolha == i)) & ~self.down
                    if m.get("ef") == "contido":
                        cont = cont & ~self.ctrl            # preso: só o dano de manutenção
                    self.aplicar(i, cont)
            # dano de quem continua preso (Tentacles, Phantasmal Force)
            for i, m in enumerate(lst):
                if m.get("tick"):
                    pres = (self.conc == i) & self.ctrl & ~self.down
                    n_, dd, t = m["tick"]
                    self.dano(dados(n_, dd, N), tipos_de(t, N), pres)
            # ---- turno do alvo ----
            sleep = getattr(self, "sleep", np.zeros(N, bool))
            ap = getattr(self, "area_peso", np.zeros(N))
            w_conc = np.zeros(N); still_conc = np.zeros(N, bool)
            for i, m in enumerate(lst):
                if m.get("conc") and m.get("ef") not in (None, "area_peso"):
                    a = (self.conc == i) & self.ctrl
                    w_conc = np.where(a, peso(self.d, m), w_conc)
                    still_conc |= a & bool(m.get("stillness"))
            perda = np.maximum.reduce([w_conc, self.luta_w, np.where(self.fim_nc, self.fim_nc_w, 0),
                                       self.turno, np.where(sleep, 1.0, 0), np.minimum(ap, 1)])
            # Stillness of Mind: gasta a ação para encerrar encanto/medo que não incapacita
            if self.d.stillness:
                usa = ~self.down & (still_conc | self.luta_still | self.fim_nc_still)
                perda = np.where(usa, np.minimum(perda, 0.5), perda)
                self.ctrl = self.ctrl & ~(usa & still_conc)
                self.luta_w = np.where(usa & self.luta_still, 0, self.luta_w)
                self.luta_still = self.luta_still & ~usa
                self.fim_nc = self.fim_nc & ~(usa & self.fim_nc_still)
                self.fim_nc_still = self.fim_nc_still & ~usa
            self.lost += np.where(self.down, 1.0, perda)
            if self.d.cura_round:
                age = ~self.down & (perda < 1)
                self.hp = np.where(age, np.minimum(self.d.pv, self.hp + self.d.cura_round), self.hp)
            self.turno[:] = 0
            self.area_peso = np.zeros(N)
            # saves de fim de turno
            for i, m in enumerate(lst):
                a = (self.conc == i) & self.ctrl
                if not a.any():
                    continue
                if m.get("ef") == "fim":
                    ok = self.save(m["save"], m, a)
                    self.ctrl = self.ctrl & ~(a & ok)
                elif m.get("ef") == "contido":
                    attr = m.get("escape", "for")
                    if attr == "forte":
                        attr = "for" if self.d.sv["for"] >= self.d.sv["des"] else "des"
                    ok = self.save(attr, m, a)
                    self.ctrl = self.ctrl & ~(a & ok)
            if self.fim_nc.any():
                for attr in ("for", "des", "con", "int", "sab", "car"):
                    a = self.fim_nc & (self.fim_nc_attr == attr)
                    if a.any():
                        ok = self.save(attr, {}, a)
                        self.fim_nc = self.fim_nc & ~(a & ok)
            # controle da concentração que já caiu libera a concentração (o conjurador tenta de novo)
            for i, m in enumerate(lst):
                if m.get("conc") and not m.get("area") and not m.get("acao"):
                    self.conc = np.where((self.conc == i) & ~self.ctrl, -1, self.conc)
        return float(np.mean(R - self.lost))


def teste(d: S, rampa, L):
    global rng
    rng = np.random.default_rng(1000 + L + (0 if rampa == "res" else 500))   # mesmos dados para todos
    lista, cant = (FISICAS, CANTRIPS_FISICOS) if rampa == "res" else (MENTAIS, CANTRIPS_MENTAIS)
    return Luta(d, lista, cant, L).rodar()


def nota(d: S, rampa):
    vals = [teste(d, rampa, L) for L in TESTES]
    return float(np.mean(vals)), vals


def prof(L):
    return 2 + (L - 1) // 4


def itens(L):
    """Crescimento dos saves que não vem da proficiência: ASIs, itens (Cloak/Ring of Protection),
    talentos (Resilient). +1 em todos os saves a cada 4 níveis."""
    return (L - 1) // 4


def regua(L):
    """Personagem equilibrado de nível L: Con e Sab proficientes, PV de d10 com Con 16,
    +1 nos saves no nível 11 e +2 no 15 (itens, como a CA da régua de defesa)."""
    p, it = prof(L), itens(L)
    return S(f"Régua de saves {L}", pv=13 + 9 * (L - 1), ca=18,
             sv={"for": 1 + it, "des": 2 + it, "con": 3 + p + it, "int": 0 + it, "sab": 1 + p + it, "car": 0 + it})


REGUA_NIVEIS = list(range(1, 21))
_MATRIZ = {}


def _arq_cache():
    import hashlib
    from pathlib import Path
    h = hashlib.sha1(Path(__file__).read_bytes()).hexdigest()[:10]
    return Path(__file__).resolve().parents[1] / 'cache' / f'saves-{h}.json'


def matriz(rampa):
    """Turnos livres da régua de nível L' em cada teste: M[t][L']. Guardada em cache/ (refeita se este arquivo mudar)."""
    import json
    arq = _arq_cache()
    if rampa not in _MATRIZ and arq.exists():
        d = json.loads(arq.read_text())
        for r, m in d.items(): _MATRIZ[r] = {int(t): np.array(v) for t, v in m.items()}
    if rampa not in _MATRIZ:
        _MATRIZ[rampa] = {t: np.maximum.accumulate([teste(regua(Lr), rampa, t) for Lr in REGUA_NIVEIS])
                          for t in TESTES}
        arq.parent.mkdir(exist_ok=True)
        arq.write_text(json.dumps({r: {str(t): list(map(float, v)) for t, v in m.items()} for r, m in _MATRIZ.items()}))
    return _MATRIZ[rampa]


def nivel_equivalente(vals, rampa):
    """Para cada teste, o nível da régua que se sai igual; a nota é a mediana."""
    M_ = matriz(rampa); eq = []
    for t, v in zip(TESTES, vals):
        curva = M_[t]
        if v <= curva[0]:
            eq.append(max(0.0, curva[0] and v / curva[0]))   # abaixo da régua de nível 1: fração do nível 1
        elif v >= curva[-1]:
            eq.append(float(REGUA_NIVEIS[-1]))
        else:
            eq.append(float(np.interp(v, curva, REGUA_NIVEIS)))
    return float(np.median(eq)), eq


CAMPOS = ('adv', 'evasion', 'res', 'imune', 'adv_encanto', 'adv_mental_magia', 'humanoide', 'conjurador', 'barrado',
          'absorb', 'contra', 'contra_mod', 'contra_nivel', 'rerolagens', 'stillness', 'bonus_prob', 'cura_round', 'ataques')


def avaliar(spec, corpo, reacao_livre=1.0):
    """spec (linha) + corpo (build): {"sv": {for,des,con,int,sab,car}, "pv", "ca", + campos de S}.
    Absorb Elements e Counterspell são reações: sem reação livre na hipótese, não contam."""
    from .base import letra
    d = dict(corpo.get('saves', {})); d.update(spec)
    if 'sv' not in d: raise ValueError('saves: faltam os bônus de save ("sv") no corpo ou na linha')
    k = {c: (tuple(d[c]) if isinstance(d[c], list) else d[c]) for c in CAMPOS if c in d}
    if reacao_livre <= 0: k['absorb'] = 0; k['contra'] = 0
    s = S(spec.get('nome', ''), d.get('pv', corpo['pv']), d.get('ca', corpo['ca']), d['sv'], **k)
    out = {}
    for rampa, nome in (('res', 'resiliencia'), ('vol', 'vontade')):
        vals = [teste(s, rampa, t) for t in TESTES]
        nv = round(nivel_equivalente(vals, rampa)[0], 2)
        out[nome] = dict(nivel_eq=nv, rank=letra(nv), turnos_livres=[round(v, 2) for v in vals])
    return out
