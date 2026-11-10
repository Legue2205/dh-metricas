# dh-metricas

Motores das métricas de builds de D&D 5e (2014) da DragonHeist, num lugar só. Uma build é **um arquivo
JSON** em `builds/`; os motores leem esse arquivo e devolvem nível equivalente e letra por eixo, no mesmo
padrão das planilhas de rank.

```
python -m dh validar 'builds/*.json'
python -m dh rapido   builds/kael-7.json     # segundos: dano + defesa + controle relativo (N=2000)
python -m dh completo builds/kael-7.json     # + controle absoluto nos 10 níveis de teste (N=8000)
python -m dh linhas   builds/kael-7.json     # linhas prontas para colar nas planilhas
python -m dh painel                          # resumo de tudo que já foi calculado
python -m pytest -q                          # paridade com as planilhas
```

Só precisa de Python 3.10+ e numpy (`pip install -e .`).

## Estrutura

```
dh/
  base.py            tabelas comuns: CR do Monster Manual, perfis, topologias, encontros do DMG, rampa de letras
  build.py           carregar / validar build.json, impressão digital
  orcamento.py       recursos por hipótese: a reação não conta duas vezes; soma o gasto de cada linha
  planos.py          plano do dia: livro-caixa de recursos, média do dia e por categoria de combate
  saves.py           Resiliência e Vontade (Monte Carlo contra um conjurador pleno)
  area.py            fração da horda removida → nível eq
  suporte.py         dano equivalente por round (fórmula fechada)
  dano.py            DPR em 9 CAs (fórmula fechada ou "medido") → nível eq pelas rampas da planilha de dano
  defesa.py          Blindagem (horda) e Durabilidade (boss) → nível eq
  controle/
    magias.json      biblioteca de efeitos (peso, save, término) — usada pelos personagens E pela régua
    campo.py         negação de turnos (Monte Carlo vetorizado)
    atencao.py       para onde vão os ataques (determinístico)
    efeitos.py       controle declarativo: "fontes" do JSON → função de negação
    total.py         campo + atenção em "vidas poupadas", calibrado contra o conjurador de referência
  motor.py           orquestra uma build e grava resultados/<id>.json
  cli.py             comandos acima
builds/              uma build por arquivo (fonte da verdade)
cache/               régua de controle pronta (regua-<hash>.json); refeita sozinha se o motor mudar
resultados/          saída por build; só é recalculada se o JSON ou a versão do motor mudar
tests/               paridade com as planilhas
```

## Caminho de uma build nova

1. Ler a ficha **uma vez** e escrever `builds/<id>.json` (copie um parecido).
2. `python -m dh validar builds/<id>.json`
3. `python -m dh rapido builds/<id>.json` para conferir; `completo` quando for para a planilha.
4. `python -m dh linhas builds/<id>.json` e colar cada bloco na planilha indicada (as colunas de
   fórmula ficam como estão). Com `--json`, sai a lista {planilha, aba, células} que o Claude escreve
   direto pelo conector do Sheets (procedimento em `dh/planilhas.py`). O Painel central já pega pelo ID.

Só a build nova roda. A régua do conjurador de referência (a parte cara do controle) já está em `cache/`.

## Formato do build.json

```jsonc
{
  "id": "kael-7", "nome": "Kael", "grupo": "Party", "nivel": 7,
  "build": "Way of the Blood Monk 7 (homebrew), Des 18",
  "corpo": {"ca": 17, "pv": 79, "res": 1, "adv": 0, "red": 0},   // res: fator de dano (0,5 = resistência)
  "linhas": [                                                      // cada linha = uma hipótese
    {"id": "principal", "principal": true, "hipotese": "…",
     "dano":     {...},
     "defesa":   {...},
     "controle": {"atencao": {...}, "fontes": [...]}}
  ]
}
```

Uma linha pode ter só alguns eixos (ex.: uma linha só de defesa para "postura de tanque").

### dano

```jsonc
"dano": {
  "ataques":   [{"n": 2, "bonus": 7, "dano": "1d8+6", "crit_em": 19, "vantagem": 0.0},
                {"n": 0.5, "bonus": 7, "dano": "1d8+6"}],          // n fracionário: Action Surge 2 ataques ÷ 4 rounds
  "por_turno": [{"dano": "4d6"}],                                   // Sneak Attack: 1× por turno no 1º acerto
  "por_luta":  [{"usos": 2, "dano": "2d8"}],                        // smites: usos por luta ÷ 4 rounds, no acerto
  "automatico": "3d6"                                               // dano sem rolagem
}
// ou, para linhas antigas: "dano": {"medido": [9 DPRs em CA 11,12,15,16,18,20,22,24,25]}
```

### defesa

`{"pv_efetivo": 98, "ca": 21, "adv": -1, "resist": true, "red": 3}` — tudo opcional (vem do `corpo`).
`adv: -1` = ataques contra ele com desvantagem (Dodge, Patient Defense). `red` = redução fixa por golpe
(Heavy Armor Master), que não vale contra boss de CR 10+ (golpes mágicos).

Para o que o motor ainda não modela (Shield, Absorb Elements, Uncanny Dodge, Evasion, "barrado"):
`"defesa": {"medido": {"blindagem": 9.87, "durabilidade": 7.74}, "nota": "por quê"}`.

`"principal"` numa linha pode ser `true` (todos os eixos dela) ou uma lista, ex. `["defesa"]`, quando a
linha principal da planilha difere por eixo. Uma linha pode sobrescrever o corpo: `"corpo": {"adv": -1}`.

### controle

`atencao` descreve o personagem na party de referência: `papel` (tank, striker, atirador, conjurador),
`dpr`, `soft` (ameaça), `front`, `acc_m`/`acc_r` (chance de ser alcançado em campo aberto/ruínas/dungeon),
`conc`, `hard` (`{"sentinela": 8}` ou `{"p": 0.5}`), `esqueletos`, `agarra`.

`fontes` é a lista do que o personagem faz. Exemplos reais:

```jsonc
{"tipo": "area", "magia": "conquering_presence", "cd": 13, "so_corpo_a_corpo": true}     // Abdul
{"tipo": "sentinela", "bonus": 8}
{"tipo": "ameaca"}
{"tipo": "ataque_com_save", "bonus": [9, 9, 7, 7], "cd": 14, "save": "Con", "penalidade_por_round": 1}  // Kael
{"tipo": "alvo_unico", "cd": 14, "slots": [3, 3, 3, 2], "magias": ["bestow_curse", "ray_of_enfeeblement"],
 "modo": "melhor", "sobre": {"ray_of_enfeeblement": {"ataque": 6}}}
{"tipo": "melhor_de", "opcoes": [{...}, {...}]}       // concentração exclusiva: fica a que mais nega
{"tipo": "plano", "cd": 17, "penalidade": {"dado": 10},                                     // Virgil
 "acoes": [{"round": 1, "magia": "hold_person", "alvos": 3, "penalidade": "primeiro"},
           {"round": 2, "magia": "synaptic_static", "alvos": 4, "escala_area": true},
           {"round": 3, "magia": "psychic_lance", "selecao": "livre", "penalidade": "todos"},
           {"round": 4, "magia": "command", "alvos": 3}],
 "penalidade_manutencao": {"rounds": [2, 4]},
 "solo": {"magia": "hold_person"}}
```

Outros tipos: `terreno` (Plant Growth), `parada_oa` (Caleb), `alvo_unico_direto` (Wall of Force num alvo).
Casos especiais já registrados: `esqueletos`, `agarrao`, `ancestral_protectors`, `command_fixo`,
`ataque_nega_turno`. Mecânica nova = um tipo novo em `controle/efeitos.py` + um teste, nunca código
solto num chat.

Magia nova: uma linha em `controle/magias.json` (`peso` = fração do turno negada; `termino` =
`fim_turno` | `inicio_turno` | `luta` | `escape` | `um_turno`). Mudar a biblioteca invalida a régua
(o hash muda) e ela é refeita na próxima execução (~30 s para os 10 níveis).

## Uma linha = uma hipótese (orçamento de recursos)

Nenhum recurso é contado duas vezes dentro de uma linha (`dh/orcamento.py`):

- **Reação.** A linha declara onde a gasta: `"reacao": [{"uso": "2º Sneak", "fracao": 1.0, "eixos": ["dano"]}]`.
  A soma das frações não passa de 1 (erro). O que sobra é o que Shield, Uncanny Dodge, Absorb Elements e
  Counterspell podem usar. Fontes de controle que usam reação (`sentinela`, `parada_oa`, `counterspell`,
  `atencao.hard`) exigem um uso declarado com `"controle"` em `eixos` (erro se faltar).
- **Espaços de magia e outros recursos** são decididos no **plano do dia** (abaixo), não por fração automática.
- Recursos diários no dano e no suporte: `usos_dia` (repartido pelas lutas) em vez de `usos`.

## Plano de orçamento do dia (`dh/planos.py`)

A decisão de como gastar recursos é da build e fica escrita no JSON. **Tag = premissa diária**:

| Tag | Combates (peso) |
|---|---|
| `padrao` | NP(1) · P(2) · descanso curto · NP(1) · P(2) |
| `combate_unico` | 1 combate, todos os recursos |
| `dia_longo` | 1 · 1 · 2 · SR · 1 · 2 · 2 · SR · 2 · 4 (1 = não prioritário, 2 = moderado, 4 = boss) |

```jsonc
"recursos": {"espacos": {"1": 4, "2": 3, "3": 3, "4": 1},        // "espacos_volta": "curto" para pacto
             "outros": {"furia": {"qtd": 3, "volta": "longo"}, "ki": {"qtd": 7, "volta": "curto"}}},
"linhas": [{"id": "marcial", ...},
           {"id": "caster", "herda": "marcial", "usa": {"furia": 1}, "controle": {...}}],   // herda o que não declarar
"planos": {"padrao": {"combates": ["marcial", "caster", "marcial", {"linha": "caster", "nota": "gasta o que sobrou"}]},
           "combate_unico": {"combates": ["caster"], "hypercharged": 1.5}}   // hypercharged = acesso a mais recursos
```

- Cada combate aponta para uma linha (hipótese). O **livro-caixa** desconta o que a linha gasta (espaços lidos
  dos eixos + `usa`), devolve no descanso curto o que tem `volta: curto`, e **recusa** o plano se faltar recurso
  (a não ser com `hypercharged`). `"gasta": {...}` no combate sobrescreve o gasto lido da linha.
- O que sobra no fim do dia aparece como **sobra para utilidade** (gastar 100% é permitido; fica visível).
- Resultado por eixo: **média do dia** ponderada pelo peso e a **média por categoria** (np, p, mod, boss).
  Eixo ausente em alguns combates conta 0 neles. `dh painel [tag]` compara as builds na mesma tag.

## Invocações

`"invocacoes": [{"nome": "esqueletos", "quantidade": 7, "pv": 19, "ca": 16, "cobertura": 2,
"ataque": {"bonus": 4, "dano": "1d6+5"}}]` na linha (é a hipótese de quantas criaturas há). Entram sozinhas no
controle de corpo (atraem ataques até o PV acabar), na atenção e, quando o dano é calculado, no DPR.

## Os outros eixos

**Defesa com reações** — `"defesa": {"reacoes": [{"tipo": "shield", "usos_luta": 1}, {"tipo": "uncanny_dodge"},
{"tipo": "reduz_dano", "valor": 8}]}`. Simulação golpe a golpe: o personagem vê o total do ataque (Shield) e o
dano rolado (Uncanny Dodge) antes de decidir, pesa os golpes que ainda vêm no round, e o limiar de uso é
otimizado. `adv_por_round: [-1,-1,-1,0]` para posturas que não duram a luta toda.

**Saves** (Resiliência e Vontade) — bônus em `corpo.saves.sv`; a linha só sobrescreve:
`"saves": {"cura_round": 5, "ataques": 4}`. Campos: `adv`, `evasion`, `res`, `imune`, `absorb`, `contra`
(+ `contra_mod`, `contra_nivel`), `rerolagens`, `stillness`, `conjurador`, `barrado`, `bonus_prob`.

**Área** — lista de áreas; vale a melhor na horda padrão (saem também esparsa e agrupada):
`{"nome": "Fireball", "usos": [{"alvos": 4, "dano": "8d6", "cd": 14, "slot": 3}]}`, `"tipo": "prioritaria"`
(compara com 3 usos da referência), `cleave_ataque`, `cleave_save`. Opções do uso: `seletiva`, `metade`,
`dobra_maior_dado`, `extra_sem_save`.

**Suporte** — `{"fontes": [{"nome", "lado": "of"|"def", "modelo", ...}]}`; modelos: `vantagem`,
`bonus_continuo`, `bonus_por_uso`, `ataque_extra`, `dano_por_acerto`, `cura`, `pv_temporario`, `aura_saves`,
`valor_por_luta`, `fixo`.

**Dano** — novos campos de ataque: `"elven_accuracy": true`, `"poder": [-5, 10]` (GWM/Sharpshooter: usa o modo
que rende mais em cada CA); `por_luta` aceita `usos_dia`.

**Controle** — nova fonte `counterspell` (`usos_luta`, `slot`, `mod`): nega turnos de conjuradores inimigos.

## Paridade com as planilhas (10/11/2026)

Builds migradas: Abdul, Kael, Amadeus, John, Tin Bin, Ravin, Marcus, Fjord, Miau, Caleb, Lucius,
O Aprendiz, Pyotr, Solaris, Jamal, Virgil (+ um guerreiro de exemplo com dano calculado).

| Eixo | Situação |
|---|---|
| Dano: nível eq a partir dos 9 DPRs | idêntico em todas as linhas testadas |
| Dano: DPR a partir dos ataques | motor novo em fórmula fechada; as linhas antigas entram como `medido` |
| Defesa | idêntica em todas as linhas sem reação (incluindo o Heavy Armor Master do Abdul, depois de corrigir o nº de atacantes da horda). Linhas com Shield/Uncanny Dodge/Evasion/barrado entram como `medido` |
| Controle relativo e absoluto | 14 builds dentro de 0,4 nível. **Divergem**: Ravin (7,2 × 7,7, só no encontro Minions + minibosses, onde a régua é extrapolada acima do teto) e Solaris (8,8 × 7,5, valor da planilha veio de uma versão anterior do script) |
| Saves | idêntico (Abdul 6,07 / 8,03; motor copiado do original, mesmas sementes) |
| Área | idêntico (Fireball do Amadeus 8,1; Shatter 4,02) |
| Suporte | idêntico à especificação (régua e linhas de checagem) |
| Defesa com reações | **modelo novo** (política ótima de Shield/Uncanny Dodge, usos finitos): não é para bater com a planilha antiga |

## Pendências

- Ação e concentração ainda não entram no orçamento (só reação, espaços e recursos nomeados).
- **Planos do dia dos conjuradores** (Marcus, Amadeus, Ravin, Solaris, Virgil, Pyotr, John, Abdul): decidir na discussão de cada build.
- Ravin: defesa com "barrado" segue `medido` (o `defesa2.py` original não foi recuperado).
- Marcus: planos de controle "luta prioritária"/"média do dia" e linhas de suporte dia/comum/prioritária.
- Saves de Caleb, Lucius, Jamal e Virgil; arquétipos e monstros de referência.
- Linhas de dano `medido` → calculadas (exige os ataques de cada ficha).
- `dh linhas` ainda só gera dano, defesa e controle para as planilhas.
