import json
OUT='/home/claude/dh-metricas/progressoes/'
def FONTE(slug): return {"tipo":"rpgbot","url":f"https://rpgbot.net/dnd5/characters/classes/fighter/subclasses/{slug}/","nota":"Build exemplo do guia de subclasse (2014). Passada 1 cega: só mecânica; premissas congeladas."}
def prof(L): return 2+(L-1)//4
def mods(f,d,c,i,w,ch): return {"for":f,"des":d,"con":c,"int":i,"sab":w,"car":ch}
def sv(L,m,profs): return {k:m[k]+(prof(L) if k in profs else 0) for k in m}
def corpo(ca,pv,L,m,ataques,profs=('for','con'),**k): return dict(ca=ca,pv=pv,saves=dict(sv=sv(L,m,profs),ataques=ataques),**k)
def atk(n,b,d,**k): return dict(n=n,bonus=b,dano=d,**k)
def surge(at): return [dict(a,n=round(a['n']/4,4)) for a in at if a.get('acao',True)]
PLANOS={"padrao":"auto","combate_unico":"auto"}
AS={"qtd":1,"volta":"curto"}
CTRL=lambda papel,**k: {"atencao":dict(papel=papel,soft=0.15,dpr="auto",**k),"fontes":[{"tipo":"ameaca","nome":"Corpo (ameaça)"}]}
def escrever(slug,nome,base,niveis):
    id_='rpgbot-fighter-'+slug
    p=dict(id=id_,nome=nome,grupo="RPGBot",fonte=FONTE(slug),base=base,niveis={str(k):v for k,v in niveis.items()})
    json.dump(p,open(OUT+id_+'.json','w'),ensure_ascii=False,indent=1); print('ok',id_)
def strip(at): return [{k:v for k,v in a.items() if k!='acao'} for a in at]

# ================= Samurai (A Fistful of Advantage) =================
sm=lambda d: mods(-1,d,3,0,2,-1)
PIER12=[{"dano":"1.5","nota":"Piercer: rerrolar d12"},{"dano":"1d12","gatilho":"critico"}]
def sam(L,ca,dex,n,dado,profs,v0=0.0,pier=False):
    b=dex+prof(L)+2; at=[atk(n,b,f"{dado}+{dex}",vantagem=v0)]
    at1=[atk(n,b,f"{dado}+{dex}",vantagem=min(1.0,v0+0.25))]
    def d(a,extra=()):
        x={"ataques":a+list(extra)}
        if pier: x["por_turno"]=PIER12
        return x
    return dict(corpo=corpo(ca,hp(L,3),L,sm(dex),n,profs),
        linhas=[{"id":"principal","dano":d(at)},{"id":"espirito","dano":d(at1)},{"id":"surge","dano":d(at1,surge(at1))}])
def hp(L,con): return 10+con+(L-1)*(6+con)
s3=sam(3,16,3,1,"1d8",('for','con'))
escrever('samurai','Samurai Fighter (RPGBot: A Fistful of Advantage)',
 dict(build="Fighter (Samurai), Kobold (MMoM), besta leve → mosquete (Gunner 4), Archery; Resilient Des 6, Piercer 8",
  corpo=s3['corpo'],recursos={"espacos":{},"outros":{"action_surge":AS,"fighting_spirit":{"qtd":3,"volta":"longo"}}},
  linhas=[dict(s3['linhas'][0],principal=True,hipotese="atira todo round, sem vantagem",custo="gratuita",defesa={},controle=CTRL("atirador",front=False),saves={}),
          dict(s3['linhas'][1],herda="principal",hipotese="Fighting Spirit num round (vantagem em todos os ataques do turno)",gasta={"fighting_spirit":1}),
          dict(s3['linhas'][2],herda="principal",plano="prioritaria",hipotese="Fighting Spirit + Action Surge no mesmo round",gasta={"fighting_spirit":1,"action_surge":1})],
  planos=PLANOS,
  descricao={"resumo":"Samurai pistoleiro (Kobold) que liga vantagem quando precisa; mosquete com Gunner, proficiente em Des, Con e Sab.",
   "estrategia":"Atira de perto ou de longe; Fighting Spirit no round de maior impacto, junto com o Action Surge nas lutas importantes.",
   "nao_modelado":"Draconic Cry (vantagem para a party contra inimigos a 10 pés: depende de posição); PV temporários do Fighting Spirit; Blade Ward; Indomitable; Second Wind; Elegant Courtier fora dos saves."}),
 {3:{"_texto":"Fighting Spirit 3/dia; besta leve 1d8."},
  5:dict(_texto="Gunner (Des 18): mosquete 1d12; Extra Attack; meia-armadura (CA 17).",**sam(5,17,4,2,"1d12",('for','con'))),
  7:dict(_texto="Resilient Des (19); Elegant Courtier: proficiência em Sab.",**sam(7,17,4,2,"1d12",('for','con','des','sab'))),
  9:dict(_texto="Piercer (Des 20); Indomitable.",**sam(9,17,5,2,"1d12",('for','con','des','sab'),pier=True)),
  11:dict(_texto="Tireless Spirit (10): 1 Fighting Spirit garantido por luta; terceiro ataque.",**sam(11,17,5,3,"1d12",('for','con','des','sab'),v0=0.25,pier=True))})

# ================= Echo Knight (Dioscuri) =================
ekm=lambda s: mods(s,1,2,-1,1,-1)
GW=lambda s,extra=0: f"2d6+{s+extra}+1.33"
def echo(L,s,n,pv,unleash=2,rage=None,reck=False,gwm=False,anc=False):
    b=s+prof(L); kw={}
    if reck: kw['vantagem']=1.0
    if gwm: kw['poder']=[-5,10]
    def at(r): 
        dmg=GW(s,2 if r else 0)
        return [atk(n,b,dmg,**kw),atk(round(unleash/4/4,4),b,dmg,**kw,nota="Unleash Incarnation (Con/dia ÷ 4 lutas ÷ 4 rounds)"),
                dict(atk(0.5,b,dmg,**{k:v for k,v in kw.items() if k!='vantagem'}),acao=False,nota="ataque de oportunidade (Sentinel, também pelo eco), reação em 50% dos rounds")]
    ctl={"atencao":{"papel":"tank","soft":0.15,"dpr":"auto","hard":{"sentinela":b}},"fontes":[{"tipo":"sentinela","nome":"Corpo (Sentinel pelo eco)","bonus":b},{"tipo":"ameaca","nome":"Corpo (ameaça)"}]}
    ctl_r=json.loads(json.dumps(ctl))
    if anc: ctl_r["fontes"].insert(0,{"tipo":"ancestral_protectors","nome":"Ancestral Protectors (pelo eco)","bonus":b})
    adv=1 if reck else 0
    c=corpo(16,pv,L,ekm(s),n,adv=adv) if adv else corpo(16,pv,L,ekm(s),n)
    a0=at(False); L0=[{"id":"principal","dano":{"ataques":strip(a0)},"controle":ctl,"defesa":({"adv":1} if reck else {})},
        {"id":"surge","dano":{"ataques":strip(a0+surge(a0))},"controle":ctl,"defesa":({"adv":1} if reck else {})}]
    if rage:
        a1=at(True); dr={"resist":True}; 
        if reck: dr["adv"]=1
        L0+=[{"id":"furia","dano":{"ataques":strip(a1)},"controle":ctl_r,"defesa":dr},
             {"id":"furia-surge","dano":{"ataques":strip(a1+surge(a1))},"controle":ctl_r,"defesa":dr}]
    out=dict(corpo=c,linhas=L0)
    return out
REAC=[{"uso":"ataque de oportunidade (Sentinel)","fracao":0.5,"eixos":["dano","controle"]}]
e3=echo(3,3,1,28)
rage_lines=lambda: [{"id":"furia","herda":"principal","hipotese":"luta inteira em fúria (+2 de dano, resistência a dano físico)","gasta":{"furia":1}},
                    {"id":"furia-surge","herda":"principal","plano":"prioritaria","hipotese":"fúria + Action Surge","gasta":{"furia":1,"action_surge":1}}]
escrever('echo-knight','Echo Knight Fighter (RPGBot: Dioscuri)',
 dict(build="Fighter 8 / Barbarian 3 (Echo Knight, Ancestral Guardian), Custom Lineage, malho + GWF; Sentinel 1, Crusher 4, For 20 6, GWM 11 (nível de personagem)",
  corpo=e3['corpo'],recursos={"espacos":{},"outros":{"action_surge":AS}},
  linhas=[dict(e3['linhas'][0],principal=True,hipotese="ataca pelo eco; Sentinel pune quem tenta sair de perto do eco",custo="gratuita",reacao=REAC,saves={}),
          dict(e3['linhas'][1],herda="principal",plano="prioritaria",hipotese="Action Surge num round",gasta={"action_surge":1})],
  planos=PLANOS,
  descricao={"resumo":"Echo Knight defensor com Sentinel: ataca pelo eco e prende os inimigos longe da party; a partir do 7 mergulha em Barbarian (Ancestral Guardian).",
   "estrategia":"Põe o eco ao lado da maior ameaça, bate pelo eco e segura o alvo com Sentinel; com fúria, Ancestral Protectors faz o alvo errar quem não é ele.",
   "nao_modelado":"Crusher (empurrão); o eco como alvo extra e teleporte; Danger Sense; Indomitable; Second Wind; Shadow Martyr; os outros alvos que o eco ameaça além do principal."}),
 {3:{"_texto":"Manifest Echo; Unleash Incarnation (Con/dia)."},
  5:dict(_texto="Crusher (For 18); Extra Attack.",**echo(5,4,2,44)),
  7:dict(_texto="For 20 (F6); Barbarian 1: fúria 2/dia.",recursos={"outros":{"furia":{"qtd":2,"volta":"longo"}}},**{**echo(7,5,2,61,rage=True),"linhas":echo(7,5,2,61,rage=True)['linhas']}),
  9:dict(_texto="Barbarian 3: Reckless Attack, Ancestral Protectors; fúria 3/dia.",recursos={"outros":{"furia":{"qtd":3,"volta":"longo"}}},**echo(9,5,2,79,rage=True,reck=True,anc=True)),
  11:dict(_texto="F8: Great Weapon Master (personagem 11); ainda 2 ataques.",**echo(11,5,2,95,rage=True,reck=True,anc=True,gwm=True))})
# as linhas de fúria só existem do 7 em diante: adiciona a definição base no patch do 7
p=json.load(open(OUT+'rpgbot-fighter-echo-knight.json'))
for l in p['niveis']['7']['linhas']:
    if l['id']=='furia': l.update({"herda":"principal","hipotese":"luta inteira em fúria (+2 de dano, resistência a dano físico)","gasta":{"furia":1}})
    if l['id']=='furia-surge': l.update({"herda":"principal","plano":"prioritaria","hipotese":"fúria + Action Surge","gasta":{"furia":1,"action_surge":1}})
json.dump(p,open(OUT+'rpgbot-fighter-echo-knight.json','w'),ensure_ascii=False,indent=1)

# ================= Psi Warrior (Giff Yankee) =================
pw=lambda d,i: mods(0,d,2,i,-1,-1)
def psi(L,ca,dex,n,dado,dpsi,dados_dia,i=3,ss=False,pier=False):
    b=dex+prof(L)+2; kw={"poder":[-5,10]} if ss else {}
    at=[atk(n,b,f"{dado}+{dex}",**kw)]
    pl=[{"usos_dia":dados_dia,"dano":f"{dpsi}+{i}","nota":"Psionic Strike: dados por dia (2×PB + 1 por descanso curto) ÷ 4 lutas"},
        {"usos_dia":prof(L),"dano":str(prof(L)),"nota":"Astral Spark (Giff): PB/dia, +PB de força num acerto"}]
    d=lambda a: dict(ataques=a,por_luta=pl,**({"por_turno":PIER12} if pier else {}))
    return dict(corpo=corpo(ca,hp(L,2),L,pw(dex,i),n),linhas=[{"id":"principal","dano":d(at)},{"id":"surge","dano":d(at+surge(at))}])
p3=psi(3,15,3,1,"1d10","1d6",6)
escrever('psi-warrior','Psi Warrior Fighter (RPGBot: Giff Yankee)',
 dict(build="Fighter (Psi Warrior), Giff, besta pesada → mosquete, Archery; Piercer 4, Sharpshooter 6, Des 20 8",
  corpo=p3['corpo'],recursos={"espacos":{},"outros":{"action_surge":AS}},
  linhas=[dict(p3['linhas'][0],principal=True,hipotese="atira todo round; dados psiônicos no Psionic Strike, espalhados pelo dia",custo="gratuita",defesa={},controle=CTRL("atirador",front=False),saves={}),
          dict(p3['linhas'][1],herda="principal",plano="prioritaria",hipotese="Action Surge num round",gasta={"action_surge":1})],
  planos=PLANOS,
  descricao={"resumo":"Psi Warrior atirador (Giff) com mosquete; dados psiônicos para dano extra, proteção e empurrão telecinético.",
   "estrategia":"Atira de longe e gasta os dados psiônicos com parcimônia ao longo do dia, no Psionic Strike para finalizar alvos.",
   "nao_modelado":"Protective Field (todos os dados foram para o Psionic Strike); Telekinetic Thrust (derrubar/empurrar); Telekinetic Movement; Psi-Powered Leap; Guarded Mind; Indomitable; Second Wind; vantagem do Giff em testes de For."}),
 {3:{"_texto":"Psionic Power: 4 dados d6 + 1 por descanso curto."},
  5:dict(_texto="Piercer (Des 18); Extra Attack; mosquete 1d12; dados d8 (6 + 2).",**psi(5,16,4,2,"1d12","1d8",8,pier=True)),
  7:dict(_texto="Sharpshooter (6); Telekinetic Adept.",**psi(7,16,4,2,"1d12","1d8",8,ss=True,pier=True)),
  9:dict(_texto="Des 20 (8); 8 dados + 2; Indomitable.",**psi(9,17,5,2,"1d12","1d8",10,ss=True,pier=True)),
  11:dict(_texto="Terceiro ataque; dados d10.",**psi(11,17,5,3,"1d12","1d10",10,ss=True,pier=True))})

# ================= Rune Knight (Attaxi of the Giant Tabaxi) =================
rk=lambda s,c: mods(s,1,c,-1,1,-1)
def rune(L,ca,s,n,gm,atl,perde=0.0,hill=False):
    b=s+prof(L); a=[atk(round(n-perde,4),b,f"1d6+{s}")]
    ctl={"atencao":{"papel":"tank","soft":0.15,"dpr":"auto","agarra":True},"fontes":[{"tipo":"agarrao","nome":"Agarrão (Atletismo)","bonus":atl},{"tipo":"ameaca","nome":"Corpo (ameaça)"}]}
    g={"por_turno":[{"dano":gm,"nota":"Giant's Might: dano extra 1×/turno"}]}
    out=[{"id":"principal","dano":{"ataques":a},"controle":ctl},
         {"id":"gigante","dano":dict(ataques=a,**g),"controle":ctl},
         {"id":"surge","dano":dict(ataques=a+surge([atk(n,b,f"1d6+{s}")]),**g),"controle":ctl}]
    if hill:
        for l in out[1:]: l["defesa"]={"resist":True}
    return dict(corpo=corpo(ca,hp(L,3),L,rk(s,3),n),linhas=out)
r3=rune(3,16,3,1,"1d6",5,perde=0.25)
escrever('rune-knight','Rune Knight Fighter (RPGBot: Attaxi of the Giant Tabaxi)',
 dict(build="Fighter (Rune Knight), Tabaxi (MMoM), garras + Unarmed Fighting, agarrador; Skill Expert (Atletismo) 4, Tavern Brawler 6, Crusher 8",
  corpo=r3['corpo'],recursos={"espacos":{},"outros":{"action_surge":AS,"giants_might":{"qtd":2,"volta":"longo"}}},
  linhas=[dict(r3['linhas'][0],principal=True,hipotese="agarra o alvo prioritário (custa ataques até o Tavern Brawler) e bate com as garras",custo="gratuita",defesa={},saves={}),
          dict(r3['linhas'][1],herda="principal",hipotese="Giant's Might na luta (Grande, vantagem em For, +dado 1×/turno)",gasta={"giants_might":1}),
          dict(r3['linhas'][2],herda="principal",plano="prioritaria",hipotese="Giant's Might + Action Surge",gasta={"giants_might":1,"action_surge":1})],
  planos=PLANOS,
  descricao={"resumo":"Rune Knight agarrador (Tabaxi): cresce com Giant's Might, agarra e derruba o alvo prioritário; runas de Fogo e Pedra para prender e encantar.",
   "estrategia":"Na frente, agarra e derruba quem ameaça a party; Giant's Might nas lutas que pedem; Hill Rune contra dano físico.",
   "nao_modelado":"Fire Rune (impedido + dano), Stone Rune (encantado/incapacitado), Storm e Cloud Rune, Runic Shield; dano do Unarmed Fighting no agarrado; derrubar (shove) e a vantagem que dá; vantagem do Giant's Might no agarrão; Indomitable; Second Wind."}),
 {3:{"_texto":"Giant's Might (PB/dia); runas de Fogo e Pedra; agarrar custa 1 ataque no 1º round."},
  5:dict(_texto="Skill Expert (For 18, expertise em Atletismo); Extra Attack.",recursos={"outros":{"giants_might":{"qtd":3,"volta":"longo"}}},**rune(5,16,4,2,"1d6",10,perde=0.25)),
  7:dict(_texto="Tavern Brawler (For 19): agarra com ação bônus; Hill Rune (resistência a dano físico 1/descanso curto); placas (CA 18).",
         recursos={"outros":{"hill_rune":{"qtd":1,"volta":"curto"}}},**rune(7,18,4,2,"1d6",10,hill=True)),
  9:dict(_texto="Crusher (For 20); Indomitable; Giant's Might 4/dia.",recursos={"outros":{"giants_might":{"qtd":4,"volta":"longo"}}},**rune(9,18,5,2,"1d6",13,hill=True)),
  11:dict(_texto="Great Stature (1d8); Storm Rune; terceiro ataque.",**rune(11,18,5,3,"1d8",13,hill=True))})
p=json.load(open(OUT+'rpgbot-fighter-rune-knight.json'))
for nv in ('7','9','11'):
    for l in p['niveis'][nv]['linhas']:
        if l['id']=='gigante': l['gasta']={"giants_might":1,"hill_rune":1}; l['hipotese']="Giant's Might + Hill Rune na luta"
        if l['id']=='surge': l['gasta']={"giants_might":1,"hill_rune":1,"action_surge":1}; l['hipotese']="Giant's Might + Hill Rune + Action Surge"
json.dump(p,open(OUT+'rpgbot-fighter-rune-knight.json','w'),ensure_ascii=False,indent=1)

# ================= Purple Dragon Knight (Traitor to the Crown) =================
pd=lambda ch: mods(-1,3,3,-1,0,ch)
def pdk(L,ca,pv,fl,ch,bow_n,eb=None,sopro_d="1d10"):
    p=prof(L); bow=atk(bow_n,3+p+2,"1d8+3" if not eb else "1d8+3+1d6")
    if eb:  # Eldritch Blast + Hex
        beams,ag=eb; at=[atk(beams,ch+p,f"1d10+1d6{'+'+str(ch) if ag else ''}",nota="Eldritch Blast + Hex")]
    else: at=[bow]
    cd=8+3+p
    area=[{"nome":"Breath Weapon (cone 15 pés)","usos":[{"alvos":2,"dano":sopro_d,"cd":cd}]}]
    cura={"fontes":[{"nome":"Rallying Cry (Second Wind)","lado":"def","modelo":"cura","usos_descanso_curto":1,"pv":3*fl,"nota":"3 aliados × nível de Fighter"}]}
    return dict(corpo=corpo(ca,pv,L,pd(ch),bow_n),linhas=[
        {"id":"principal","dano":{"ataques":at},"suporte":cura},
        {"id":"sopro","dano":{"ataques":at},"area":area,"suporte":cura},
        {"id":"surge","dano":{"ataques":at+surge(at)},"area":area,"suporte":cura}])
d3=pdk(3,16,31,3,2,1)
escrever('purple-dragon-knight','Purple Dragon Knight Fighter (RPGBot: Traitor to the Crown)',
 dict(build="Fighter 9 / Warlock 2 (Purple Dragon Knight, Undead), Dragonborn de Gema (Fizban), arco longo + Archery, Eldritch Blast; Dragon Fear 4, Car 20 (nível de personagem 10)",
  corpo=d3['corpo'],recursos={"espacos":{},"outros":{"action_surge":AS,"sopro":{"qtd":2,"volta":"longo"}}},
  linhas=[dict(d3['linhas'][0],principal=True,hipotese="atira com o arco (depois Eldritch Blast + Hex); Rallying Cry junto do Second Wind",custo="gratuita",defesa={},controle=CTRL("atirador",front=False),saves={}),
          dict(d3['linhas'][1],herda="principal",hipotese="Breath Weapon num round (substitui um ataque)",gasta={"sopro":1}),
          dict(d3['linhas'][2],herda="principal",plano="prioritaria",hipotese="Breath Weapon + Action Surge",gasta={"sopro":1,"action_surge":1})],
  planos=PLANOS,
  descricao={"resumo":"Purple Dragon Knight atirador com dip de Warlock (Undead): Eldritch Blast + Hex, sopro de dragão e cura em grupo pelo Second Wind.",
   "estrategia":"Fica atrás disparando Eldritch Blast; Breath Weapon ou Dragon Fear quando os inimigos se juntam; Action Surge com Eldritch Blast nas lutas importantes.",
   "nao_modelado":"Dragon Fear e Form of Dread (amedrontado), Repelling Blast; PV temporários do Form of Dread; Second Wind próprio; Indomitable; Royal Envoy; o gasto de ação bônus do Hex no 1º round."}),
 {3:{"_texto":"Rallying Cry; sopro 1d10, PB/dia."},
  5:dict(_texto="F4 Dragon Fear (Car 16); Warlock 1: Eldritch Blast (2 raios) + Hex; sopro 2d10; meia-armadura (CA 17).",recursos={"outros":{"sopro":{"qtd":3,"volta":"longo"}},"espacos":{"1":1},"espacos_volta":"curto"},
         **pdk(5,17,48,4,3,1,eb=(2,False),sopro_d="2d10")),
  7:dict(_texto="Warlock 2: Agonizing Blast; F5 Extra Attack.",recursos={"espacos":{"1":2}},**pdk(7,17,65,5,3,2,eb=(2,True),sopro_d="2d10")),
  9:dict(_texto="Car 18 (personagem 8); F7 Royal Envoy; sopro 4/dia.",recursos={"outros":{"sopro":{"qtd":4,"volta":"longo"}}},**pdk(9,17,83,7,4,2,eb=(2,True),sopro_d="2d10")),
  11:dict(_texto="Car 20 (personagem 10); F9 Indomitable; Eldritch Blast 3 raios; sopro 3d10.",**pdk(11,17,101,9,5,2,eb=(3,True),sopro_d="3d10"))})
