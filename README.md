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

## Paridade com as planilhas (09/11/2026)

Builds migradas: Abdul, Kael, Amadeus, John, Tin Bin, Ravin, Marcus, Fjord, Miau, Caleb, Lucius,
O Aprendiz, Pyotr, Solaris, Jamal, Virgil (+ um guerreiro de exemplo com dano calculado).

| Eixo | Situação |
|---|---|
| Dano: nível eq a partir dos 9 DPRs | idêntico em todas as linhas testadas |
| Dano: DPR a partir dos ataques | motor novo em fórmula fechada; as linhas antigas entram como `medido` |
| Defesa | idêntica em todas as linhas sem reação (incluindo o Heavy Armor Master do Abdul, depois de corrigir o nº de atacantes da horda). Linhas com Shield/Uncanny Dodge/Evasion/barrado entram como `medido` |
| Controle relativo e absoluto | 14 builds dentro de 0,4 nível. **Divergem**: Ravin (7,2 × 7,7, só no encontro Minions + minibosses, onde a régua é extrapolada acima do teto) e Solaris (8,8 × 7,5, valor da planilha veio de uma versão anterior do script) |

## Ainda fora do repo (próximos passos)

- Área, Suporte, Resiliência e Vontade: os motores não estavam salvos no Drive; continuam na planilha.
- Marcus: as linhas de controle "luta prioritária, orçamento real" e "média do dia" eram de um script
  que não está no Drive; reescrever como `plano`.
- Migrar arquétipos e monstros de referência (hoje só nas planilhas).
- Defesa: modelar reações (Shield, Absorb Elements, Uncanny Dodge, Evasion) e trocar os `medido`.
- Dano: rotações com recursos e GWM/SS condicional à CA no motor de fórmula fechada.
- Ligar a skill `dnd-build-rapido` a este repo, para que ela gere o `build.json` em vez do formato próprio dela.
