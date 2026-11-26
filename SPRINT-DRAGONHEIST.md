# Sprint DragonHeist — até a sessão de 8/12 (plataforma pronta em 30/11; party e Kael de 1 a 7/12)

Pergunta que a plataforma precisa responder com segurança: **"o Kael (Blood Monk, homebrew) está equilibrado com a
party da DragonHeist em dano, cura/sobrevivência e no geral — e que ajuste no homebrew o deixaria no alvo?"**
Contexto do usuário (26/11): na última sessão ele aplicou uma leve mudança no homebrew e acha que "passou a mão um
pouco" na cura e no dano. O texto do homebrew está no Drive (documento do Blood Monk, ao lado das notas da party).

## Como este roadmap funciona (revisado 26/11, 01h53 — usuário)
Os marcos são **gates medidos**, não listas de mecânicas. As mecânicas genéricas que faltam (autocura com limiar,
recurso tipo fúria, bônus que escala…) vão ser descobertas investigando por que uma métrica não passa — por que o τ do
suporte está baixo, por que o topo do corpo é o que é — no mesmo ciclo do deep dive do dano: **medir → achar a
inconsistência → diagnosticar o problema estrutural → corrigir de forma genérica → medir de novo**. Regras:
- **Os gates estão congelados (pré-registro, 26/11).** Mudar um gate só com decisão do usuário registrada aqui.
- Uma correção não pode derrubar outro gate que já passa em mais de 1 erro-padrão (~0,08 com n ≈ 70; ~0,15 com n ≈ 20).
- Descoberta que não move nenhum gate vai para "depois do sprint".
- **Holdout congelado:** Artificer, Rogue e Sorcerer NÃO são olhados para decidir mudanças a partir de 26/11 (os
  scripts de análise devem aceitar `--sem-holdout`); só entram na medição final do G6.
- Medição oficial: `python calibracao/comparar_chassi.py --nivel 7|11` (visão misto; dano com pacote_vh).

## Estrela do norte — gates (valores de 26/11 → alvo; nv7 / nv11)
| gate | métrica | hoje | alvo |
|---|---|---|---|
| **G1 réguas com pista** | τ pista dentro da classe | dano 0,34 / 0,40 · controle 0,68 / 0,65 · suporte 0,32 / 0,31 · defesa física 0,45 / 0,44 | dano ≥ 0,40 · controle ≥ 0,60 · **suporte ≥ 0,45** · defesa física ≥ 0,45 (nos dois níveis) |
| **G2 réguas sem pista suficiente** | τ agrupado (entre classes) | área 0,47 / 0,61 · corpo 0,16 / 0,07 · defesa mental — | área ≥ 0,45 · **corpo ≥ 0,35** · defesa mental medida |
| **G3 meta faz sentido** | top-10 / fundo-10 de cada eixo contra a lista de consenso (`calibracao/meta-consenso.json`, rascunho do Claude aprovado pelo usuário ANTES de olhar os resultados) | — | ≥ 7 dos 10 primeiros na lista "forte" e 0 na lista "fraco", em cada eixo e nos dois níveis |
| **G4 global** | τ da nota geral do RPGBot × valor total em dano equivalente (P3), dentro da classe | 0,13 no nv7 (média de 5 eixos iguais, a referência atual) | **≥ 0,40** nos dois níveis e agrupado ≥ 0,30 |
| **G5 robustez** | τ entre os rankings nos extremos da faixa das premissas provisórias (k_abate, tempo da área, fração viva, acertos por posição, modo de focus fire) | — | ≥ 0,85 por eixo e no global; nenhum top-10 troca mais de 3 builds |
| **G6 generalização** | holdout (Artificer, Rogue, Sorcerer) e baseline ingênuo (só DPR; média de eixos iguais) | — | holdout ≥ τ do treino − 1 erro-padrão; global ganha dos dois baselines por ≥ 0,08 |
| **G7 engenharia** | testes; empates inexplicados; o Kael rodando sem nada estimado à mão | site já falhava | testes verdes; ≤ 10% das subclasses em empate com pistas discordantes por eixo; fumaça do Kael com `nao_modelado` vazio nos itens que afetam eixos |

## Calendário (plataforma até 30/11; party e Kael em dezembro)
Decisão do usuário (26/11): **fechar a plataforma primeiro, sem olhar a party**; a análise do Kael em dezembro.
- **26–27/11:** G3 (lista de consenso — rascunho na primeira sessão, para o usuário aprovar de manhã) e G1/G2 nas
  réguas de suporte e corpo (é aqui que as mecânicas genéricas faltantes devem aparecer).
- **28–29/11:** P3 = valor total em dano equivalente para qualquer build → G4 e G5.
- **30/11:** G6 (holdout e baseline, medidos uma vez) e G7 (fumaça do Kael: rodar a build dele como está só para ver se
  a plataforma responde; se faltar mecânica, volta para as réguas ainda em novembro).
- **1–2/12 (K1):** party no pipeline (plano automático, dias de foco, concentração, moeda), versão NOVA do homebrew do
  Kael (pedir o texto), Stunning Strike; 1 linha por personagem para o usuário conferir.
- **3–5/12 (K2):** comparação geral da party com faixa; variantes do Kael (cura ±, dano ±, usos de Blood Rage, limiar)
  contra o alvo do usuário; relatório com a recomendação.
- **6–7/12:** folga.

## Depois do sprint
- Pacotes para casters (blaster × controlador, Hexblade), lista expandida dos Warlocks, holdout + baseline ingênuo.
- Abate como métrica própria de "fechar luta" (fase 2); treino de k_abate / tempo da área / fração viva.
- Summon talvez subvalorizado depois de D18 (pêndulo) — ver com mais pistas.
