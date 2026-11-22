"""Wildfire Druid puro (22/11): a build do RPGBot (Gamera) sem o nível de Cleric (Arcana). Fatias 3/5/7/9/11, grupo RPGBot.
Rodar da raiz: python ferramentas/geradores/puro_druid.py && python -m dh expandir
Remendo: druida em todos os níveis (Enhanced Bond no 6, Cauterizing Flames no 10, Flame Strike no 9); sem os truques
de Arcana (Green-Flame Blade/Booming Blade), o ataque vira Produce Flame com Enhanced Bond; Tortle, escudo e War Caster
no 4 mantidos; Sab 18 no 8 (antes: personagem 9)."""
import sys

sys.path.insert(0, 'ferramentas/geradores')
from chassi_druid import D  # noqa: E402

PURO = "Extensão simples da build do RPGBot sem a multiclasse (níveis adiantados, atributos e feats remendados); a build original continua como referência."
D['wiz'].FONTE = lambda slug: {"tipo": "rpgbot", "url": D['URL'][slug], "nota": "Extensão simples sem multiclasse (22/11)."}
prof, area_sp, wall_fire = D['prof'], D['area_sp'], D['wall_fire']

F = {}
for L in D['FATIAS']:
    w = 3 if L < 8 else 4; p = prof(L); cd = 8 + p + w; atk = p + w
    eb = "+1d8" if L >= 6 else ""
    cant = lambda n, L=L, atk=atk, eb=eb: D['produce_flame'](L, atk, n, eb)
    esp_ = {"nome": "Wildfire Spirit", "quantidade": 1, "pv": 5 + 5 * L, "ca": 13, "ataque": {"n": 1, "bonus": atk, "dano": f"1d6+{p}"}}

    def espirito(l, esp_=esp_):
        l['invocacoes'] = [esp_] + list(l.get('invocacoes', [])); return l
    ea = "+4" if eb else ""
    areas = [area_sp("Burning Hands", 2, "3d6" + ea, cd, 1)] + ([wall_fire(cd, ea)] if L >= 7 else []) + \
            ([area_sp("Flame Strike", 2, "8d6" + ea, cd, 5)] if L >= 9 else [])
    sup = [{"nome": "Cauterizing Flames (cura na reação)", "lado": "def", "modelo": "cura", "usos_luta": round(p / 4, 2), "pv": 11 + w}] if L >= 10 else []
    cura = {"nome": "Healing Word (levanta um caído)", "lado": "def", "modelo": "cura_na_luta", "alcance": "distancia",
            "acao": "bonus", "usos_luta": 1, "pv": round(2.5 + w + (4.5 if eb else 0), 2)}
    f = D['fatia'](L, D['M'](3, -1, 3, -1, w, -1), ('int', 'sab'), 19, D['hpcalc']([8] * L, 3), cant, cd, atk, w, 'frontliner', True,
                   (L + 1) // 2, ctrl=[D['ENT'](cd), D['HP'](cd)], areas=areas, sup=sup, forma_var=("+espirito", espirito, 0.5))
    for l in f['linhas']:
        if 'suporte' in l:
            l['suporte']['fontes'] = [cura if x.get('modelo') == 'cura_na_luta' else x for x in l['suporte']['fontes']]
    f['_texto'] = f"Druid {L}; Tortle (CA 17) + escudo; Sab {10 + 2 * w}" + ("; War Caster" if L >= 4 else "") + ("; Enhanced Bond" if eb else "") + "."
    F[L] = f
D['emit']('rpgbot-druid-wildfire-puro', 'wildfire', 'Circle of Wildfire Druid puro (extensão da build do RPGBot)',
          "Druid (Wildfire) sem multiclasse, Tortle, escudo, Produce Flame; War Caster 4; Sab 18 (8)",
          {"resumo": "A build Gamera sem o nível de Cleric (Arcana): Wildfire Spirit, Produce Flame com Enhanced Bond, magias de fogo e Healing Word potencializado, tudo um nível antes.",
           "estrategia": PURO,
           "nao_modelado": "Fiery Teleport; magias saindo do espírito; Create Bonfire; Scorching Ray, Flaming Sphere, Plant Growth, Fire Shield, Aura of Life; Blazing Revival; War Caster (concentração); ação bônus disputada entre o espírito e Healing Word; lança (For 16) sem uso."}, F)
