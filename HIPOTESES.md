# Bíblia de hipóteses (gerada de premissas/premissas.json — não editar à mão)

Cada premissa é um "peso" do modelo. Mudar: `python -m dh premissa <nome> <valor> --motivo "..."`; depois `python -m dh completo 'builds/*.json'` recalcula só quem usa.

## area

| Premissa | Valor | Desde | Builds que usam | O que é |
|---|---|---|---|---|
| `area.alvos_referencia_por_circulo` | [2, 2, 4, 4, 6, 6, 6, 6, 6] | 2026-11-18 | 6 | Alvos da magia de área do conjurador de referência por círculo (1º…9º). |
| `area.cenarios` | {'esparsa': 0.5, 'padrao': 1.0, 'agrupada': 1.5} | 2026-11-18 | 6 | Escala de alvos por cenário (esparsa, padrão, agrupada). |
| `area.fator_round2_nao_seletiva` | 0.5 | 2026-11-18 | 6 | Idem para área não seletiva (a party se espalha, inimigos se afastam). |
| `area.fator_round2_seletiva` | 0.75 | 2026-11-18 | 6 | Do 2º round em diante uma área seletiva (escolhe alvos) ainda pega esta fração dos alvos do 1º round. |
| `area.horda_cr_por_nivel` | {'1': 0.125, '2': 0.25, '3': 0.25, '4': 0.5, '5': 1, '6': 1, '7': 1, '8': 2, '9': 2, '10': 2, '11': 3, '12': 3, '13': 4, '14': 4, '15': 4, '16': 4, '17': 5, '18': 5, '19': 6, '20': 6} | 2026-11-18 | 6 | CR das criaturas da horda de referência (encontro Difícil de 6) por nível da party. |
| `area.horda_tamanho` | 6 | 2026-11-18 | 6 | Criaturas na horda de referência. |

## base

| Premissa | Valor | Desde | Builds que usam | O que é |
|---|---|---|---|---|
| `base.chefe.chefe_save` | 2 | 2026-11-18 | 17 | Bônus extra nos saves de um chefe sozinho. |
| `base.chefe.lr_cr` | 10 | 2026-11-18 | 17 | CR mínimo para o chefe ter Legendary Resistance. |
| `base.chefe.lr_n` | 1 | 2026-11-18 | 17 | Legendary Resistances de um chefe sozinho. |
| `base.encontros` | [['Minions + minibosses', 0.25, [['Minion', 'Oportunista', 4, 0.25], ['Bruiser', 'Fera', 1, 0.25], ['Tank inimigo', 'Veterano defensor', 1, 0.25], ['Conjurador', 'Conjurador tático', 1, 0.25]]], ['Party de elite', 0.15, [['Bruiser', 'Veterano agressor', 1, 0.25], ['Tank inimigo', 'Veterano defensor', 1, 0.25], ['Artilheiro', 'Atirador', 1, 0.25], ['Conjurador', 'Conjurador tático', 1, 0.25]]], ['Horda + chefe', 0.15, [['Minion', 'Soldado disciplinado', 6, 0.5], ['Chefe', 'Comandante', 1, 0.5]]], ['Horda', 0.1, [['Minion', 'Oportunista', 6, 1.0]]], ['Dupla', 0.05, [['Bruiser', 'Fera', 1, 0.5], ['Conjurador', 'Conjurador tático', 1, 0.5]]], ['Chefe sozinho', 0.3, [['Chefe', 'Chefe (perfil próprio)', 1, 1.0]]]] | 2026-11-18 | 17 | Mistura de encontros do dia de referência: [nome, peso, composição [papel, perfil, quantidade, fração do orçamento de XP]]. Os pesos somam 1. |
| `base.perfis_inimigos` | {'Instintivo': [0.2, 0, True], 'Fera': [0.3, 1, True], 'Oportunista': [0.7, 2, True], 'Soldado disciplinado': [0.5, 2, True], 'Atirador': [0.0, 3, False], 'Cavaleiro noviço': [0.1, 1, True], 'Veterano defensor': [0.3, 2, True], 'Veterano agressor': [0.8, 2, True], 'Conjurador tático': [0.0, 3, False], 'Comandante': [0.2, 3, True], 'Chefe (perfil próprio)': [0.4, 2, True]} | 2026-11-18 | 17 | Comportamento dos inimigos: [fração que busca a backline, malícia 0–3, corpo a corpo?]. Define quem é atacado e quem foge de taunt. |
| `base.rounds_por_luta` | 4 | 2026-11-18 | 17 | Rounds por luta em todos os eixos (duração típica de um combate). |
| `base.save_tipo` | {'For': 1, 'Con': 1, 'Des': 0.5, 'Int': 0, 'Sab': 0, 'Car': 0} | 2026-11-18 | 17 | Quanto cada atributo de save puxa para o save forte do monstro (1 = forte, 0 = fraco). For/Con fortes, mentais fracos. |
| `base.topologias` | {'Campo aberto': {'peso': 0.25, 'area': 0.8, 'cruza': 0.3, 'alc_corpo_a_corpo_atras': 0.1, 'pg': 1.0, 'wall': 1.0}, 'Ruínas ou cidade': {'peso': 0.35, 'area': 1.0, 'cruza': 0.6, 'alc_corpo_a_corpo_atras': 0.15, 'pg': 1.0, 'wall': 1.0}, 'Sala de dungeon': {'peso': 0.4, 'area': 1.2, 'cruza': 0.9, 'alc_corpo_a_corpo_atras': 0.6, 'pg': 0.5, 'wall': 1.5}} | 2026-11-18 | 17 | Terrenos e seus pesos no dia, multiplicador de alvos em área, fração que cruza o alcance do tanque, alcance de quem fica atrás, eficácia do Plant Growth e do Wall of Force. |

## controle

| Premissa | Valor | Desde | Builds que usam | O que é |
|---|---|---|---|---|
| `controle.atencao.conc_bonus` | 1.5 | 2026-11-18 | 17 | Prioridade extra dos inimigos espertos em conjuradores concentrando. |
| `controle.atencao.near_back` | 0.25 | 2026-11-18 | 17 | Fração dos que querem a backline que ainda atacam quem está perto. |
| `controle.atencao.reach_grande` | 0.5 | 2026-11-18 | 17 | Alcance de inimigos grandes (atenção). |
| `controle.atencao.reach_pequeno` | 0.2 | 2026-11-18 | 17 | Alcance de inimigos pequenos (atenção). |
| `controle.atencao.skel_peso` | 1.5 | 2026-11-18 | 17 | Peso de atração de invocações/esqueletos sobre inimigos corpo a corpo. |
| `controle.atencao.skel_pv` | 133 | 2026-11-18 | 17 | PV padrão de um corpo de invocações quando a build não informa. |
| `controle.campo.golpes_party` | 2 | 2026-11-18 | 17 | Golpes da party por round que podem quebrar uma condição com save a cada dano. |
| `controle.campo.p_disengage` | 0.5 | 2026-11-18 | 17 | Chance de um inimigo parado por AO não ter como sair (padrão de parada_oa). |
| `controle.campo.reach_grande` | 0.5 | 2026-11-18 | 17 | Fração de inimigos grandes (CR ≥ 5) com alcance para escapar de agarrão/zona. |
| `controle.campo.reach_pequeno` | 0.2 | 2026-11-18 | 17 | Idem para inimigos menores. |
| `controle.campo.taunt_ameaca` | 0.15 | 2026-11-18 | 17 | Taunt soft de um corpo que ameaça (fração dos ataques desviados para ele). |
| `controle.campo.taunt_summon` | 0.4 | 2026-11-18 | 17 | Taunt de invocações que ocupam espaço. |
| `controle.padroes.counterspell_fracao_conjurando` | 0.75 | 2026-11-18 | 17 | Fração dos turnos de um conjurador inimigo em que ele lança algo que vale contramágica. |
| `controle.padroes.sentinela_tentativas` | 2 | 2026-11-18 | 17 | Ataques de oportunidade do Sentinel por luta que podem parar alguém (quando a build não diz). |
| `controle.padroes.terreno_fator` | 0.5 | 2026-11-18 | 17 | Fração do turno de um inimigo corpo a corpo perdida em terreno difícil grande (Plant Growth), antes do fator do terreno. |
| `controle.peso_no_controle.ameaca` | 0.0 | 2026-11-16 | 17 | Taunt soft (corpo que atrai ataques): só Corpo. |
| `controle.peso_no_controle.esqueletos` | 0.0 | 2026-11-16 | 17 | Invocações que desviam ataques: só Corpo. |
| `controle.peso_no_controle.parada_oa` | 0.25 | 2026-11-18 | 17 | Igual à do Sentinel, para paradas por ataque de oportunidade com probabilidade fixa. |
| `controle.peso_no_controle.sentinela` | 0.25 | 2026-11-18 | 17 | Fração da negação do AO do Sentinel (velocidade 0) que também conta como Controle. O resto (taunt, diluição de dano) fica só no Corpo. |

<details><summary>Histórico</summary>

- `controle.peso_no_controle.parada_oa`: valor 0.0, ate 2026-11-18
- `controle.peso_no_controle.parada_oa`: valor 0.5, desde 2026-11-18, motivo mesma decisão do Sentinel
- `controle.peso_no_controle.parada_oa`: de 0.5, para 0.25, data 2026-11-18, motivo usuário: tirar o movimento é ganho marginal (o alvo mantém ações, pode circular o tanque); 0,5 punha o Abdul acima dos casters
- `controle.peso_no_controle.sentinela`: valor 0.0, ate 2026-11-18, motivo 16/11: fontes de corpo fora do Controle (evitar contagem dupla)
- `controle.peso_no_controle.sentinela`: valor 0.5, desde 2026-11-18, motivo usuário: negar movimento só precisando acertar a CA é controle real (como o Plant Growth), mas parte do valor já está no Corpo
- `controle.peso_no_controle.sentinela`: de 0.5, para 0.25, data 2026-11-18, motivo usuário: tirar o movimento é ganho marginal (o alvo mantém ações, pode circular o tanque); 0,5 punha o Abdul acima dos casters

</details>

## defesa

| Premissa | Valor | Desde | Builds que usam | O que é |
|---|---|---|---|---|
| `defesa.chefe.acerto_extra` | 3 | 2026-11-18 | 13 | Bônus de ataque do chefe acima da coluna de acerto da tabela de dano. |
| `defesa.chefe.ataques_por_cr` | [[4, 2], [16, 3], [30, 4]] | 2026-11-18 | 13 | Ataques por round de um chefe: [até o CR, ataques]. |
| `defesa.chefe.cr_arma_magica` | 10 | 2026-11-18 | 13 | A partir deste CR os golpes do chefe ignoram redução de dano não mágica. |
| `defesa.fator_critico` | 0.6 | 2026-11-18 | 13 | Dano extra de um crítico inimigo, em fração do golpe normal (dados dobram, modificador não). |
| `defesa.horda.acerto` | {'base': 3, 'por_cr': 0.3333333333333333} | 2026-11-18 | 13 | Bônus de ataque da horda: base + CR × por_cr. |
| `defesa.horda.atacantes` | {'min': 3, 'max': 10} | 2026-11-18 | 13 | Horda: número de atacantes entre min e max (importa para redução fixa de dano). |
| `defesa.horda.dano_por_golpe` | {'base': 4, 'por_cr': 0.5} | 2026-11-18 | 13 | Horda: o dano por round do CR é dividido em golpes de (base + CR × por_cr). |

## eixos

| Premissa | Valor | Desde | Builds que usam | O que é |
|---|---|---|---|---|
| `eixos.def_fisica.peso_resiliencia` | 0.3333333333333333 | 2026-11-18 | 17 | Def. Física = (1 − p) × Defesa (blindagem/durabilidade) + p × Resiliência (saves For/Des/Con). |
| `eixos.def_magica.peso_resiliencia` | 0.3333333333333333 | 2026-11-18 | 17 | Def. Mágica = (1 − p) × Vontade (saves mentais) + p × Resiliência. |

## planos

| Premissa | Valor | Desde | Builds que usam | O que é |
|---|---|---|---|---|
| `planos.dias` | {'padrao': [['np', 1], ['p', 2], 'SR', ['np', 1], ['p', 2]], 'combate_unico': [['p', 1]], 'dia_longo': [['np', 1], ['np', 1], ['mod', 2], 'SR', ['np', 1], ['mod', 2], ['mod', 2], 'SR', ['mod', 2], ['boss', 4]]} | 2026-11-18 | 17 | Dias de aventura: sequência de [categoria, peso] e "SR" (descanso curto). Padrão: comum 1, prioritária 2. Dia longo: 8 lutas, boss pesa 4. |

## saves

| Premissa | Valor | Desde | Builds que usam | O que é |
|---|---|---|---|---|
| `saves.conjurador_inimigo.mod_por_nivel` | [[3, 3], [7, 4], [20, 5]] | 2026-11-18 | 0 | Modificador de conjuração do inimigo de referência: [até o nível, mod]. CD = 8 + proficiência + mod. |
| `saves.peso.mockery` | {'conjurador': 0.05, 'marcial': 0.3} | 2026-11-18 | 0 | Vicious Mockery: turno perdido por um conjurador; marcial = valor ÷ ataques por turno. |
| `saves.peso.slow_conjurador` | 0.6 | 2026-11-18 | 0 | Fração do turno que um conjurador perde sob Slow (50% de a magia atrasar + perde a ação bônus). |
| `saves.peso.slow_marcial` | {'min': 0.25, 'max': 0.9, 'extra': 0.05} | 2026-11-18 | 0 | Slow num marcial: 1 − 1/ataques + extra, entre min e max. |
| `saves.repertorio_fisico` | [{'dano': [3, 6, 0], 'tipo': 'fogo', 'metade': True, 'nome': 'Burning Hands', 'nivel': 1, 'save': 'des'}, {'dano': [2, 8, 0], 'tipo': 'trovao', 'metade': True, 'nome': 'Thunderwave', 'nivel': 1, 'save': 'con'}, {'ef': 'contido', 'w': 0.5, 'conc': True, 'escape': 'for', 'nome': 'Entangle', 'nivel': 1, 'save': 'for'}, {'dano': [3, 6, 0], 'tipo': 'dragao', 'metade': True, 'conc': True, 'acao': True, 'nome': "Dragon's Breath", 'nivel': 2, 'save': 'des'}, {'dano': [3, 8, 0], 'tipo': 'trovao', 'metade': True, 'nome': 'Shatter', 'nivel': 2, 'save': 'con'}, {'ef': 'contido', 'w': 0.5, 'conc': True, 'area': True, 'escape': 'for', 'nome': 'Web', 'nivel': 2, 'save': 'des'}, {'dano': [8, 6, 0], 'tipo': 'fogo', 'metade': True, 'nome': 'Fireball', 'nivel': 3, 'save': 'des'}, {'dano': [8, 6, 0], 'tipo': 'eletrico', 'metade': True, 'nome': 'Lightning Bolt', 'nivel': 3, 'save': 'des'}, {'dano': [2, 6, 0], 'tipo': 'acido', 'nada_no_sucesso': True, 'auto': [2, 6, 'frio'], 'ef': 'area_peso', 'w': 0.5, 'conc': True, 'area': True, 'nome': 'Hunger of Hadar', 'nivel': 3, 'save': 'des'}, {'dano': [3, 6, 0], 'tipo': 'fisico', 'nada_no_sucesso': True, 'ef': 'contido', 'w': 0.75, 'conc': True, 'area': True, 'tick': [3, 6, 'fisico'], 'escape': 'forte', 'nome': "Evard's Black Tentacles", 'nivel': 4, 'save': 'des'}, {'dano': [5, 8, 0], 'tipo': 'fogo', 'metade': True, 'conc': True, 'area': True, 'nome': 'Wall of Fire (de pé nela)', 'nivel': 4, 'save': 'des'}, {'dano': [2, 8, 0], 'tipo': 'fisico', 'metade': True, 'extra': [4, 6, 'frio'], 'nome': 'Ice Storm', 'nivel': 4, 'save': 'des'}, {'ef': 'contido', 'w': 0.75, 'conc': True, 'escape': 'for', 'nome': 'Watery Sphere', 'nivel': 4, 'save': 'for'}, {'dano': [5, 8, 0], 'tipo': 'veneno', 'metade': True, 'conc': True, 'area': True, 'nome': 'Cloudkill', 'nivel': 5, 'save': 'con'}, {'dano': [8, 8, 0], 'tipo': 'frio', 'metade': True, 'nome': 'Cone of Cold', 'nivel': 5, 'save': 'con'}, {'dano': [4, 8, 0], 'tipo': 'radiante', 'metade': True, 'ef': 'fim', 'w': 0.3, 'conc': True, 'nome': 'Wall of Light', 'nivel': 5, 'save': 'con'}, {'dano': [10, 8, 0], 'tipo': 'eletrico', 'metade': True, 'nome': 'Chain Lightning', 'nivel': 6, 'save': 'des'}, {'dano': [10, 6, 40], 'tipo': 'forca', 'nada_no_sucesso': True, 'nome': 'Disintegrate', 'nivel': 6, 'save': 'des'}, {'dano': [8, 6, 0], 'tipo': 'necrotico', 'metade': True, 'nome': 'Circle of Death', 'nivel': 6, 'save': 'con'}, {'dano': [12, 6, 0], 'tipo': 'fogo', 'metade': True, 'nome': 'Delayed Blast Fireball', 'nivel': 7, 'save': 'des'}, {'dano': [7, 8, 30], 'tipo': 'necrotico', 'metade': True, 'nome': 'Finger of Death', 'nivel': 7, 'save': 'con'}, {'dano': [10, 6, 0], 'tipo': 'prisma', 'metade': True, 'nome': 'Prismatic Spray', 'nivel': 7, 'save': 'des'}, {'dano': [10, 6, 0], 'tipo': 'fisico', 'metade': True, 'ef': 'contido', 'w': 0.5, 'conc': True, 'area': True, 'escape': 'for', 'nome': 'Whirlwind', 'nivel': 7, 'save': 'des'}, {'dano': [12, 6, 0], 'tipo': 'radiante', 'metade': True, 'ef': 'fim', 'w': 0.3, 'nome': 'Sunburst', 'nivel': 8, 'save': 'con'}, {'dano': [10, 8, 0], 'tipo': 'fogo', 'metade': True, 'conc': True, 'area': True, 'nome': 'Incendiary Cloud', 'nivel': 8, 'save': 'des'}, {'dano': [12, 8, 0], 'tipo': 'necrotico', 'metade': True, 'nome': "Abi-Dalzim's Horrid Wilting", 'nivel': 8, 'save': 'con'}] | 2026-11-18 | 0 | Magias de For/Des/Con do conjurador inimigo de referência (dano e contenção). Base da Resiliência. |
| `saves.repertorio_mental` | [{'sono_hp': [5, 8], 'ef': 'sono', 'w': 1, 'sono': True, 'nome': 'Sleep', 'nivel': 1, 'save': None}, {'ef': 'fim', 'w': 1, 'conc': True, 'nome': "Tasha's Hideous Laughter", 'nivel': 1, 'save': 'sab'}, {'ef': 'turno', 'w': 1, 'nome': 'Command', 'nivel': 1, 'save': 'sab'}, {'ef': 'fim', 'w': 1, 'conc': True, 'humanoide': True, 'nome': 'Hold Person', 'nivel': 2, 'save': 'sab'}, {'ef': 'fim', 'w': 1, 'conc': True, 'tick': [1, 6, 'psiquico'], 'nome': 'Phantasmal Force', 'nivel': 2, 'save': 'int'}, {'ef': 'luta', 'w': 1, 'conc': True, 'encanto': True, 'stillness': True, 'nome': 'Suggestion', 'nivel': 2, 'save': 'sab'}, {'ef': 'fim', 'w': 'slow', 'conc': True, 'nome': 'Slow', 'nivel': 3, 'save': 'sab'}, {'ef': 'fim', 'w': 1, 'conc': True, 'medo': True, 'stillness': True, 'nome': 'Fear', 'nivel': 3, 'save': 'sab'}, {'ef': 'sono', 'w': 1, 'conc': True, 'encanto': True, 'nome': 'Hypnotic Pattern', 'nivel': 3, 'save': 'sab'}, {'ef': 'luta', 'w': 1, 'conc': True, 'nome': 'Banishment', 'nivel': 4, 'save': 'car'}, {'ef': 'luta', 'w': 1, 'conc': True, 'nome': 'Polymorph', 'nivel': 4, 'save': 'sab'}, {'dano': [7, 6, 0], 'tipo': 'psiquico', 'metade': True, 'ef': 'turno', 'w': 1, 'nome': "Raulothim's Psychic Lance", 'nivel': 4, 'save': 'int'}, {'ef': 'sono', 'w': 1, 'conc': True, 'humanoide': True, 'encanto': True, 'stillness': True, 'nome': 'Dominate Person', 'nivel': 5, 'save': 'sab'}, {'dano': [8, 6, 0], 'tipo': 'psiquico', 'metade': True, 'ef': 'fim', 'w': 0.2, 'nome': 'Synaptic Static', 'nivel': 5, 'save': 'int'}, {'ef': 'sono', 'w': 1, 'conc': True, 'encanto': True, 'vant_save': True, 'nome': 'Modify Memory', 'nivel': 5, 'save': 'sab'}, {'ef': 'luta', 'w': 1, 'encanto': True, 'stillness': True, 'nome': 'Mass Suggestion', 'nivel': 6, 'save': 'sab'}, {'ef': 'sono', 'w': 1, 'conc': True, 'acao': True, 'sono': True, 'nome': 'Eyebite (dormir)', 'nivel': 6, 'save': 'sab'}, {'dano': [5, 10, 0], 'tipo': 'psiquico', 'nada_no_sucesso': True, 'ef': 'luta', 'w': 0.5, 'conc': True, 'nome': 'Mental Prison', 'nivel': 6, 'save': 'int'}, {'limiar': True, 'nome': 'Divine Word', 'nivel': 7, 'save': 'car'}, {'ataque': True, 'ef': 'luta', 'w': 1, 'nome': 'Plane Shift (ofensivo)', 'nivel': 7, 'save': 'car'}, {'ef': 'luta', 'w': 1, 'nome': 'Symbol (atordoamento)', 'nivel': 7, 'save': 'sab'}, {'dano': [4, 6, 0], 'tipo': 'psiquico', 'sempre_dano': True, 'ef': 'luta', 'w': 0.3, 'w_conj': 1, 'nome': 'Feeblemind', 'nivel': 8, 'save': 'int'}, {'ef': 'fim', 'w': 1, 'medo': True, 'stillness': True, 'nome': 'Antipathy (medo)', 'nivel': 8, 'save': 'sab'}, {'dano': [8, 8, 0], 'tipo': 'psiquico', 'metade': True, 'conc': True, 'area': True, 'nome': 'Maddening Darkness', 'nivel': 8, 'save': 'sab'}] | 2026-11-18 | 0 | Magias mentais (Int/Sab/Car) do conjurador inimigo de referência, com o efeito e o peso (fração do turno perdida). Ele lança do maior espaço para o menor, escolhendo entre as magias do círculo. Base da Vontade / Def. Mágica. |
| `saves.truques_fisicos` | [{'dano': ['cantrip', 6, 0], 'tipo': 'frio', 'nada_no_sucesso': True, 'nome': 'Frostbite', 'nivel': 0, 'save': 'con'}, {'dano': ['cantrip', 8, 0], 'tipo': 'radiante', 'nada_no_sucesso': True, 'nome': 'Sacred Flame', 'nivel': 0, 'save': 'des'}] | 2026-11-18 | 0 | Truques de save físico usados quando acabam os espaços. |
| `saves.truques_mentais` | [{'dano': ['cantrip', 6, 0], 'tipo': 'psiquico', 'nada_no_sucesso': True, 'sliver': True, 'nome': 'Mind Sliver', 'nivel': 0, 'save': 'int'}, {'dano': ['cantrip', 4, 0], 'tipo': 'psiquico', 'nada_no_sucesso': True, 'ef': 'turno', 'w': 'mockery', 'nome': 'Vicious Mockery', 'nivel': 0, 'save': 'sab'}] | 2026-11-18 | 0 | Truques mentais usados quando acabam os espaços (Mind Sliver, Vicious Mockery). |

## suporte

| Premissa | Valor | Desde | Builds que usam | O que é |
|---|---|---|---|---|
| `suporte.h.ACERTO` | 0.65 | 2026-11-18 | 7 | Chance de acerto típica de um aliado. |
| `suporte.h.ACERTOS_INIM_ROUND` | 4 | 2026-11-18 | 7 | Acertos em que o dano inimigo do round chega. |
| `suporte.h.ALIADOS` | 3 | 2026-11-18 | 7 | Aliados que recebem um buff em grupo. |
| `suporte.h.ATIVO` | 0.875 | 2026-11-18 | 7 | Fração da luta em que um buff contínuo está ativo. |
| `suporte.h.CUSTO_SAVE` | 1 | 2026-11-18 | 7 | Valor de 1 ponto de save, em dano evitado relativo. |
| `suporte.h.EF_CURA` | 0.9 | 2026-11-18 | 7 | Eficiência da cura (fração que não é desperdiçada). |
| `suporte.h.EF_PVT` | 0.75 | 2026-11-18 | 7 | Eficiência de PV temporários. |
| `suporte.h.ESCOLHA` | 2.0 | 2026-11-18 | 7 | Ganho de escolher quando gastar um dado de inspiração (×). |
| `suporte.h.F_AURA` | 0.67 | 2026-11-18 | 7 | Fração dos aliados dentro de uma aura. |
| `suporte.h.F_SAVE` | 0.25 | 2026-11-18 | 7 | Fração do dano inimigo que vem por save. |
| `suporte.h.PARCELA_FRENTE` | 0.35 | 2026-11-18 | 7 | Parcela do dano inimigo que vai para um aliado da linha de frente. |
| `suporte.h.P_ACERTO_INIM` | 0.6 | 2026-11-18 | 7 | Chance de um ataque inimigo acertar um aliado. |
| `suporte.h.TURNOS_CONDICAO` | 1.5 | 2026-11-18 | 7 | Turnos de aliado perdidos num save crítico falho. |
| `suporte.h.TURNOS_LEVANTAR` | 1.0 | 2026-11-18 | 7 | Turnos devolvidos ao levantar um caído. |
| `suporte.lutas_dia` | 4 | 2026-11-10 | 7 | Lutas por dia para diluir recursos usados ENTRE lutas ("quando": "entre_lutas": Song of Rest, PV temporário de descanso). |
| `suporte.lutas_por_descanso_curto` | 2 | 2026-11-10 | 7 | Lutas por descanso curto: recurso por descanso curto usado em combate se espalha por essas lutas. |
| `suporte.mix_dado_multiuso` | {'dano': 0.3, 'acerto': 0.25, 'ca': 0.2, 'save_dano': 0.15, 'save_critico': 0.07, 'counterspell': 0.03} | 2026-11-18 | 7 | Como um dado de inspiração é gasto em média (dano, acerto, CA, save de dano, save crítico, counterspell). Soma 1. |
| `suporte.padroes.resgate_p_evento` | 0.2 | 2026-11-18 | 7 | Chance por round de surgir uma condição que vale resgatar. |
| `suporte.padroes.resgate_p_save` | 0.45 | 2026-11-18 | 7 | Chance do aliado passar no save refeito contra uma condição (Countercharm e afins). |

## tatico

| Premissa | Valor | Desde | Builds que usam | O que é |
|---|---|---|---|---|
| `tatico.composicoes` | {'terceiro_melee': {'escondido': 0.04, 'longe': 0.1, 'colado': 0.2, 'nota': 'tanque + outro corpo a corpo na frente + ele + 1 de trás'}, 'segundo_frontliner': {'escondido': 0.05, 'longe': 0.15, 'colado': 0.32, 'nota': 'tanque + ele na frente + 2 de trás'}, 'sem_tanque': {'escondido': 0.06, 'longe': 0.2, 'colado': 0.45, 'nota': 'ele é o único corpo a corpo'}} | 2026-11-18 | 1 | Fração do dano inimigo por round que vai para o personagem conforme a posição (escondido, longe, colado) e a composição da party. |
| `tatico.padrao` | {'deslocamento': 30, 'ca': 15, 'steady_aim': True, 'p_agir_antes': 0.7, 'p_comeca_escondido': 0.3, 'p_aliado': {'r1': 0.2, 'depois': 0.7}, 'dano_inimigo_round': 54.5, 'composicao': 'segundo_frontliner', 'reducao_exposto': 1.0, 'pv': 50, 'recuperacao_dia': 20, 'lutas_dia': 4, 'excesso': 3.0, 'queda': 60, 'alvo': {'pv': 60, 'dano_aliados_colado': 25, 'dano_aliados_longe': 12}, 'topologias': {'Sala de dungeon': {'esconderijo': {'15': 0.6, '30': 0.3, '50': 0.1}, 'inicial': {'30': 0.5, '50': 0.5}, 'proximo': {'10': 0.4, '25': 0.4, '45': 0.2}}, 'Ruínas ou cidade': {'esconderijo': {'15': 0.4, '30': 0.4, '50': 0.2}, 'inicial': {'40': 0.5, '70': 0.5}, 'proximo': {'15': 0.3, '30': 0.4, '50': 0.3}}, 'Campo aberto': {'esconderijo': {'15': 0.15, '30': 0.35, '50': 0.5}, 'inicial': {'60': 0.5, '100': 0.5}, 'proximo': {'20': 0.3, '40': 0.4, '60': 0.3}}}} | 2026-11-18 | 1 | Premissas do motor tático (rogue/skirmisher): deslocamento, iniciativa, chance de começar escondido, aliado ao lado, orçamento de PV, distâncias por terreno. (Rounds: base.rounds_por_luta.) |

## O que não é premissa (régua e fatos)

- Tabelas do Monster Manual/DMG (fatos, não premissas): CA/PV/saves/dano por CR (base.CRT, area.CR, defesa.T_DMG), XP e orçamento de encontro (base.XP, base.BUD), dano de magia por círculo (area.MULTI), espaços por nível (area.TOP3, saves.SLOTS).
- Réguas (o 'zero' de cada eixo; mudam o significado das letras, não a hipótese): rampas de DPR (dano.TRONCO/BRUTA/PRECISA), limites de Defesa (defesa.LIM_*), régua de suporte (suporte.REGUA: DPR aliado, dano inimigo, maior espaço por nível), party de referência da atenção (controle.atencao.ref), letras (base.RAMPA).
- Parâmetros numéricos de simulação (precisão, não hipótese): N de simulações, sementes, grade de preços de reação (defesa.GRADE).

## Hipóteses ainda no código (migrar)

