import json, math
OUT='/home/claude/dh-metricas/progressoes/'
SL={1:{"1":2},2:{"1":3},3:{"1":4,"2":2},4:{"1":4,"2":3},5:{"1":4,"2":3,"3":2},6:{"1":4,"2":3,"3":3},7:{"1":4,"2":3,"3":3,"4":1},
    8:{"1":4,"2":3,"3":3,"4":2},9:{"1":4,"2":3,"3":3,"4":3,"5":1},10:{"1":4,"2":3,"3":3,"4":3,"5":2},11:{"1":4,"2":3,"3":3,"4":3,"5":2,"6":1}}
def prof(L): return 2+(L-1)//4
def espacos(cl, wl, mage_armor=True):
    e=dict(SL[cl]); r=math.ceil(wl/2)
    while r>0:                      # Arcane Recovery: maior espaço possível (até 5º), o resto em espaços menores
        s=min(r,5); e[str(s)]=e.get(str(s),0)+1; r-=s
    if mage_armor: e["1"]-=1
    return e
def k(L): return 1+(L>=5)+(L>=11)
# truques
def fire_bolt(L,atk,n): return {"ataques":[{"n":n,"bonus":atk,"dano":f"{k(L)}d10","nota":"Fire Bolt"}]}
def ray_frost(L,atk,n): return {"ataques":[{"n":n,"bonus":atk,"dano":f"{k(L)}d8","nota":"Ray of Frost"}]}
def toll(L,cd,n,meio=False,extra=0): return {"com_save":[{"n":n,"cd":cd,"save":"Sab","dano":f"{k(L)}d12"+(f"+{extra}" if extra else ""),"meio":meio,"nota":"Toll the Dead (alvo ferido)"}]}
def sliver(L,cd,n): return {"com_save":[{"n":n,"cd":cd,"save":"Int","dano":f"{k(L)}d6","nota":"Mind Sliver"}]}
def acid(L,cd,n): return {"com_save":[{"n":n,"cd":cd,"save":"Des","dano":f"{k(L)}d6","nota":"Acid Splash"}]}
def xbow(L,b,dex,n): return {"ataques":[{"n":n,"bonus":b,"dano":f"1d8+{dex}","nota":"besta leve"}]}
def merge(*ds):
    o={}
    for d in ds:
        for kk,v in d.items(): o.setdefault(kk,[]).extend(v) if isinstance(v,list) else o.__setitem__(kk,v)
    return o
# invocações (Tasha): stat block pelo nível do espaço
def summon(tipo,lv,atk):
    if tipo=='fey': ca,pv,d=12+lv,30+10*(lv-3),f"1d6+{3+lv}"
    if tipo=='undead': ca,pv,d=11+lv,20+10*(lv-3),f"2d4+{3+lv}"
    if tipo=='shadowspawn': ca,pv,d=11+lv,35+15*(lv-3),f"1d12+{3+lv}"
    if tipo=='aberration': ca,pv,d=11+lv,40+10*(lv-4),f"1d8+{3+lv}"
    return {"nome":f"Summon {tipo.title()} ({lv}º)","quantidade":1,"pv":pv,"ca":ca,"ataque":{"n":lv//2,"bonus":atk,"dano":d}}
AT=lambda front=False,papel='conjurador': {"papel":papel,"front":front,"acc_m":[0.8,0.9,1.0],"conc":True,"soft":0.15,"dpr":"auto"}
SH={"reacoes":[{"tipo":"shield","usos_luta":1}]}
RE=[{"uso":"Shield","fracao":0.5,"eixos":["defesa"]}]
def area_sp(nome,alvos,dano,cd,slot,save=None,sel=False):
    u={"alvos":alvos,"dano":dano,"cd":cd,"slot":slot}
    if sel: u["seletiva"]=True
    return {"nome":nome,"usos":[u]}
def U(nome,magia,cd,slot,alvos=None,area=False):
    """opção de controle: área da biblioteca ou alvo único (1 lançamento)."""
    if area or alvos: f={"tipo":"area","nome":nome,"magia":magia,"cd":cd}; 
    else: f={"tipo":"alvo_unico","nome":nome,"cd":cd,"slots":[slot],"magias":[magia],"modo":"melhor"}
    if alvos: f["alvos"]=alvos
    return dict(f=f,slot=slot)
def controle_fonte(ops):
    if len(ops)==1: return ops[0]['f']
    return {"tipo":"melhor_de","nome":"Magia de controle (a melhor da lista)","opcoes":[o['f'] for o in ops]}
def fatia(L, cl, wl, mods, profs, ca, pv, cant, ctrl=(), barato=None, areas=(), inv=None, extra=(), shield=True, mage_armor=True, ctl_extra=(), papel='conjurador', front=False, ff=0):
    p=prof(L); sv={kk:mods[kk]+(p if kk in profs else 0) for kk in mods}
    corpo=dict(ca=ca,pv=pv,saves=dict(sv=sv,conjurador=True))
    esp=espacos(cl,wl,mage_armor)
    linhas=[]
    def ln(id_,dn,**kw):
        l={"id":id_,"dano":dn}; l.update(kw); linhas.append(l)
    base_ctl={"atencao":AT(front,papel),"fontes":[{"tipo":"ameaca","nome":"Corpo (ameaça)"}]+list(ctl_extra)}
    ln("principal",cant(1.0),controle=base_ctl,defesa={},saves={},area=[],invocacoes=[])
    def gasto(*sl,meio=None):
        g={}
        for s in sl: g[str(s)]=g.get(str(s),0)+1
        if meio: g[str(meio)]=g.get(str(meio),0)+0.5
        if shield: g["1"]=g.get("1",0)+1
        return {"espacos":g}
    dfs=dict(defesa=SH,reacao=RE) if shield else dict(defesa={},reacao=[])
    def FF(fo): return dict(fo, forcar_falha=ff) if ff else fo
    if ctrl:
        top=max(o['slot'] for o in ctrl)
        ln("controle",cant(0.75),controle={"atencao":AT(front,papel),"fontes":[FF(controle_fonte(list(ctrl)))]+list(ctl_extra)},gasta=gasto(top),area=[],invocacoes=[],**dfs)
        if barato:
            ln("controle-barato",cant(0.75),controle={"atencao":AT(front,papel),"fontes":[FF(barato['f'])]+list(ctl_extra)},gasta=gasto(barato['slot']),area=[],invocacoes=[],**dfs)
    if areas:
        a=list(areas)
        ln("area",cant(0.75),controle=base_ctl,area=a,gasta=gasto(*[u['slot'] for x in a for u in x['usos']]),invocacoes=[],**dfs)
        if ctrl:
            ln("combo",cant(0.5),controle={"atencao":AT(front,papel),"fontes":[FF(controle_fonte(list(ctrl)))]+list(ctl_extra)},area=a,
               gasta=gasto(top,*[u['slot'] for x in a for u in x['usos']]),invocacoes=[],**dfs)
    if inv:
        ln("invocacao",cant(0.75),controle=base_ctl,invocacoes=[inv['i']],gasta=gasto(meio=inv['slot']),area=[],**dfs)
    for x in extra: linhas.append(x)
    for l in linhas:
        if l['id']!='principal': l.setdefault('herda','principal')
    return dict(corpo=corpo,recursos={"espacos":esp},linhas=linhas)
def hpcalc(dados,con,extra=0):
    t=0
    for i,d in enumerate(dados): t+= (d if i==0 else d//2+1)+con
    return t+extra
FONTE=lambda slug: {"tipo":"rpgbot","url":f"https://rpgbot.net/dnd5/characters/classes/wizard/subclasses/{slug}/","nota":"Build exemplo do guia de subclasse (2014). Passada 1 cega: só mecânica; premissas congeladas."}
def escrever(id_,slug,nome,build,desc,fatias):
    b=fatias[3]; base=dict(build=build,corpo=b['corpo'],recursos=b['recursos'],linhas=b['linhas'],planos={"padrao":"auto","combate_unico":"auto"},descricao=desc)
    base['linhas'][0]['principal']=True; base['linhas'][0]['custo']='gratuita'; base['linhas'][0]['hipotese']='só truques (anel interno)'
    for l in base['linhas'][1:]: l.setdefault('hipotese',l['id'])
    niv={}
    for L in (5,7,9,11):
        f=fatias[L]
        for l in f['linhas']:
            if l['id']=='principal': l.pop('herda',None)
            else: l.setdefault('hipotese',l['id'])
        niv[str(L)]=dict(_texto=f.get('_texto',''),corpo=f['corpo'],recursos=f['recursos'],linhas=f['linhas'])
    niv={'3':{"_texto":fatias[3].get('_texto','')},**niv}
    P=dict(id=id_,nome=nome,grupo="RPGBot",fonte=FONTE(slug),base=base,niveis=niv)
    json.dump(P,open(OUT+id_+'.json','w'),ensure_ascii=False,indent=1); print('ok',id_)
def M(f,d,c,i,w,ch): return {"for":f,"des":d,"con":c,"int":i,"sab":w,"car":ch}
HYP=lambda cd: U("Hypnotic Pattern","hypnotic_pattern",cd,3,area=True)
WEB=lambda cd: U("Web","web",cd,2,area=True)
EBT=lambda cd: U("Evard's Black Tentacles","evards_black_tentacles",cd,4,area=True)
HM=lambda cd,s=5: U("Hold Monster","hold_monster",cd,s)
HP_=lambda cd: U("Hold Person","hold_person",cd,2)
BAN=lambda cd: U("Banishment","banishment",cd,4)
WOF=lambda cd: U("Wall of Force","wall_of_force",cd,5)
SYN=lambda cd: U("Synaptic Static","synaptic_static",cd,5,area=True)
PF=lambda cd: U("Phantasmal Force","phantasmal_force",cd,2)
EG=lambda cd: U("Earthen Grasp","earthen_grasp",cd,2)
FB=lambda cd,extra=0,sel=False: area_sp("Fireball",4,"8d6"+(f"+{extra}" if extra else ""),cd,3,sel=sel)
