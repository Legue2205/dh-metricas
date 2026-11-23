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
def _conc_nome(nome):
    """M5b (23/11): magia de concentração RAW pelo nome (lista _concentracao_nomes do magias.json) → token ou None."""
    import re as _re
    from pathlib import Path as _P
    lst=json.loads((_P(__file__).resolve().parents[2]/'dh'/'controle'/'magias.json').read_text(encoding='utf-8'))['_concentracao_nomes']['nomes']
    n=_re.sub(r'\s*\(.*','',nome).strip()
    return _re.sub(r'[^a-z]+','_',n.lower()).strip('_') if n.lower().startswith(tuple(x.lower() for x in lst)) else None
def area_sp(nome,alvos,dano,cd,slot,save=None,sel=False):
    u={"alvos":alvos,"dano":dano,"cd":cd,"slot":slot}
    if sel: u["seletiva"]=True
    e={"nome":nome,"usos":[u]}
    c=_conc_nome(nome)
    if c: e["concentracao"]=c          # M5b: declarada (o validador passa a ver duas concentrações na mesma linha)
    return e
def U(nome,magia,cd,slot,alvos=None,area=False):
    """opção de controle: área da biblioteca ou alvo único (1 lançamento)."""
    if area or alvos: f={"tipo":"area","nome":nome,"magia":magia,"cd":cd}; 
    else: f={"tipo":"alvo_unico","nome":nome,"cd":cd,"slots":[slot],"magias":[magia],"modo":"melhor"}
    if alvos: f["alvos"]=alvos
    return dict(f=f,slot=slot)
def controle_fonte(ops):
    if len(ops)==1: return ops[0]['f']
    return {"tipo":"melhor_de","nome":"Magia de controle (a melhor da lista)","opcoes":[o['f'] for o in ops]}

# Área com upcast (passada 3, 19/11): a linha "area" (luta de pico) usa as DUAS maiores magias de área da build, cada uma
# num dos dois maiores espaços do dia (o maior e o segundo maior, unidades distintas), escalada pela regra da magia.
# Com uma magia só, ela é lançada duas vezes. Magias sem regra de escala (Breath Weapon, raças) não escalam.
ESCALA={"Fireball":("dado",1),"Shatter":("dado",1),"Cone of Cold":("dado",1),"Pulse Wave":("dado",1),
        "Gravity Fissure":("dado",1),"Chain Lightning":("alvo",1)}
def _dados(d):
    import re
    m=re.fullmatch(r"(\d+)d(\d+)(.*)",d); return int(m.group(1)),int(m.group(2)),m.group(3)
def _media(d):
    n,x,r=_dados(d); return n*(x+1)/2+sum(float(t) for t in r.split('+') if t.strip())
def escala(a,slot):
    """Entrada de área (1 uso, no círculo base) lançada no espaço `slot`."""
    u=dict(a['usos'][0]); base=u['slot']; up=slot-base; regra=ESCALA.get(a['nome'])
    if regra and up>0:
        if regra[0]=="dado":
            n,x,r=_dados(u['dano']); u['dano']=f"{n+regra[1]*up}d{x}{r}"
        else: u['alvos']=u['alvos']+regra[1]*up
    u['slot']=slot
    e={"nome":a['nome']+(f" ({slot}º)" if regra else ""),"usos":[u]}
    if a.get('concentracao'): e['concentracao']=a['concentracao']   # M5b: a concentração sobrevive ao upcast
    return e
def _valor(a): u=a['usos'][0]; return u['alvos']*_media(u['dano'])
def area_pico(areas,esp):
    """[(entrada escalada), ...] em ordem de dano esperado e os espaços gastos."""
    sl=sorted((int(k) for k,q in esp.items() for _ in range(int(q))),reverse=True)[:2]
    if not areas or not sl: return [],[]
    cands=[]
    if len(areas)==1: pares=[(areas[0],areas[0])]
    else: pares=[(x,y) for x in areas for y in areas if x is not y]
    # M5b: no pico, no máximo uma área de concentração (a 2ª derrubaria a 1ª); a mesma de concentração não repete
    pares=[(x,y) for x,y in pares if not (x.get('concentracao') and y.get('concentracao'))] or [(x,x) for x in areas if not x.get('concentracao')] or [(areas[0],None)]
    for x,y in pares:
        if x['usos'][0]['slot']>sl[0]: continue
        usa=[(x,sl[0])]+([(y,sl[1])] if y is not None and len(sl)>1 and y['usos'][0]['slot']<=sl[1] and not (y is x and x.get('concentracao')) else [])
        e=[escala(a,s) for a,s in usa]
        cands.append((sum(_valor(z) for z in e),e,[s for _,s in usa]))
    if not cands: return [],[]
    _,e,ss=max(cands,key=lambda c:c[0])
    ordem=sorted(range(len(e)),key=lambda i:-_valor(e[i]))
    return [e[i] for i in ordem],[ss[i] for i in ordem]
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
        a=list(areas); ap,sp=area_pico(a,esp)
        ln("area",cant(0.5 if len(ap)>1 else 0.75),controle=base_ctl,area=ap,gasta=gasto(*sp),invocacoes=[],**dfs)
        ac=[x for x in a if not x.get('concentracao')]   # M5b: o combo já tem a concentração do controle
        if ctrl and ac:
            ln("combo",cant(0.5),controle={"atencao":AT(front,papel),"fontes":[FF(controle_fonte(list(ctrl)))]+list(ctl_extra)},area=ac,
               gasta=gasto(top,*[u['slot'] for x in ac for u in x['usos']]),invocacoes=[],**dfs)
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
def _anula(ant,novo,chave=None):
    """Patch cumulativo exato (19/11): o merge da progressão é recursivo, então chaves que existiam no nível anterior e
    sumiram neste (ex.: um espaço que a linha deixou de gastar) viram null, e linhas que sumiram viram _remover."""
    if chave=='linhas':
        ids={l['id'] for l in novo}; pa={l['id']:l for l in ant}
        out=[_anula(pa[l['id']],l) if l['id'] in pa else l for l in novo]
        return out+[{"id":i,"_remover":True} for i in pa if i not in ids]
    if isinstance(ant,dict) and isinstance(novo,dict):
        out={}
        for k,v in novo.items(): out[k]=_anula(ant[k],v,k) if k in ant else v
        for k in ant:
            if k not in novo and k not in ('principal','custo','hipotese'): out[k]=None   # só na base
        return out
    return novo
def escrever(id_,slug,nome,build,desc,fatias):
    b=fatias[3]; base=dict(build=build,corpo=b['corpo'],recursos=b['recursos'],linhas=b['linhas'],planos={"padrao":"auto","combate_unico":"auto"},descricao=desc)
    base['linhas'][0]['principal']=True; base['linhas'][0]['custo']='gratuita'; base['linhas'][0]['hipotese']='só truques (anel interno)'
    for l in base['linhas'][1:]: l.setdefault('hipotese',l['id'])
    niv={}; ant=dict(corpo=base['corpo'],recursos=base['recursos'],linhas=base['linhas'])
    for L in (5,7,9,11):
        f=fatias[L]
        for l in f['linhas']:
            if l['id']=='principal': l.pop('herda',None)
            else: l.setdefault('hipotese',l['id'])
        cur=json.loads(json.dumps(dict(corpo=f['corpo'],recursos=f['recursos'],linhas=f['linhas'])))
        niv[str(L)]=dict(_texto=f.get('_texto',''),**_anula(ant,json.loads(json.dumps(cur))))
        ant=cur
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
