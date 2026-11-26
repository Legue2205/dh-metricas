# Sprint DragonHeist — até a sessão de 8/12 (meta: pronto em 30/11, folga de 1 a 7/12)

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
**M1 — Blood Monk no motor (26–27/11).** A mecânica do Kael simulada, não estimada à mão: autocura com limiar de vida
(Blood Eating, 75–80%), Blood Rage como recurso (3 por dia, como fúria) curando acima do limiar, 3 Blood Dice (1 volta no
descanso curto), combo que escala durante a luta ("bônus que escala", ROADMAP item 5) — tudo como **tipos de campo
genéricos** (servem para Barbarian, Paladin, Fighter), nada com nome de personagem em `dh/`. Aplicar a versão NOVA do
homebrew (pedir/ler no Drive). Saída: linhas do Kael calculadas pelo motor; paridade com a planilha/impressão do
usuário explicada; testes.

**M2 — Party no pipeline atual (27–28/11).** As builds da DragonHeist (Kael, John, Tin Bin, Abdul, Marcus, Amadeus,
Ravin) com plano automático + dias de foco + concentração + moeda DE; revisar as hipóteses abertas (Stunning Strike do
Kael, Amadeus com `pesos_invocacao`). Saída: painel da party regenerado e um resumo de 1 linha por personagem "o que o
plano manda fazer" para o usuário conferir se faz sentido de mesa.

**M3 — Réguas que a pergunta usa (28–29/11).** As réguas de dano, defesa/sobrevivência (incluindo autocura) e corpo
coerentes para a comparação do Kael: Monks diferenciados (hoje empatam no dano; τ do Monk fraco), autocura comparável
entre classes (Kael × Second Wind × Lay on Hands × fúria). Saída: τ do Monk ≥ 0 sem empate inexplicado; defesa física
≥ 0,40 nos dois níveis; tabela de autocura por classe que o usuário reconheça.

**M4 — Comparação geral mínima (29/11).** Fase 2 só no que a pergunta precisa: valor total por luta em dano
equivalente (dano convertido + dano evitado + corpo + cura) para cada personagem da party, com faixa de incerteza
(variar `moeda.k_abate`, `moeda.tempo_area`, `invocacao.fracao_viva`, `concentracao.acertos_por_round`, modo de focus
fire). Saída: ranking da party com faixa; conclusões só valem se se mantêm em toda a faixa.

**M5 — Experimentos no homebrew (30/11).** Variantes do Kael (cura ±, dano ±, usos de Blood Rage, limiar) varridas no
motor; alvo de equilíbrio definido com o usuário (ex.: dentro de ±1 nível da média da party em cada eixo e no total em
DE). Saída: relatório curto com a recomendação, as alternativas e o quanto cada uma move cada eixo.

**Folga (1–7/12):** revisão do usuário, imprevistos, descobertas de última hora, preparação da sessão.

## Depois do sprint
- Pacotes para casters (blaster × controlador, Hexblade), lista expandida dos Warlocks, holdout + baseline ingênuo.
- Abate como métrica própria de "fechar luta" (fase 2); treino de k_abate / tempo da área / fração viva.
- Summon talvez subvalorizado depois de D18 (pêndulo) — ver com mais pistas.
