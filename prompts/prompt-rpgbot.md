# Prompt — build de referência (RPGBot e afins) em .md compacto com progressão

Uso: cole este prompt numa IA (Gemini, Claude…) junto com o guia/handbook da build. A saída é **um .md por build**,
salvo na pasta do Drive "Builds RPG/Biblioteca de builds .md/rpgbot/". O Claude lê esse .md (não o guia) e gera
`progressoes/<id>.json`; `dh expandir` cria uma build por nível. Meta: ~3–5 KB por .md.

---

Você vai transformar um guia de build de D&D 5e (regras 2014) numa **ficha mecânica compacta com progressão**.
Não copie texto do guia: escreva só números e escolhas, em frases curtas, em português.

Regras:
1. Níveis-alvo: **3, 5, 7, 9, 11** (e 13 se o guia cobrir). Se o guia não diz algo para um nível, siga a progressão
   recomendada dele; se ainda faltar, escolha o óbvio e marque com (suposto).
2. Atributos pelo método do guia (point buy 27 se não disser). ASIs/feats na ordem que o guia recomenda.
3. Itens: **nenhum item mágico**, salvo se o guia depender de um (marque). Sem homebrew.
4. Multiclasse: siga a ordem de níveis do guia; diga a distribuição em cada nível-alvo.
5. Números já calculados: bônus de ataque, dano por acerto (com atributo, Dueling, Fúria, Hex…), CD, CA, PV médios
   (média de dado por nível + Con), saves. Truques com a escala do nível.
6. Orçamento: dia de 4 lutas (não prioritária, prioritária, descanso curto, não prioritária, prioritária). Se o guia
   fala de como gastar recursos, resuma; senão, deixe "plano: auto".
7. Seja curto. Tabelas só onde indicado. Nada de explicação de regra.

MODELO (preencha; apague o que não se aplica):

---
id: [slug curto, ex.: rpgbot-devotion-paladin]
nome: [Nome da build (RPGBot)]
fonte: [rpgbot | d4 | treant] · [URL do guia]
classe: [Classe (Subclasse) ou distribuição de multiclasse]
plano: [auto | guia]
---

## Ideia
[até 300 caracteres: papel na party, o que ela faz de melhor, o que o guia diz que é o ponto forte]

## Base (nível 3)
- Raça: [nome; traços de combate]
- Atributos: For X | Des X | Con X | Int X | Sab X | Car X
- PV X | CA X ([como]) | Prof +2 | Deslocamento X
- Saves: For +X | Des +X | Con +X | Int +X | Sab +X | Car +X  (vantagens/resistências: …)
- Recursos: [espaços 1º X…; outros: nome qtd/curto|longo]
- Ataques: [nome: +acerto, dano, quantos por round, crítico em, vantagem habitual (fração dos rounds), GWM/SS?]
- Dano extra: [1×/turno: …; por recurso: …; com save: magia/truque, CD, save, dano, metade?]
- Controle: [efeito, recurso, CD/save, alvos, concentração] ou –
- Área: [efeito, recurso, CD/save, dano, forma] ou –
- Suporte/cura: [efeito, recurso, quem recebe, o que dá] ou –
- Defesas ativas/reações: [Shield, Uncanny Dodge, Absorb Elements… com usos] ou –
- Posição: [linha de frente | segunda linha | atirador | conjurador]

## Mudanças por nível (só o que muda; cumulativo)
| Nível | Classes | Ganha | PV | CA | Ataque/dano | Recursos | Novas opções de combate |
|---|---|---|---|---|---|---|---|
| 5 | [ex.: Paladin 5] | [Extra Attack; 2º círculo] | [X] | [X] | [2× +7, 2d6+4] | [1º 4, 2º 2] | [ex.: Misty Step, Find Steed] |
| 7 | … | … | … | … | … | … | … |
| 9 | … | … | … | … | … | … | … |
| 11 | … | … | … | … | … | … | … |
- Saves que mudam: [nível: novos valores] ou –

## Linhas-opção (hipóteses de luta)
Uma linha por jeito de lutar (vale para todos os níveis em que existe). Diga o que gasta **por luta**.
- [id curto, ex.: sem-recurso]: [o que faz round a round] · gasta: nada
- [ex.: smite-prioritaria]: [R1 Bless; smites nos acertos] · gasta: 1º 1 + smites 2×2º · a partir do nível 5
- [ex.: controle]: [Hold Person no R1, depois ataques] · gasta: 2º 1

## Plano do dia (só se o guia orienta; senão "auto")
- [nível ou faixa]: NP1 [linha] · P1 [linha] · SR · NP2 [linha] · P2 [linha]

## O que o guia destaca / avisa
- [3–5 bullets curtos: forças, fraquezas, armadilhas, picos de poder por nível]
