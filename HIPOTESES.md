# Bíblia de hipóteses (gerada de premissas/premissas.json — não editar à mão)

Cada premissa é um "peso" do modelo. Mudar: `python -m dh premissa <nome> <valor> --motivo "..."`; depois `python -m dh completo 'builds/*.json'` recalcula só quem usa.

## controle

| Premissa | Valor | Desde | Builds que usam | O que é |
|---|---|---|---|---|
| `controle.peso_no_controle.ameaca` | 0.0 | 2026-11-16 | 13 | Taunt soft (corpo que atrai ataques): só Corpo. |
| `controle.peso_no_controle.esqueletos` | 0.0 | 2026-11-16 | 1 | Invocações que desviam ataques: só Corpo. |
| `controle.peso_no_controle.parada_oa` | 0.5 | 2026-11-18 | 1 | Igual à do Sentinel, para paradas por ataque de oportunidade com probabilidade fixa. |
| `controle.peso_no_controle.sentinela` | 0.5 | 2026-11-18 | 1 | Fração da negação do AO do Sentinel (velocidade 0) que também conta como Controle. O resto (taunt, diluição de dano) fica só no Corpo. |

<details><summary>Histórico</summary>

- `controle.peso_no_controle.parada_oa`: valor 0.0, ate 2026-11-18
- `controle.peso_no_controle.parada_oa`: valor 0.5, desde 2026-11-18, motivo mesma decisão do Sentinel
- `controle.peso_no_controle.sentinela`: valor 0.0, ate 2026-11-18, motivo 16/11: fontes de corpo fora do Controle (evitar contagem dupla)
- `controle.peso_no_controle.sentinela`: valor 0.5, desde 2026-11-18, motivo usuário: negar movimento só precisando acertar a CA é controle real (como o Plant Growth), mas parte do valor já está no Corpo

</details>

## planos

| Premissa | Valor | Desde | Builds que usam | O que é |
|---|---|---|---|---|
| `plano.peso_prioritaria` | 2 | 2026-11-10 | 0 | Peso de uma luta prioritária na média do dia (não prioritária = 1). Ainda lido de planos.TAGS; migrar. *(ainda no código)* |

## suporte

| Premissa | Valor | Desde | Builds que usam | O que é |
|---|---|---|---|---|
| `suporte.lutas_dia` | 4 | 2026-11-10 | 3 | Lutas por dia para diluir recursos usados ENTRE lutas ("quando": "entre_lutas": Song of Rest, PV temporário de descanso). |
| `suporte.lutas_por_descanso_curto` | 2 | 2026-11-10 | 2 | Lutas por descanso curto: recurso por descanso curto usado em combate se espalha por essas lutas. |
