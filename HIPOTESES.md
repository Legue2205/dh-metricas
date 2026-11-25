# Bíblia de hipóteses (gerada de premissas/premissas.json — não editar à mão)

Cada premissa é um "peso" do modelo. Mudar: `python -m dh premissa <nome> <valor> --motivo "..."`; depois `python -m dh completo 'builds/*.json'` recalcula só quem usa.

## aneis

| Premissa | Valor | Desde | Builds que usam | O que é |
|---|---|---|---|---|
| `aneis.alfa_versatilidade` | 0.2 | 2026-11-23 | 0 | D2: anel misto = plano padrão + α·(externo − plano), por eixo. O plano é o que a build faz com o combustível de um dia; o externo conta cada eixo como se todo o dia fosse dele ("três Wizards"). α dá valor à versatilidade sem triplicar a munição; marciais (mínimo ≈ máximo) quase não mudam. Visão padrão do teste de régua (comparar_chassi). Um α global por ora; parâmetro treinável (α por eixo só se o treino pedir). |

<details><summary>Histórico</summary>

- `aneis.alfa_versatilidade`: data 2026-11-23, de None, para 0.2, motivo D2 (usuário, 23/11): mistura com peso treinável, bem mais perto do plano do que do externo.

</details>

## area

| Premissa | Valor | Desde | Builds que usam | O que é |
|---|---|---|---|---|
| `area.alvos_referencia_por_circulo` | [2, 2, 4, 4, 6, 6, 6, 6, 6] | 2026-11-18 | 1172 | Alvos da magia de área do conjurador de referência por círculo (1º…9º). |
| `area.cenarios` | {'esparsa': 0.5, 'padrao': 1.0, 'agrupada': 1.5} | 2026-11-18 | 1172 | Escala de alvos por cenário (esparsa, padrão, agrupada). |
| `area.crescimento_por_nivel` | 1.12 | 2026-11-23 | 1172 | Área acima do 20 (D3): se a build ainda vence a referência no 20, nível eq. = 20 + ln(fr20/ref20)/ln(g), com g = quanto o desempenho contra a horda cresce por nível. Preserva a ordem das builds pelo desempenho no 20 (a margem pode ficar quase plana entre 11 e 20 e a raiz de uma reta explode). Antes: teto fixo em 20,0. g chutado ~ degraus da rampa antiga; parâmetro treinável. |
| `area.fator_round2_nao_seletiva` | 0.5 | 2026-11-18 | 1172 | Idem para área não seletiva (a party se espalha, inimigos se afastam). |
| `area.fator_round2_seletiva` | 0.75 | 2026-11-18 | 1172 | Do 2º round em diante uma área seletiva (escolhe alvos) ainda pega esta fração dos alvos do 1º round. |
| `area.horda2.N` | 3000 | 2026-11-19 | 1172 | Combates simulados por nível de horda. |
| `area.horda2.corpo` | 5 | 2026-11-19 | 1172 | Criaturas da horda no grupo que avança para o corpo a corpo (chega à linha de frente no round 2). |
| `area.horda2.distancia` | 3 | 2026-11-19 | 1172 | Criaturas da horda num grupo separado à distância (arqueiros): alvo de área sem fogo amigo em todos os rounds. |
| `area.horda2.fracao_alvo` | 0.5 | 2026-11-19 | 1172 | A luta de área termina quando a party tira esta fração da vida total da horda (o resto é limpeza, sem gastar recursos). |
| `area.horda2.guerreiros` | {'quantidade': 2, 'dano': '2d6', 'mod': [3, 4, 5], 'ataques': [1, 2, 3, 4]} | 2026-11-19 | 1172 | Dois guerreiros de referência que batem junto (alvo de menor PV, dano acima do PV é perdido). mod: +3 até o 3, +4 do 4 ao 7, +5 do 8; ataques: 1 até o 4, 2 do 5 ao 10, 3 do 11 ao 19, 4 no 20. |
| `area.horda2.rounds_max` | 3 | 2026-11-19 | 1172 | Teto de rounds; quem não chega à fração da vida é extrapolado pela taxa média (até 2× o teto). |
| `area.horda2.truque_referencia` | 1d10 | 2026-11-19 | 1172 | Truque de alvo único do conjurador de referência (dados escalam no 5 e no 11), ataque com prof + atributo da régua. |
| `area.horda_cr_por_nivel` | {'1': 0.125, '2': 0.25, '3': 0.25, '4': 0.5, '5': 1, '6': 1, '7': 1, '8': 2, '9': 2, '10': 2, '11': 3, '12': 3, '13': 4, '14': 4, '15': 4, '16': 4, '17': 5, '18': 5, '19': 6, '20': 6} | 2026-11-18 | 1172 | CR das criaturas da horda de referência (encontro Difícil de 6) por nível da party. |
| `area.horda_tamanho` | 6 | 2026-11-18 | 1172 | Criaturas na horda de referência. |

<details><summary>Histórico</summary>

- `area.crescimento_por_nivel`: data 2026-11-23, de None, para 1.12, motivo D3 (usuário, 23/11): tirar o teto da área; consistência interna antes da calibração entre réguas.
- `area.horda2.N`: data 2026-11-19, de None, para 3000, motivo Área v2 (usuário, 19/11): área = luta contra uma horda com a party de referência.
- `area.horda2.corpo`: data 2026-11-19, de None, para 5, motivo Área v2 (usuário, 19/11): área = luta contra uma horda com a party de referência.
- `area.horda2.distancia`: data 2026-11-19, de None, para 3, motivo Área v2 (usuário, 19/11): área = luta contra uma horda com a party de referência.
- `area.horda2.fracao_alvo`: data 2026-11-19, de None, para 0.5, motivo Área v2 (usuário, 19/11): área = luta contra uma horda com a party de referência.
- `area.horda2.guerreiros`: data 2026-11-19, de None, para {'quantidade': 2, 'dano': '2d6', 'mod': [3, 4, 5], 'ataques': [1, 2, 3, 4]}, motivo Área v2 (usuário, 19/11): área = luta contra uma horda com a party de referência.
- `area.horda2.rounds_max`: data 2026-11-19, de None, para 5, motivo Área v2 (usuário, 19/11): área = luta contra uma horda com a party de referência.
- `area.horda2.rounds_max`: de 5, para 3, data 2026-11-19, motivo usuário 19/11: medir o pico; com 5 rounds o DPR sustentado dos marciais pesava demais
- `area.horda2.truque_referencia`: data 2026-11-19, de None, para 1d10, motivo Área v2 (usuário, 19/11): área = luta contra uma horda com a party de referência.

</details>

## base

| Premissa | Valor | Desde | Builds que usam | O que é |
|---|---|---|---|---|
| `base.chefe.chefe_save` | 2 | 2026-11-18 | 1176 | Bônus extra nos saves de um chefe sozinho. |
| `base.chefe.lr_cr` | 10 | 2026-11-18 | 1176 | CR mínimo para o chefe ter Legendary Resistance. |
| `base.chefe.lr_n` | 1 | 2026-11-18 | 1176 | Legendary Resistances de um chefe sozinho. |
| `base.encontros` | [['Minions + minibosses', 0.25, [['Minion', 'Oportunista', 4, 0.25], ['Bruiser', 'Fera', 1, 0.25], ['Tank inimigo', 'Veterano defensor', 1, 0.25], ['Conjurador', 'Conjurador tático', 1, 0.25]]], ['Party de elite', 0.15, [['Bruiser', 'Veterano agressor', 1, 0.25], ['Tank inimigo', 'Veterano defensor', 1, 0.25], ['Artilheiro', 'Atirador', 1, 0.25], ['Conjurador', 'Conjurador tático', 1, 0.25]]], ['Horda + chefe', 0.15, [['Minion', 'Soldado disciplinado', 6, 0.5], ['Chefe', 'Comandante', 1, 0.5]]], ['Horda', 0.1, [['Minion', 'Oportunista', 6, 1.0]]], ['Dupla', 0.05, [['Bruiser', 'Fera', 1, 0.5], ['Conjurador', 'Conjurador tático', 1, 0.5]]], ['Chefe sozinho', 0.3, [['Chefe', 'Chefe (perfil próprio)', 1, 1.0]]]] | 2026-11-18 | 1176 | Mistura de encontros do dia de referência: [nome, peso, composição [papel, perfil, quantidade, fração do orçamento de XP]]. Os pesos somam 1. |
| `base.perfis_inimigos` | {'Instintivo': [0.2, 0, True], 'Fera': [0.3, 1, True], 'Oportunista': [0.7, 2, True], 'Soldado disciplinado': [0.5, 2, True], 'Atirador': [0.0, 3, False], 'Cavaleiro noviço': [0.1, 1, True], 'Veterano defensor': [0.3, 2, True], 'Veterano agressor': [0.8, 2, True], 'Conjurador tático': [0.0, 3, False], 'Comandante': [0.2, 3, True], 'Chefe (perfil próprio)': [0.4, 2, True]} | 2026-11-18 | 1176 | Comportamento dos inimigos: [fração que busca a backline, malícia 0–3, corpo a corpo?]. Define quem é atacado e quem foge de taunt. |
| `base.rounds_por_luta` | 4 | 2026-11-18 | 1176 | Rounds por luta em todos os eixos (duração típica de um combate). |
| `base.save_tipo` | {'For': 1, 'Con': 1, 'Des': 0.5, 'Int': 0, 'Sab': 0, 'Car': 0} | 2026-11-18 | 1176 | Quanto cada atributo de save puxa para o save forte do monstro (1 = forte, 0 = fraco). For/Con fortes, mentais fracos. |
| `base.topologias` | {'Campo aberto': {'peso': 0.25, 'area': 0.8, 'cruza': 0.3, 'alc_corpo_a_corpo_atras': 0.1, 'pg': 1.0, 'wall': 1.0}, 'Ruínas ou cidade': {'peso': 0.35, 'area': 1.0, 'cruza': 0.6, 'alc_corpo_a_corpo_atras': 0.15, 'pg': 1.0, 'wall': 1.0}, 'Sala de dungeon': {'peso': 0.4, 'area': 1.2, 'cruza': 0.9, 'alc_corpo_a_corpo_atras': 0.6, 'pg': 0.5, 'wall': 1.5}} | 2026-11-18 | 1176 | Terrenos e seus pesos no dia, multiplicador de alvos em área, fração que cruza o alcance do tanque, alcance de quem fica atrás, eficácia do Plant Growth e do Wall of Force. |
| `concentracao.acertos_por_round` | {'front': 1.5, 'meio': 0.8, 'tras': 0.5} | 2026-11-24 | 685 | Acertos recebidos por round pela build, pela posição (front = defensor/striker ou linha com atenção de linha de frente; meio = skirmisher/meia distância; trás = atirador/retaguarda). Provisório, candidato a treino; idealmente sai do motor de atenção. |
| `concentracao.ativa` | 1 | 2026-11-24 | 1176 | Liga o ajuste de concentração genérico (dh/concentracao.py, Etapa C, 24/11): a magia de concentração da linha vale só a fração dos rounds em que se espera que ela fique de pé. |
| `concentracao.foco_inimigo` | 1.0 | 2026-11-24 | 685 | Multiplicador dos acertos em quem concentra (inimigos espertos miram o conjurador concentrando; 1 = sem foco extra). |
| `concentracao.forma_con` | 3 | 2026-11-24 | 6 | Bônus de save de CON de uma forma (Polymorph/Shapechange/Animal Shapes): usa o da besta (ex.: T-Rex +3), não o do conjurador. |

## controle

| Premissa | Valor | Desde | Builds que usam | O que é |
|---|---|---|---|---|
| `controle.atencao.ca_dpr_auto` | 16 | 2026-11-19 | 1176 | CA usada para o DPR da atenção quando a build declara "dpr": "auto" (a mesma coluna que a party usa). |
| `controle.atencao.conc_bonus` | 1.5 | 2026-11-18 | 1176 | Prioridade extra dos inimigos espertos em conjuradores concentrando. |
| `controle.atencao.near_back` | 0.25 | 2026-11-18 | 1176 | Fração dos que querem a backline que ainda atacam quem está perto. |
| `controle.atencao.reach_grande` | 0.5 | 2026-11-18 | 1176 | Alcance de inimigos grandes (atenção). |
| `controle.atencao.reach_pequeno` | 0.2 | 2026-11-18 | 1176 | Alcance de inimigos pequenos (atenção). |
| `controle.atencao.redireciona.adjacente` | 0.15 | 2026-11-24 | 1176 | D13: idem, só aliado adjacente (Divine Allegiance, 5 pés): o alcance corta a fração. Treinável. |
| `controle.atencao.redireciona.aura` | 0.25 | 2026-11-24 | 1176 | D13: fração dos turnos inimigos contra aliados que a build puxa para si com alcance de aura (Aura of the Guardian, 10 pés; Protective Bond, teleporte de 30 pés). Limitada pela reação (1 por round contra ~3–4 turnos inimigos em aliados) e pelo alcance. Treinável. |
| `controle.atencao.skel_peso` | 1.0 | 2026-11-18 | 1176 | Peso de atração de invocações/esqueletos sobre a parcela não maliciosa (1 − malícia) dos inimigos corpo a corpo (1 = o mesmo de um frontliner). A parcela maliciosa escolhe a invocação pela ameaça por PV (DPR/PV), como faz com os membros (D4, 23/11). |
| `controle.atencao.skel_pv` | 133 | 2026-11-18 | 1176 | PV padrão de um corpo de invocações quando a build não informa. |
| `controle.campo.golpes_party` | 2 | 2026-11-18 | 1176 | Golpes da party por round que podem quebrar uma condição com save a cada dano. |
| `controle.campo.p_disengage` | 0.5 | 2026-11-18 | 1176 | Chance de um inimigo parado por AO não ter como sair (padrão de parada_oa). |
| `controle.campo.reach_grande` | 0.5 | 2026-11-18 | 1176 | Fração de inimigos grandes (CR ≥ 5) com alcance para escapar de agarrão/zona. |
| `controle.campo.reach_pequeno` | 0.2 | 2026-11-18 | 1176 | Idem para inimigos menores. |
| `controle.campo.taunt_ameaca` | 0.15 | 2026-11-18 | 1176 | Taunt soft de um corpo que ameaça (fração dos ataques desviados para ele). |
| `controle.campo.taunt_summon` | 0.4 | 2026-11-18 | 1176 | Taunt de invocações que ocupam espaço. |
| `controle.corpo.extrap_pontos` | 0 | 2026-11-23 | 1176 | Corpo além do nível 1–20 (D8): a raiz de T é extrapolada por uma regressão linear sobre os últimos N pontos da busca (0 = a busca inteira, do nível da build até o 20) (antes: só os 2 últimos, instável porque T oscila com os CRs discretos dos encontros). Sem teto. |
| `controle.corpo.referencia_unica` | 1 | 2026-11-19 | 1176 | Corpo (T, S, P e tag) compara a build com um MEMBRO PADRÃO na vaga dela: o comportamento da vaga (alvo, acc, concentração) é o da referência da posição, mas CA e PV são a média da party de referência (2 frontliners, atirador, conjurador). 0 = referência da própria posição (antes de 19/11). Tira a 'colher de chá' de quem fica atrás. |
| `controle.marca.fator_sem_resistencia` | 0.5 | 2026-11-19 | 1176 | Marca no acerto só com desvantagem contra os outros (Unwavering Mark), sem a resistência que os aliados ganham no Ancestral Protectors: fração do valor da marca completa. 0,5 ≈ (1 − p_desv/p) ÷ (1 − 0,5·p_desv/p) com p ≈ 0,65. |
| `controle.padroes.counterspell_fracao_conjurando` | 0.75 | 2026-11-18 | 1176 | Fração dos turnos de um conjurador inimigo em que ele lança algo que vale contramágica. |
| `controle.padroes.sentinela_tentativas` | 2 | 2026-11-18 | 1176 | Ataques de oportunidade do Sentinel por luta que podem parar alguém (quando a build não diz). |
| `controle.padroes.terreno_fator` | 0.5 | 2026-11-18 | 1176 | Fração do turno de um inimigo corpo a corpo perdida em terreno difícil grande (Plant Growth), antes do fator do terreno. |
| `controle.peso_no_controle.ameaca` | 0.0 | 2026-11-16 | 1176 | Taunt soft (corpo que atrai ataques): só Corpo. |
| `controle.peso_no_controle.ancestral_protectors` | 0.25 | 2026-11-19 | 1176 | Marca (Ancestral Protectors; Unwavering Mark com "resistencia": false): fração da redução do dano que o marcado causa aos aliados que também conta como Controle. O resto fica no Corpo (atenção: a marca protege os outros membros da party). Mesmo valor da do Sentinel. |
| `controle.peso_no_controle.esqueletos` | 0.0 | 2026-11-16 | 1176 | Invocações que desviam ataques: só Corpo. |
| `controle.peso_no_controle.parada_oa` | 0.25 | 2026-11-18 | 1176 | Igual à do Sentinel, para paradas por ataque de oportunidade com probabilidade fixa. |
| `controle.peso_no_controle.sentinela` | 0.25 | 2026-11-18 | 1176 | Fração da negação do AO do Sentinel (velocidade 0) que também conta como Controle. O resto (taunt, diluição de dano) fica só no Corpo. |
| `controle.referencia.frontliner.ca_bonus` | 1 | 2026-11-19 | 1176 | Frontliner de referência (2 na party): CA = CA marcial do nível + este bônus (média entre o tank, +2, e o striker, +0). |
| `controle.referencia.frontliner.ca_max` | 21 | 2026-11-19 | 1176 | Teto da CA do frontliner de referência. |
| `controle.referencia.frontliner.dpr_fator` | 0.85 | 2026-11-19 | 1176 | DPR do frontliner de referência = este fator × DPR de referência do nível (média entre tank 0,7 e striker 1,0). |
| `controle.referencia.frontliner.pv_base` | 11 | 2026-11-19 | 1176 | PV do frontliner de referência no nível 1 (média entre tank 12 e striker 10). |
| `controle.referencia.frontliner.pv_por_nivel` | 8 | 2026-11-19 | 1176 | PV por nível acima do 1º do frontliner de referência (média entre tank 8,5 e striker 7,5). |
| `controle.referencia.frontliner.soft` | 0.15 | 2026-11-19 | 1176 | Ameaça (taunt soft) do frontliner de referência. |

<details><summary>Histórico</summary>

- `controle.atencao.redireciona.adjacente`: data 2026-11-24, de None, para 0.15, motivo D13 (usuário, 24/11): puxar o dano de um aliado para si entra no corpo, como um taunt forte; só vale se aguentar o dano.
- `controle.atencao.redireciona.aura`: data 2026-11-24, de None, para 0.25, motivo D13 (usuário, 24/11): puxar o dano de um aliado para si entra no corpo, como um taunt forte; só vale se aguentar o dano.
- `controle.atencao.skel_peso`: data 2026-11-23, de 1.5, para 1.0, motivo D4 (usuário, 23/11): inimigos não fazem ataques burros; a parcela 'burra' trata a invocação como mais um corpo na linha de frente (peso de um frontliner), e a parcela esperta passa a pesar a ameaça por PV da invocação (inv_dpr).
- `controle.corpo.extrap_pontos`: data 2026-11-23, de None, para 0, motivo D8 (usuário, 23/11): sem teto no corpo; prioridade é a consistência da régua, então extrapolação estável.
- `controle.marca.fator_sem_resistencia`: data 2026-11-19, de None, para 0.5, motivo Usuário: Ancestral Protectors é mais forte que Unwavering Mark (resistência ao dano nos aliados).
- `controle.peso_no_controle.ancestral_protectors`: data 2026-11-19, de None, para 0.25, motivo Usuário 19/11 (passada 3): marcas contam no Corpo; fração no Controle igual à do Sentinel.
- `controle.peso_no_controle.parada_oa`: valor 0.0, ate 2026-11-18
- `controle.peso_no_controle.parada_oa`: valor 0.5, desde 2026-11-18, motivo mesma decisão do Sentinel
- `controle.peso_no_controle.parada_oa`: de 0.5, para 0.25, data 2026-11-18, motivo usuário: tirar o movimento é ganho marginal (o alvo mantém ações, pode circular o tanque); 0,5 punha o Abdul acima dos casters
- `controle.peso_no_controle.sentinela`: valor 0.0, ate 2026-11-18, motivo 16/11: fontes de corpo fora do Controle (evitar contagem dupla)
- `controle.peso_no_controle.sentinela`: valor 0.5, desde 2026-11-18, motivo usuário: negar movimento só precisando acertar a CA é controle real (como o Plant Growth), mas parte do valor já está no Corpo
- `controle.peso_no_controle.sentinela`: de 0.5, para 0.25, data 2026-11-18, motivo usuário: tirar o movimento é ganho marginal (o alvo mantém ações, pode circular o tanque); 0,5 punha o Abdul acima dos casters
- `controle.referencia.frontliner.ca_bonus`: data 2026-11-19, de None, para 1, motivo Usuário 19/11 (passada 3): tank e striker de referência viram um frontliner só, com valores médios.
- `controle.referencia.frontliner.ca_max`: data 2026-11-19, de None, para 21, motivo Usuário 19/11 (passada 3): tank e striker de referência viram um frontliner só, com valores médios.
- `controle.referencia.frontliner.dpr_fator`: data 2026-11-19, de None, para 0.85, motivo Usuário 19/11 (passada 3): tank e striker de referência viram um frontliner só, com valores médios.
- `controle.referencia.frontliner.pv_base`: data 2026-11-19, de None, para 11, motivo Usuário 19/11 (passada 3): tank e striker de referência viram um frontliner só, com valores médios.
- `controle.referencia.frontliner.pv_por_nivel`: data 2026-11-19, de None, para 8, motivo Usuário 19/11 (passada 3): tank e striker de referência viram um frontliner só, com valores médios.
- `controle.referencia.frontliner.soft`: data 2026-11-19, de None, para 0.15, motivo Usuário 19/11 (passada 3): tank e striker de referência viram um frontliner só, com valores médios.

</details>

## corpo

| Premissa | Valor | Desde | Builds que usam | O que é |
|---|---|---|---|---|
| `corpo.pvt_rounds` | 3 | 2026-11-21 | 0 | Rounds em que o PV temporário renovável (pvt_round, ex.: Reckless Abandon) conta na atenção/corpo: PV + pvt_luta + pvt_round × este valor. |

## dano

| Premissa | Valor | Desde | Builds que usam | O que é |
|---|---|---|---|---|
| `dano.peso_rampa_bruta` | 0.5 | 2026-11-23 | 1172 | D1: nível eq. de dano = β·rampa bruta (CA 16) + (1 − β)·rampa precisa (CA 18–25). Antes: o máximo das duas, que deixava invisível todo feat que troca acerto por dano (a build só trocava de perfil). β ~ o peso das CAs típicas na distribuição de inimigos; parâmetro treinável. |
| `dano.peso_round1` | 1.0 | 2026-11-25 | 1172 | D12: peso do 1º round na régua de dano (rounds pesam [w, 1, 1, 1], normalizados: o dano constante não muda). Vale para ataques marcados round1 (Dread Ambusher) e para o dano por luta (smites e afins), gasto nos primeiros acertos. Quem age antes tira inimigo da luta mais cedo; peso moderado para não favorecer demais o burst (contra chefe importa menos). Treinável; poderia variar por tipo de encontro. |
| `invocacao.peso.companheiro` | 1.0 | 2026-11-24 | 58 | Peso dos companheiros de feature de subclasse (Drake, Primal Companion, Steel Defender, Eldritch Cannon, Wildfire Spirit…): contam inteiros (usuário, 24/11). |
| `invocacao.peso.numerosa` | 0.0 | 2026-11-24 | 61 | Peso (0–1, multiplica a quantidade) das invocações numerosas do modelo antigo (Conjure Animals/Woodland Beings/Minor Elementals/Elemental, Animate Dead, ciclo do necromante). 0 = não contam: muita economia de ação, e o modelo não cobre concentração caindo nem área matando o bando (usuário, 24/11). Candidata a parâmetro treinável. |
| `invocacao.peso.summon` | 1.0 | 2026-11-24 | 129 | Peso das magias Summon X (Tasha): uma criatura com bloco que escala; já vieram balanceadas, contam inteiras (usuário, 24/11). |
| `rogue.vantagem.ajuste_scout` | 0.1 | 2026-11-24 | 10 | D11: o Scout tem Steady Aim mais confiável (Skirmisher: anda na reação, fora do próprio turno, então não perde o Steady Aim) e é feito para isso. Soma à rogue.vantagem.atirador. Treinável. |
| `rogue.vantagem.atirador` | 0.8 | 2026-11-24 | 66 | D11: chance de o Rogue atirador ter vantagem no ataque do turno, combinando Steady Aim (quando não precisa andar) e Hide (quando há onde se esconder e passa na percepção passiva). Não é produto: as fontes cobrem os turnos uma da outra. Turno 1 costuma ser de posicionamento. Antes: 1,0 (Steady Aim em todo turno). Treinável. |

<details><summary>Histórico</summary>

- `dano.peso_rampa_bruta`: data 2026-11-23, de None, para 0.5, motivo D1 (usuário, 23/11): mistura ponderada das rampas com peso treinável.
- `dano.peso_round1`: data 2026-11-24, de None, para 1.25, motivo D12 (usuário, 24/11): peso extra no 1º round, mas não alto.
- `dano.peso_round1`: de 1.25, para 1.0, data 2026-11-25, motivo 25/11 (usuário): o valor de agir antes/burst passa a ser medido explicitamente (dano.por_round e valor de abate, Etapa D, opção b — métrica própria de fechar luta na fase 2); o peso fixo de 1,25 no 1º round deixa de ser necessário
- `rogue.vantagem.ajuste_scout`: data 2026-11-24, de None, para 0.1, motivo D11 (usuário, 24/11): Scout justifica vantagem maior pelo movimento de reação.
- `rogue.vantagem.atirador`: data 2026-11-24, de None, para 0.8, motivo D11 (usuário, 24/11): uma chance global de vantagem ~0,75–0,85, ajustável por subclasse.

</details>

## defesa

| Premissa | Valor | Desde | Builds que usam | O que é |
|---|---|---|---|---|
| `defesa.chefe.acerto_extra` | 3 | 2026-11-18 | 653 | Bônus de ataque do chefe acima da coluna de acerto da tabela de dano. |
| `defesa.chefe.ataques_por_cr` | [[4, 2], [16, 3], [30, 4]] | 2026-11-18 | 653 | Ataques por round de um chefe: [até o CR, ataques]. |
| `defesa.chefe.cr_arma_magica` | 10 | 2026-11-18 | 653 | A partir deste CR os golpes do chefe ignoram redução de dano não mágica. |
| `defesa.fator_critico` | 0.6 | 2026-11-18 | 653 | Dano extra de um crítico inimigo, em fração do golpe normal (dados dobram, modificador não). |
| `defesa.horda.acerto` | {'base': 3, 'por_cr': 0.3333333333333333} | 2026-11-18 | 653 | Bônus de ataque da horda: base + CR × por_cr. |
| `defesa.horda.atacantes` | {'min': 3, 'max': 10} | 2026-11-18 | 653 | Horda: número de atacantes entre min e max (importa para redução fixa de dano). |
| `defesa.horda.dano_por_golpe` | {'base': 4, 'por_cr': 0.5} | 2026-11-18 | 653 | Horda: o dano por round do CR é dividido em golpes de (base + CR × por_cr). |

## eixos

| Premissa | Valor | Desde | Builds que usam | O que é |
|---|---|---|---|---|
| `eixos.def_fisica.peso_resiliencia` | 0.3333333333333333 | 2026-11-18 | 1176 | Def. Física = (1 − p) × Defesa (blindagem/durabilidade) + p × Resiliência (saves For/Des/Con). |
| `eixos.def_magica.peso_resiliencia` | 0.3333333333333333 | 2026-11-18 | 1176 | Def. Mágica = (1 − p) × Vontade (saves mentais) + p × Resiliência. |

## plano

| Premissa | Valor | Desde | Builds que usam | O que é |
|---|---|---|---|---|
| `moeda.ca_ref_base` | 14 | 2026-11-24 | 1159 | CA de referência do DPR na moeda DE: base + nível ÷ moeda.ca_ref_niveis_por_ponto (15 no 7, 16 no 11). |
| `moeda.ca_ref_niveis_por_ponto` | 4 | 2026-11-24 | 1159 | Níveis por ponto de CA na CA de referência da moeda DE. |
| `moeda.peso` | {'dano': 1.0, 'suporte': 1.0, 'controle': 1.0, 'area': 0.5} | 2026-11-24 | 1159 | Peso de cada parcela do dano equivalente no plano padrão. Área 0,5 = parcela das lutas que são horda (provisório, usuário 24/11). Dano causado = dano evitado (1:1). |
| `plano.auto.moeda` | de | 2026-11-24 | 1176 | Como o plano padrão automático soma as linhas: 'de' = dano equivalente por luta (dh/moeda.py; adotado pelo usuário em 24/11, Etapa B — evita somar níveis de réguas descalibradas entre si, ex.: Bless × smite do Paladin) ou 'niveis' = soma de nível eq. ÷ típico × peso (D5, antes de 24/11). Planos de foco usam sempre o nível do próprio eixo. |
| `plano.auto.peso_eixo` | {'dano': 1, 'defesa': 1, 'resiliencia': 1, 'vontade': 1, 'campo': 1, 'corpo': 1, 'area': 1, 'suporte': 1} | 2026-11-23 | 1176 | D5: o plano automático escolhe, dentro do livro-caixa, a atribuição de linhas que maximiza o rendimento do dia = soma (peso do combate × valor da linha); valor da linha = soma dos níveis eq. dos eixos (mesma nota do plano) × este peso por eixo. Gasto vira desempate. Pesos iguais por ora; parâmetros treináveis. |
| `plano.auto.tipico` | {'area': {'3': 4.2, '5': 4.6, '7': 4.6, '9': 4.8, '11': 8.0, '14': 16.4}, 'campo': {'3': 1.82, '5': 4.45, '7': 5.8, '9': 6.12, '11': 7.32}, 'corpo': {'3': 3.0, '5': 5.0, '7': 7.0, '9': 12.35, '11': 11.0}, 'dano': {'3': 2.1, '5': 4.8, '7': 5.3, '9': 6.5, '11': 7.7}, 'defesa': {'3': 2.2, '5': 4.0, '7': 5.7, '9': 8.6, '11': 9.4}, 'resiliencia': {'3': 2.7, '5': 4.52, '7': 7.39, '9': 8.83, '11': 11.3}, 'suporte': {'3': 3.2, '5': 3.7, '7': 3.82, '9': 4.1, '11': 4.5}, 'vontade': {'3': 4.06, '5': 8.25, '7': 8.44, '9': 12.19, '11': 12.35}} | 2026-11-23 | 1176 | P2.15: nível típico de cada eixo por nível de build (percentil 75 das linhas que fazem o eixo, nota > 0,5, em todos os resultados). O rendimento do plano automático usa nível ÷ típico, para nenhum eixo ganhar só por ter uma escala maior. Gerado por calibracao/tipico_eixos.py --gravar. |

<details><summary>Histórico</summary>

- `plano.auto.peso_eixo`: data 2026-11-23, de None, para todos 1, motivo D5 (usuário, 23/11): maximizar o rendimento respeitando o orçamento, não o gasto.
- `plano.auto.tipico`: data 2026-11-23, de None, para recalculado, motivo P2.15 (usuário, 23/11): normalizar por eixo; recalculado dos resultados.

</details>

## planos

| Premissa | Valor | Desde | Builds que usam | O que é |
|---|---|---|---|---|
| `planos.dias` | {'padrao': [['np', 1], ['p', 2], 'SR', ['np', 1], ['p', 2]], 'combate_unico': [['p', 1]], 'dia_longo': [['np', 1], ['np', 1], ['mod', 2], 'SR', ['np', 1], ['mod', 2], ['mod', 2], 'SR', ['mod', 2], ['boss', 4]]} | 2026-11-18 | 1176 | Dias de aventura: sequência de [categoria, peso] e "SR" (descanso curto). Padrão: comum 1, prioritária 2. Dia longo: 8 lutas, boss pesa 4. |
| `planos.magias_por_luta` | {'utilidade': 0.2} | 2026-11-23 | 1176 | D9: quantas linhas (magias) cabem numa luta do plano automático. k = espaços do dia × (1 − utilidade) / combates do dia, arredondado, entre 1 e base.rounds_por_luta; a build pode fixar "magias_por_luta". Linhas extras entram pelo ganho marginal sobre a linha principal (à vontade): valor e gasto = linha 1 + Σ (extra − principal); no máximo uma concentração por luta. Utilidade = fração dos espaços que não vai para combate. |

<details><summary>Histórico</summary>

- `planos.magias_por_luta`: data 2026-11-23, de None, para {'utilidade': 0.2}, motivo D9 (usuário, 23/11): premissa de magias por luta derivada dos espaços, ~20% para utilidade, sobrescrevível por build.

</details>

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
| `suporte.dado_multiuso.decaimento` | 0.75 | 2026-11-23 | 463 | D6: retorno decrescente dos usos de um dado multiuso (Bardic Inspiration e afins) na mesma luta: o k-ésimo uso vale δ^k (total (1 − δ^u)/(1 − δ)). As oportunidades de ouro são poucas; cada fonte (ex.: BI e Cutting Words) tem a sua sequência, então uma opção extra nunca piora a build. Parâmetro treinável. |
| `suporte.dado_multiuso.fator_acao_bonus` | 0.85 | 2026-11-23 | 463 | D6: dado multiuso entregue com ação bônus (Bardic Inspiration) disputa a ação bônus com Healing Word, Spiritual Weapon etc.: o valor é multiplicado por este fator. Uso por reação (Cutting Words, "acao": "reacao") não paga. Parâmetro treinável. |
| `suporte.dado_multiuso.reuso_max` | 2 | 2026-11-21 | 463 | Dado de vários usos que volta quando a rolagem falha mesmo assim (Unfailing Inspiration do Eloquence): o dado é reusado até virar uma rolagem (×1/chance de virar), no máximo este fator por dado (a luta acaba antes). |
| `suporte.h.ACERTO` | 0.65 | 2026-11-18 | 463 | Chance de acerto típica de um aliado. |
| `suporte.h.ACERTOS_INIM_ROUND` | 4 | 2026-11-18 | 463 | Acertos em que o dano inimigo do round chega. |
| `suporte.h.ACESSO_ACAO` | 0.8 | 2026-11-19 | 463 | Fator da cura que custa a ação (Cure Wounds) frente à de ação bônus (Healing Word). Chute inicial (19/11). |
| `suporte.h.ACESSO_TOQUE` | 0.6 | 2026-11-19 | 463 | Fator da cura de toque (Cure Wounds, Lay on Hands) frente à de distância (Healing Word): precisa chegar ao caído. Chute inicial (19/11). |
| `suporte.h.ALIADOS` | 3 | 2026-11-18 | 463 | Aliados que recebem um buff em grupo. |
| `suporte.h.ATIVO` | 0.875 | 2026-11-18 | 463 | Fração da luta em que um buff contínuo está ativo. |
| `suporte.h.CUSTO_SAVE` | 1 | 2026-11-18 | 463 | Valor de 1 ponto de save, em dano evitado relativo. |
| `suporte.h.EF_CURA` | 0.9 | 2026-11-18 | 463 | Eficiência da cura (fração que não é desperdiçada). |
| `suporte.h.EF_PVT` | 0.75 | 2026-11-18 | 463 | Eficiência de PV temporários. |
| `suporte.h.ESCOLHA` | 2.0 | 2026-11-18 | 463 | Ganho de escolher quando gastar um dado de inspiração (×). |
| `suporte.h.F_AURA` | 0.67 | 2026-11-18 | 463 | Fração dos aliados dentro de uma aura. |
| `suporte.h.F_SAVE` | 0.25 | 2026-11-18 | 463 | Fração do dano inimigo que vem por save. |
| `suporte.h.PARCELA_FRENTE` | 0.35 | 2026-11-18 | 463 | Parcela do dano inimigo que vai para um aliado da linha de frente. |
| `suporte.h.P_ACERTO_INIM` | 0.6 | 2026-11-18 | 463 | Chance de um ataque inimigo acertar um aliado. |
| `suporte.h.P_CAIDO` | 0.5 | 2026-11-19 | 463 | Aliados caídos por luta que uma cura na luta levanta (cura_na_luta). Chute inicial (19/11), a calibrar. |
| `suporte.h.TURNOS_CONDICAO` | 1.5 | 2026-11-18 | 463 | Turnos de aliado perdidos num save crítico falho. |
| `suporte.h.TURNOS_LEVANTAR` | 1.0 | 2026-11-18 | 463 | Turnos devolvidos ao levantar um caído. |
| `suporte.lutas_dia` | 4 | 2026-11-10 | 463 | Lutas por dia para diluir recursos usados ENTRE lutas ("quando": "entre_lutas": Song of Rest, PV temporário de descanso). |
| `suporte.lutas_por_descanso_curto` | 2 | 2026-11-10 | 463 | Lutas por descanso curto: recurso por descanso curto usado em combate se espalha por essas lutas. |
| `suporte.mix_dado_multiuso` | {'dano': 0.3, 'acerto': 0.25, 'ca': 0.2, 'save_dano': 0.15, 'save_critico': 0.07, 'counterspell': 0.03} | 2026-11-18 | 463 | Como um dado de inspiração é gasto em média (dano, acerto, CA, save de dano, save crítico, counterspell). Soma 1. |
| `suporte.padroes.resgate_p_evento` | 0.2 | 2026-11-18 | 463 | Chance por round de surgir uma condição que vale resgatar. |
| `suporte.padroes.resgate_p_save` | 0.45 | 2026-11-18 | 463 | Chance do aliado passar no save refeito contra uma condição (Countercharm e afins). |

<details><summary>Histórico</summary>

- `suporte.dado_multiuso.decaimento`: data 2026-11-23, de None, para 0.75, motivo D6 (usuário, 23/11): a 4ª e a 5ª inspiração não valem a 1ª; rever se o BI está superestimado.
- `suporte.dado_multiuso.fator_acao_bonus`: data 2026-11-23, de None, para 0.85, motivo D6 (usuário, 23/11): BI cobra a ação bônus.

</details>

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

