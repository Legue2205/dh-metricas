# ROADMAP e decisões — dh-metricas

> Para retomar em outra sessão: "vamos retomar o dh-metricas". Conecte o repo `Legue2205/dh-metricas`,
> leia este arquivo, o `CLAUDE.md` e o `README.md`. Tudo o que foi decidido está aqui; não dependa do chat.
> Atualize este arquivo ao fim de cada sessão (seção "Estado" e "Próximo passo").

## Objetivo

Adicionar uma build deve ser só: **discutir a build → gerar `builds/<id>.json` → commit**. O resto (validar,
rodar motores, guardar resultados, atualizar o painel) é automático, sem o Claude rodar código nem colar valores.

## Decisões tomadas

| # | Decisão | Data |
|---|---|---|
| 1 | Um repo único com todos os motores; números só vêm de `python -m dh` | 08/11 |
| 2 | Uma build = um JSON em `builds/`; nada de nome de personagem em `dh/` (motor agnóstico) | 08/11 |
| 3 | Moeda comum = nível equivalente + letra (F…S), por eixo. Eixos do card antigo (COND, FÔLEGO, MOB, alcance) retirados | 08/11 |
| 4 | Controle declarativo (`fontes`, `plano`) com biblioteca única `magias.json` | 08/11 |
| 5 | Uma linha = uma hipótese: reação e espaços de magia não contam duas vezes (`orcamento.py`). Reação duplicada = erro; espaços estourados = aviso "eixos não somam" | 10/11 |
| 6 | Shield/Uncanny Dodge são recursos finitos com decisão informada (vê o ataque/dano, pesa o resto do round). Counterspell conta em controle e em saves, não em blindagem | 10/11 |
| 7 | Padrão: 4 lutas por dia (2 prioritárias que gastam o dobro de uma comum), 2 por descanso curto, 4 rounds por luta | 10/11 |
| 7b | **Tags de orçamento automáticas por linha** (menor em que a linha cabe): `comum` (1/6 dos espaços do dia) < `prioritaria` (1/3) < `combate_unico` (dia inteiro) < `hypercharged_1.5` < `hypercharged_2.0` … (degraus de 0,5 dia). Substitui o aviso "eixos não somam" | 10/11 |
| 8 | **Armazenamento = o próprio Git** (`builds/` entrada, `resultados/` saída). Sem banco de dados por enquanto | 10/11 (confirmada) |
| 9 | **Automação = GitHub Actions**: a cada push roda testes + `dh completo` e commita `resultados/` e `PAINEL.md` | 10/11 (confirmada) |
| 10 | **Front-end = site estático** gerado dos `resultados/*.json` (Cloudflare Pages ou GitHub Pages). Sem back-end: os motores são Python/numpy com Monte Carlo, ruins para funções serverless da Vercel/Cloudflare | 10/11 (confirmada) |
| 11 | Google Sheets vira opcional (espelho/exportação), não fonte da verdade | 10/11 (confirmada) |

Itens 8–11 confirmados pelo usuário em 10/11. **Repo público → site no GitHub Pages.**

### Por que não app com back-end + banco agora
- Os dados são poucos arquivos JSON versionados: o Git já dá histórico, diff e backup.
- O cálculo leva ~1 min e precisa de numpy: cabe num job de CI gratuito, não numa função serverless.
- Site estático não tem servidor para manter nem custo.
- Se um dia for preciso editar builds por formulário: o formulário gera o JSON e abre um commit pela API do
  GitHub (ou os motores rodam no navegador com Pyodide). Só então pensar em banco (ex.: Cloudflare D1).

## Estado (10/11/2026)

Pronto e testado (37 testes): dano, defesa (com reações), saves (Resiliência/Vontade), controle (campo +
atenção + absoluto), área, suporte, orçamento de recursos, CLI (`validar`, `rapido`, `completo`, `linhas`,
`painel`), caches de régua. 16 builds migradas. Paridade com as planilhas descrita no README.

## Próximos passos (em ordem)

### Fase 1 — motor geral completo e flexível
1. **Invocações/summons como cidadãos de primeira classe.** Hoje os esqueletos do Amadeus aparecem em três
   lugares soltos (dano `medido`, fonte `esqueletos` do controle, `atencao.esqueletos`). Criar no JSON
   `"invocacoes": [{"nome", "quantidade", "pv", "ca", "ataque": {...}}]` na linha (hipótese de quantos tem) e
   fazer dano, controle de corpo e atenção lerem dali.
2. **Ação, ação bônus e concentração no orçamento** (hoje só reação e espaços).
3. **Dano calculado para todas as builds** (trocar `medido` por `ataques`); rotações com recursos.
4. **Ganchos para mecânicas exóticas**: `golpes_extras_a_0pv` (o "barrado" do Ravin) já existe na defesa;
   seguir o mesmo padrão (campo genérico no JSON) para o que aparecer.
5. ~~Avisos de espaços~~ → resolvido com as tags (7b).
6. Pendências de dados: saves de Jamal e Virgil (Caleb e Lucius já entraram); planos e suporte do Marcus; arquétipos e monstros.

### Fase 2 — automação (sem Claude no meio)
7. ~~Workflow do GitHub Actions~~: roda com sucesso a cada push (conferido em 10/11).
8. `dh site`: gera `site/index.html` estático (painel, página por build, comparação) a partir de `resultados/`.
9. Publicar no GitHub Pages (repo público), pelo próprio workflow.
10. Opcional: `dh exportar-sheets` no CI para manter as planilhas como espelho.

### Fase 3 — aplicação
11. Formulário no site para criar/editar build (gera JSON + commit pela API do GitHub).
12. Só se precisar: back-end/banco.


## Proposta: plano de orçamento do dia (10/11, aguardando confirmação)

Pedido do usuário: a decisão de como gastar os recursos é qualitativa e deve ser tomada **na discussão da
build**, escrita no JSON, e não por fração automática nem por agente no workflow.

1. **Tag = premissa diária**, poucas: `padrao` (4 combates: NP1, P1, descanso curto, NP2, P2),
   `combate_unico` (1 combate, todos os recursos) e `dia_longo` (a definir).
2. **Plano do dia no JSON**: para cada tag, a sequência de combates; cada combate diz, round a round, o que o
   personagem faz e com qual recurso ("R1 Faerie Fire 1º; R2–R4 espada"; "bárbaro: Fúria só nos prioritários").
   Também a postura (linha de frente ou não), que muda o controle de corpo/atenção daquele combate.
3. **Livro-caixa automático**: o validador desconta cada gasto do dia (espaços, pacto e ki voltam no descanso
   curto, Fúria por descanso longo, etc.). Gastar o que não tem = **erro**. O que sobra aparece como
   "sobra para utilidade". Gastar 100% é permitido (sem coeficiente de folga), mas fica visível que não há sobra.
4. **Cada combate é avaliado em todos os eixos**, com os motores atuais, a partir do que foi gasto nele.
5. **Resultado da tag padrão**: média do dia (ponderada, mais peso nos prioritários) **e** separados:
   média dos prioritários e média dos não prioritários, para ver os "picos" (ex.: Marcus com mais dano no NP e
   mais controle no P).
6. As tags automáticas `comum/prioritaria/hypercharged` saem; a comparação entre builds é sempre na mesma tag.

Etapas: (a) formato do plano + livro-caixa + agregação, reaproveitando os eixos por combate como hoje;
(b) modelo de ação round a round unificado, em que uma ação alimenta dano, controle, área e suporte ao mesmo tempo.

Perguntas: peso dos prioritários na média (2:1? 1:1?); definição do `dia_longo`; orçamento estourado é sempre
erro ou existe uma tag explícita `hypercharged`?

## Perguntas em aberto para o usuário
- Incluir ação/concentração no orçamento agora?

## Próximo passo
Fase 1, item 1 (invocações) e item 2 (ação/concentração); depois Fase 2, itens 8–9 (site).
