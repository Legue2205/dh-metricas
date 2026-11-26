# Sprint DragonHeist — até a sessão de 8/12 (plataforma pronta em 30/11; party e Kael de 1 a 7/12)

Pergunta que a plataforma precisa responder com segurança: **"o Kael (Blood Monk, homebrew) está equilibrado com a
party da DragonHeist em dano, cura/sobrevivência e no geral — e que ajuste no homebrew o deixaria no alvo?"**
Contexto do usuário (26/11): na última sessão ele aplicou uma leve mudança no homebrew e acha que "passou a mão um
pouco" na cura e no dano. O texto do homebrew está no Drive (documento do Blood Monk, ao lado das notas da party).

## Como este roadmap funciona
Não é uma lista de tasks: é uma sequência de **marcos com critério de saída**. Dentro de cada marco o trabalho segue o
ciclo que já funcionou no deep dive do dano: **medir → achar a inconsistência → diagnosticar o problema estrutural →
corrigir de forma genérica (premissa, tipo de campo, gerador) → medir de novo**. As tasks nascem das inconsistências e
vão para o TASKS.md do marco. Regras:
- **Caminho crítico primeiro.** Uma descoberta que não muda a resposta sobre o Kael vai para "depois do sprint"
  (seção no fim deste arquivo), com uma linha de por quê.
- **Timebox.** Cada marco tem um dia-alvo; se estourar em mais de meio dia, parar e reavaliar o escopo com o usuário.
- **Não quebrar o que já passa.** Os gates atuais são o piso (abaixo); regressão maior que 1 erro-padrão (~0,08) bloqueia.
- **Toda conclusão sobre o Kael vem com faixa de sensibilidade** (premissas provisórias variadas), não um número só.

Piso atual (25/11, misto, τ contra o RPGBot nv7 / nv11): dano 0,34 / 0,40 · controle 0,68 / 0,65 · suporte 0,32 / 0,31 ·
defesa física ~0,40 / 0,44. Testes: `python -m pytest -q --deselect tests/test_site_navegador.py` (o teste do site já
falhava antes do sprint).

## Marcos
Decisão do usuário (26/11, 01h49): **fechar a plataforma primeiro (até 30/11) sem olhar a party**; a análise do Kael
fica para dezembro, com o produto final. A party só aparece antes disso num teste de fumaça (P4).

### Plataforma (26–30/11)
**P1 — Mecânicas genéricas que faltam (26–27/11).** Tipos de campo genéricos (nada com nome de personagem em `dh/`):
autocura com limiar de vida (cura só abaixo/acima de X% do PV), recurso tipo fúria com usos por dia e efeito
enquanto ativo, dados de recurso que voltam no descanso curto, bônus que escala durante a luta (ROADMAP item 5).
Validar em builds de referência que já usam isso de verdade (Barbarian, Fighter Second Wind, Paladin Lay on Hands,
Monk). Saída: testes + 2–3 builds de referência usando os campos novos.

**P2 — Réguas de sobrevivência e suporte (27–28/11).** Defesa física/mental, corpo e suporte coerentes como o dano e
o controle ficaram: autocura comparável entre classes, Monks diferenciados (hoje empatam no dano; τ do Monk fraco),
suporte fora do platô de 0,32. Saída: defesa física ≥ 0,40 e suporte ≥ 0,35 nos dois níveis (ou a explicação de por
que a pista do RPGBot não mede isso), τ do Monk ≥ 0 sem empate inexplicado.

**P3 — Comparação geral mínima (fase 2, 28–29/11).** Valor total por luta em dano equivalente (dano convertido + dano
evitado + corpo + cura + controle) para qualquer build, com **faixa de incerteza** (variar `moeda.k_abate`,
`moeda.tempo_area`, `invocacao.fracao_viva`, `concentracao.acertos_por_round`, modo de focus fire). Saída: comando que
dá o total com a faixa; checagem de sanidade nos chassis (o topo e o fundo fazem sentido de mesa).

**P4 — Validação e fumaça (29–30/11).** Holdout (classes que não foram usadas para ajustar premissas) e baseline
ingênuo (ex.: só DPR, ou só "tem Extra Attack") — a plataforma tem de ganhar dos dois. **Teste de fumaça com o Kael:**
rodar a build dele como está, sem ajustar nada, só para ver se a plataforma consegue responder a pergunta (se faltar
mecânica, volta para P1 antes de 30/11, não em dezembro). Saída: relatório "plataforma pronta" com os gates.

### Party e Kael (1–7/12)
**K1 — Party no pipeline (1–2/12).** As builds da DragonHeist (Kael, John, Tin Bin, Abdul, Marcus, Amadeus, Ravin)
com plano automático + dias de foco + concentração + moeda; versão NOVA do homebrew do Kael (pedir o texto); revisar
Stunning Strike. Saída: 1 linha por personagem "o que o plano manda fazer" para o usuário conferir.
**K2 — Análise e experimentos (3–5/12).** Comparação geral da party com faixa; variantes do Kael (cura ±, dano ±,
usos de Blood Rage, limiar) contra o alvo que o usuário definir. Saída: relatório com a recomendação.
**Folga (6–7/12).**

## Depois do sprint
- Pacotes para casters (blaster × controlador, Hexblade), lista expandida dos Warlocks, holdout + baseline ingênuo.
- Abate como métrica própria de "fechar luta" (fase 2); treino de k_abate / tempo da área / fração viva.
- Summon talvez subvalorizado depois de D18 (pêndulo) — ver com mais pistas.
