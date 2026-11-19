import json
OUT='/home/claude/dh-metricas/progressoes/'
def prof(L): return 2+(L-1)//4
def M(f,d,c,i,w,ch): return {"for":f,"des":d,"con":c,"int":i,"sab":w,"car":ch}
def corpo(ca,pv,L,m,n,profs=('for','con')): return dict(ca=ca,pv=pv,saves=dict(sv={k:m[k]+(prof(L) if k in profs else 0) for k in m},ataques=n))
def hp(L,con): return 10+con+(L-1)*(6+con)
AS={"qtd":1,"volta":"curto"}
PURO="Extensão simples da build do RPGBot sem a multiclasse (níveis adiantados, atributos e feats remendados); a build original continua como referência."
def surge(at): return [dict(a,n=round(a['n']/4,4)) for a in at if a.get('acao',True)]
def strip(at): return [{k:v for k,v in a.items() if k!='acao'} for a in at]
FONTE=lambda slug: {"tipo":"rpgbot","url":f"https://rpgbot.net/dnd5/characters/classes/fighter/subclasses/{slug}/","nota":"Extensão simples sem multiclasse; passada 2."}
def escrever(id_,slug,nome,base,niveis):
    P=dict(id=id_,nome=nome,grupo="RPGBot",fonte=FONTE(slug),base=base,niveis={str(k):v for k,v in niveis.items()})
    json.dump(P,open(OUT+id_+'.json','w'),ensure_ascii=False,indent=1); print('ok',id_)
# ---------- Echo Knight puro ----------
def echo(L,s,ca,n,gwm=False):
    b=s+prof(L); kw={"poder":[-5,10]} if gwm else {}
    dmg=f"2d6+{s}+1.33"
    at=[dict(n=n,bonus=b,dano=dmg,**kw),dict(n=round(2/16,4),bonus=b,dano=dmg,nota="Unleash Incarnation (Con/dia ÷ 4 lutas ÷ 4 rounds)",**kw),
        dict(n=0.5,bonus=b,dano=dmg,acao=False,nota="ataque de oportunidade (Sentinel, também pelo eco), reação em 50% dos rounds")]
    ctl={"atencao":{"papel":"tank","soft":0.15,"dpr":"auto","hard":{"sentinela":b}},"fontes":[{"tipo":"sentinela","nome":"Corpo (Sentinel pelo eco)","bonus":b},{"tipo":"ameaca","nome":"Corpo (ameaça)"}]}
    return dict(corpo=corpo(ca,hp(L,2),L,M(s,1,2,-1,1,-1),n),linhas=[{"id":"principal","dano":{"ataques":strip(at)},"controle":ctl},{"id":"surge","dano":{"ataques":strip(at+surge(at))},"controle":ctl}])
REAC=[{"uso":"ataque de oportunidade (Sentinel)","fracao":0.5,"eixos":["dano","controle"]}]
e3=echo(3,3,16,1)
escrever('rpgbot-fighter-echo-knight-puro','echo-knight','Echo Knight Fighter puro (extensão da build do RPGBot)',
 dict(build="Fighter (Echo Knight) sem multiclasse, Custom Lineage, malho + GWF; Sentinel 1, Crusher 4, For 20 6, GWM 8; placas no 7",
  corpo=e3['corpo'],recursos={"espacos":{},"outros":{"action_surge":AS}},
  linhas=[dict(e3['linhas'][0],principal=True,hipotese="ataca pelo eco; Sentinel pune quem sai de perto do eco",custo="gratuita",reacao=REAC,saves={},defesa={}),
          dict(e3['linhas'][1],herda="principal",plano="prioritaria",hipotese="Action Surge num round",gasta={"action_surge":1})],
  planos={"padrao":"auto","combate_unico":"auto"},
  descricao={"resumo":"A build Dioscuri sem o dip de Barbarian: Fighter puro com Sentinel pelo eco, GWM no 8 e terceiro ataque no 11.","estrategia":PURO,
   "nao_modelado":"Crusher; o eco como alvo extra e teleporte; Indomitable; Second Wind; Shadow Martyr."}),
 {3:{"_texto":"Manifest Echo; Unleash Incarnation."},5:dict(_texto="Crusher (For 18); Extra Attack.",**echo(5,4,16,2)),
  7:dict(_texto="For 20 (6); placas.",**echo(7,5,18,2)),9:dict(_texto="GWM (8); Indomitable.",**echo(9,5,18,2,True)),
  11:dict(_texto="Terceiro ataque.",**echo(11,5,18,3,True))})
# ---------- Purple Dragon Knight puro ----------
def pdk(L,ca,dx,ch,n,ss=False,surge_ins=False):
    p=prof(L); b=dx+p+2; kw={"poder":[-5,10]} if ss else {}
    at=[dict(n=n,bonus=b,dano=f"1d8+{dx}",**kw)]
    cd=8+3+p; sop="1d10" if L<5 else "2d10" if L<11 else "3d10"
    area=[{"nome":"Breath Weapon (cone 15 pés)","usos":[{"alvos":2,"dano":sop,"cd":cd}]}]
    sup={"fontes":[{"nome":"Rallying Cry (Second Wind)","lado":"def","modelo":"cura","usos_descanso_curto":1,"pv":3*L}]}
    if surge_ins: sup["fontes"].append({"nome":"Inspiring Surge (aliado ataca no Action Surge)","lado":"of","modelo":"ataque_extra","alvos":0.125,"nota":"0,5 Action Surge por luta ÷ 4 rounds"})
    ctl={"atencao":{"papel":"atirador","soft":0.15,"dpr":"auto","front":False},"fontes":[{"tipo":"ameaca","nome":"Corpo (ameaça)"}]}
    ls=[{"id":"principal","dano":{"ataques":at},"suporte":sup,"controle":ctl},{"id":"sopro","dano":{"ataques":at},"area":area,"suporte":sup},
        {"id":"surge","dano":{"ataques":at+surge(at)},"area":area,"suporte":sup}]
    if L>=5:
        ls.append({"id":"medo","dano":{"ataques":at},"suporte":sup,"controle":dict(ctl,fontes=[{"tipo":"area","nome":"Dragon Fear (cone 30 pés)","magia":"cond_amedrontado","alvos":3,"cd":8+p+ch}]+ctl['fontes'])})
    return dict(corpo=corpo(ca,hp(L,3),L,M(-1,dx,3,-1,0,ch),n),linhas=ls)
d3=pdk(3,16,3,2,1)
escrever('rpgbot-fighter-purple-dragon-knight-puro','purple-dragon-knight','Purple Dragon Knight puro (extensão da build do RPGBot)',
 dict(build="Fighter (Purple Dragon Knight) sem multiclasse, Dragonborn de Gema, arco longo + Archery; Dragon Fear 4, Sharpshooter 6, Des 18 (8)",
  corpo=d3['corpo'],recursos={"espacos":{},"outros":{"action_surge":AS,"sopro":{"qtd":2,"volta":"longo"}}},
  linhas=[dict(d3['linhas'][0],principal=True,hipotese="arco longo todo round; Rallying Cry no Second Wind",custo="gratuita",defesa={},saves={}),
          dict(d3['linhas'][1],herda="principal",hipotese="Breath Weapon num round",gasta={"sopro":1}),
          dict(d3['linhas'][2],herda="principal",plano="prioritaria",hipotese="Breath Weapon + Action Surge",gasta={"sopro":1,"action_surge":1})],
  planos={"padrao":"auto","combate_unico":"auto"},
  descricao={"resumo":"A build Traitor to the Crown sem o dip de Warlock: arqueiro com Sharpshooter, sopro de dragão, Dragon Fear e Inspiring Surge no 10.","estrategia":PURO,
   "nao_modelado":"Royal Envoy; Bulwark; Indomitable; Second Wind próprio."}),
 {3:{"_texto":"Rallying Cry."},
  5:dict(_texto="Dragon Fear (Car 16); Extra Attack; meia-armadura.",recursos={"outros":{"sopro":{"qtd":3,"volta":"longo"}}},**pdk(5,17,3,3,2)),
  7:dict(_texto="Sharpshooter (6).",**pdk(7,17,3,3,2,True)),
  9:dict(_texto="Des 18 (8); Indomitable.",recursos={"outros":{"sopro":{"qtd":4,"volta":"longo"}}},**pdk(9,17,4,3,2,True)),
  11:dict(_texto="Inspiring Surge (10); terceiro ataque; sopro 3d10.",**pdk(11,17,4,3,3,True,True))})
p=json.load(open(OUT+'rpgbot-fighter-purple-dragon-knight-puro.json'))
for l in p['niveis']['5']['linhas']:
    if l['id']=='medo': l.update(herda="principal",hipotese="Dragon Fear no lugar do sopro de dano",gasta={"sopro":1})
json.dump(p,open(OUT+'rpgbot-fighter-purple-dragon-knight-puro.json','w'),ensure_ascii=False,indent=1)
