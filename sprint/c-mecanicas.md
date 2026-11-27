# Pacote C — mecânicas de subclasse que faltavam (27/11)

Problema #4 do DIAGNOSTICO-RAIOX.md. Cada mecânica virou tipo/campo genérico no JSON + teste
(`tests/test_mecanicas_c.py`, 8 testes) + uso no gerador do chassi e na progressão rpgbot-* da subclasse.

## Peças genéricas novas (motor)
| peça | onde | o que faz |
|---|---|---|
| área `"tipo": "ataque_area"` | `dh/horda.py` (+ área v1 em `dh/area.py`) | ação que faz uma jogada de ataque contra cada criatura de uma área (`alvos`, `bonus`, `dano`, `seletiva`, `extra_um_alvo` 1×/turno). Entra como opção "livre" do round contra a horda: só é usada quando rende mais que o dano de alvo único. |
| `patches_linhas` ampliado | `dh/build.py` | features que acompanham qualquer ação da luta: `corpo` (soma ao corpo efetivo da linha), `cobertura` {usos, volta} (buff de usos/dia espalhado: × min(1, usos do dia ÷ lutas)), `fator` (aceita `$p`), `reacao` (gasta a reação, limitada pela reação livre da linha; com reação parcial tudo cai na mesma proporção; sem reação livre o patch não entra), `anexar` (`area`, `reacao`, `suporte.fontes`), `so`/`exceto`/`desde_linha_com`. |
| suporte `fator` / `complemento` | `dh/suporte.py` | multiplica o valor da fonte (parte de um recurso dividido entre eixos; reação parcial). |
| `dado_multiuso` com `vira` e `acao: "nenhuma"` | `dh/suporte.py` | dado que substitui uma rolagem (Portent) em vez de somar; sem custo de ação bônus. |
| `dano_por_acerto` com `por_round` (+ `p_gatilho`) | `dh/suporte.py` | dano extra só no 1º acerto de aliado do round, quando o gatilho acontece (Order's Wrath). |
| `cura` com `alcance: "toque"` | `dh/suporte.py` | paga o acesso ao aliado (`suporte.h.ACESSO_TOQUE`), como `cura_na_luta`. |
| controle `forcar_falha_fator` | `dh/controle/efeitos.py` | parte dos dados de forçar falha que fica no controle (o resto vai para o suporte). |

Premissas NOVAS (eixo suporte, desde 27/11; nenhuma existente mudou): `suporte.padroes.portent_vira` 0,5,
`portent_mix` {acerto .35, ca .35, save_critico .3}, `portent_fracao_controle` 0,5, `ward_projetado_fracao` 0,5,
`ward_projetado_reacao` 0,25. (HIPOTESES.md não foi regenerado.)

## Mecânica a mecânica
1. **Hunter, Volley (11)** — `patches_linhas` anexa `ataque_area` (2 alvos: esfera de raio 10 pela tabela do DMG, seletiva,
   Colossus Slayer no 1º alvo) em todas as linhas com dano. **Efeito: área 4,6 → 4,6.** Não é bug: no 11 o Hunter tem 2
   ataques, e 2 alvos de Volley = os 2 ataques do Extra Attack (empate; com 4 alvos o teste mostra a luta mais curta). O
   4,6 igual em todas as linhas vem da regra, não de mecânica faltando. Só sobe com hordas mais agrupadas que a régua
   (cenário "agrupada" da área v1) ou num nível com Extra Attack ainda 1.
2. **Bladesong** — sai das linhas `canto` (gasto e CA próprios) e vira `patches_linhas` com `cobertura` {PB, longo} somando
   Int à CA de todas as linhas (nv7: 3/4 das lutas → +3; nv11: 4/4 → +5); `recursos.outros.bladesong` sai (é gasto pelo
   patch, não pelo livro-caixa — nada conta duas vezes). As linhas `canto*` ficam como "corpo a corpo" (Haste +2 CA à parte).
   Não precisou mexer no plano. **Efeito (misto, chassi):** defesa física 3,4 → 4,3 (7) e **6,1 → 9,6 (11)**; corpo 5,2 → 6,9 e
   8,4 → 11,5. Não modelado: a ação bônus de ligar no 1º round e +Int na concentração.
   Mudança de plano que seria necessária para fazer melhor (pacote A): deixar o plano escolher em quais lutas gastar os usos
   (hoje a cobertura é a média linear de CA; ok com PB ≥ lutas, aproximação quando PB < lutas).
3. **Projected Ward (Abjuration 6)** — `patches_linhas` em todas as linhas: reação (0,25 dos rounds, compete com Shield),
   `ward_projetado_fracao` do Arcane Ward sai do PV do abjurador e vira `pv_temporario` de um aliado. **Efeito:** suporte
   — → 0,3 (7) / 0,5 (11); defesa física 4,7 → 4,0 e 8,5 → 7,4 (é transferência: o ward já estava no PV dele).
4. **Portent (Divination)** — nas linhas com controle, `forcar_falha_fator` = `portent_fracao_controle` (0,5 dos dados) e o
   resto vira `dado_multiuso` (`vira`, sem ação) com `fator` e `complemento`; linhas sem controle põem os 2 dados/dia no
   suporte. **Efeito:** controle 7,4 → 7,0 e 12,1 → 11,2; suporte — → 0,1 / 0,2 (o mesmo dado não conta duas vezes; em nível,
   o controle perde mais do que o suporte ganha porque as réguas são diferentes — em DE é transferência).
5. **Order's Wrath (Order 8)** — `dano_por_acerto` `por_round` (2d8 no 1º acerto de aliado, gatilho = acerto da maça com
   Divine Strike) na linha `arma` do chassi. **Efeito: nenhum no plano/misto** (a linha de maça não entra; Bless + Voice of
   Authority vale muito mais). As builds rpgbot-cleric-order* usam truque (Blessed Strikes), sem gatilho RAW: não entra.
   **Protective Field (Psi Warrior 3)** — linha nova `campo-protetor`: os dados psiônicos da luta vão para a reação (dado + Int
   num golpe contra um aliado, `pv_temporario`) em vez do Psionic Strike. **Efeito:** suporte — → 0,3 (11); dano 8,7 → 8,4 (11).
   **Hand of Healing (Mercy 3)** — linha nova `mao-cura`: Flurry nos 4 rounds com um golpe trocado por Hand of Healing (até
   P_CAIDO levantam caídos, o resto é cura de toque) + Physician's Touch (6) tirando condição. **Efeito:** suporte 0,3 → 0,6 (7)
   e **0,7 → 4,2 (11)**; dano 9,1 → 8,0 (11, o plano troca golpes por cura); corpo 9,4 → 11,0.

## Medição (comparar_chassi.py --sem-holdout --json, meta_consenso.py; 57 builds recalculadas com dh completo)
| gate | nv7 antes → depois | nv11 antes → depois |
|---|---|---|
| G1 dano τ pista (n 54) | 0,36 → 0,36 | 0,38 → 0,38 |
| G1 deff τ pista (n 19) | 0,60 → 0,60 | 0,58 → 0,58 |
| G1 controle τ pista (n 22/25) | 0,66 → 0,66 | 0,61 → 0,59 |
| G1 suporte τ pista (n 16) | 0,38 → 0,38 | 0,37 → 0,37 |
| suporte agrupado | 0,39 → 0,41 | 0,33 → 0,38 |
| área agrupado (G2) | 0,52 → 0,52 | 0,58 → 0,58 |
| corpo agrupado (G2) | 0,19 → 0,19 | 0,21 → 0,21 |
| τ eixo × nota (deff) | 0,14 → 0,10 | 0,14 → 0,09 |
| τ eixo × nota (suporte) | 0,02 → 0,07 | 0,03 → 0,07 |
| τ por classe (nota × 5 eixos) | — | fighter 0,56 → 0,51 (n 10); wizard 0,03 → 0,00 (n 13) |
| G3 | corpo fundo 2 → 3/10 | **deff passa** (fundo 7 → 8/10, 1 → 0 forte); corpo fundo 2 → 3/10 mas 1 forte |
Nenhum gate caiu mais de 1 erro-padrão. Os G1 de suporte não se mexem porque nenhuma das subclasses mudadas tem pista de
suporte que tenha virado par novo; o ganho aparece no agrupado e na nota.

## Outros
- `ferramentas/geradores/c_mecanicas.py`: aplica as mecânicas nas progressões rpgbot-* cujos geradores não reproduzem mais
  o arquivo (wiz_builds.py e fighter_lote2.py: rodar por cima desfaz edições à mão). Idempotente.
- `m3_sobrevivencia.aplicar` passou a preservar patches de outras origens; `chassi.escrever`, `marcial.escrever` e
  `wiz.escrever` levam `patches_linhas` por nível.
- **Bug achado:** `wiz.py`, `fighter_lote2.py`, `puro_fighter.py` e `p2.py` gravavam num caminho absoluto de outro clone;
  agora relativos à raiz.
