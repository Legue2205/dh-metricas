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
| 7 | Padrão: 4 lutas por dia, 2 por descanso curto, 4 rounds por luta. Cenários: `dia_padrao` e `luta_prioritaria` | 10/11 |
| 8 | **Armazenamento = o próprio Git** (`builds/` entrada, `resultados/` saída). Sem banco de dados por enquanto | 10/11 (proposta) |
| 9 | **Automação = GitHub Actions**: a cada push roda testes + `dh completo` e commita `resultados/` e `PAINEL.md` | 10/11 (proposta) |
| 10 | **Front-end = site estático** gerado dos `resultados/*.json` (Cloudflare Pages ou GitHub Pages). Sem back-end: os motores são Python/numpy com Monte Carlo, ruins para funções serverless da Vercel/Cloudflare | 10/11 (proposta) |
| 11 | Google Sheets vira opcional (espelho/exportação), não fonte da verdade | 10/11 (proposta) |

Itens 8–11 são a recomendação do Claude; o usuário ainda precisa confirmar.

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
4. **Ganchos para mecânicas exóticas**: campo genérico por eixo (ex.: `golpes_extras_a_0pv` para o "barrado"
   do Ravin, já possível via `defesa2.py`: PV efetivo += n × dano de um golpe).
5. Resolver os avisos de espaços (decisão do usuário: marcar "luta prioritária" ou dividir linhas).
6. Pendências de dados: saves de Jamal e Virgil; planos e suporte do Marcus; arquétipos e monstros.

### Fase 2 — automação (sem Claude no meio)
7. Workflow do GitHub Actions (`.github/workflows/metricas.yml`, já no repo): conferir que roda e commita.
8. `dh site`: gera `site/index.html` estático (painel, página por build, comparação) a partir de `resultados/`.
9. Publicar: Cloudflare Pages (funciona com repo privado, grátis) ou GitHub Pages (repo público ou plano pago).
10. Opcional: `dh exportar-sheets` no CI para manter as planilhas como espelho.

### Fase 3 — aplicação
11. Formulário no site para criar/editar build (gera JSON + commit pela API do GitHub).
12. Só se precisar: back-end/banco.

## Perguntas em aberto para o usuário
- Confirmar decisões 8–11. Repo público ou privado (define GitHub Pages × Cloudflare Pages)?
- Avisos de espaços: "luta prioritária" ou dividir em linhas?
- Incluir ação/concentração no orçamento agora?
