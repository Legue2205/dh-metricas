"""Warlock (RPGBot, 2014) — passada 1 do mutirão de 21/11. Chassi do handbook por subclasse (as páginas de build
não foram lidas por prazo; ver relatorio-warlock.md). Usa wiz.fatia com espaços de pacto (voltam no descanso curto)."""
import sys, os, json; sys.path.insert(0, os.path.dirname(__file__))
import wiz
from wiz import *
PACTO={3:(2,2),5:(2,3),7:(2,4),9:(2,5),11:(3,5)}           # (quantidade, nível do espaço)
wiz.espacos=lambda cl,wl,ma=True: {str(PACTO[cl][1]):PACTO[cl][0]}
def dc(L,c): return 8+prof(L)+c
def at(L,c): return prof(L)+c
def eb(L,a,c,n,hex_=False,extra=""):
    d=f"1d10+{c}"+("+1d6" if hex_ else "")+extra
    return {"ataques":[{"n":round(n*k(L),3),"bonus":a,"dano":d,"nota":"Eldritch Blast + Agonizing Blast"+(" + Hex" if hex_ else "")}]}
def lamina(L,a,c,n,hex_=False,curse=0):
    """curse = bônus médio do Hexblade's Curse por golpe (1/descanso curto ÷ 2 lutas = PB/2; crítico em 19 não contado)."""
    d=f"1d8+{c}"+("+1d6" if hex_ else "")+(f"+{curse:g}" if curse else "")
    x={"n":n*(2 if L>=5 else 1),"bonus":a,"dano":d,"nota":"espada longa do pacto"+(" + Thirsting Blade" if L>=5 else "")+(" + Hex" if hex_ else "")+(" + Hexblade's Curse" if curse else "")}
    return {"ataques":[x]}
HOLD=lambda cd: U("Hold Person","hold_person",cd,2)
HYPN=lambda cd: U("Hypnotic Pattern","hypnotic_pattern",cd,3,area=True)
BANI=lambda cd: U("Banishment","banishment",cd,4)
HMON=lambda cd: U("Hold Monster","hold_monster",cd,5)
SYNS=lambda cd: U("Synaptic Static","synaptic_static",cd,5,area=True)
EVAR=lambda cd: U("Evard's Black Tentacles","evards_black_tentacles",cd,4,area=True)
LAUG=lambda cd: U("Tasha's Hideous Laughter","tashas_hideous_laughter",cd,1)
SHAT=lambda cd: area_sp("Shatter",2,"3d8",cd,2)
FIRE=lambda cd: area_sp("Fireball",4,"8d6",cd,3)
LBOL=lambda cd: area_sp("Lightning Bolt",3,"8d6",cd,3)
CONE=lambda cd: area_sp("Cone of Cold",4,"8d8",cd,5)
def ctrl_pad(L,cd,extra=()):
    o=[HOLD(cd)]
    if L>=5: o+= [HYPN(cd), U("Hunger of Hadar","hunger_of_hadar",cd,3,area=True), U("Fear","fear",cd,3,area=True)]   # 25/11
    if L>=7: o.append(BANI(cd))
    if L>=9: o.append(HMON(cd))
    if L>=11: o.append(SYNS(cd))
    return o+[f(cd) for lv,f in extra if L>=lv]
def inv_pad(L,a):
    pl=PACTO[L][1]
    if L<5: return None
    if L<7: return dict(i=summon('shadowspawn',pl,a),slot=pl)
    return dict(i=summon('aberration',pl,a),slot=pl)
def ajusta(f,L):
    """Espaços de pacto: todo gasto vira o nível do pacto; descanso curto devolve."""
    pl=str(PACTO[L][1]); f['recursos']['espacos_volta']='curto'
    for l in f['linhas']:
        g=l.get('gasta',{}).get('espacos')
        if g: l['gasta']['espacos']={pl:round(sum(g.values()),3)}
    return f
def kit_m4(f, L, cd, front=False):
    """M4 (23/11): Armor of Agathys, Darkness + Devil's Sight e Hunger of Hadar como linhas-opção (espaço do pacto).
    - Agathys: PV temporários = 5 × nível do pacto; retaliação de frio (mesmo valor) uma vez por luta, só se atacado
      corpo a corpo (1,0 na linha de frente, 0,4 na retaguarda), espalhada pelos rounds; sem concentração.
    - Darkness + Devil's Sight (supõe a invocação): vantagem em ~75% dos ataques dele, desvantagem contra ele;
      concentração. Aliados dentro da escuridão não modelados.
    - Hunger of Hadar (5+): área de 20 pés por ~2 rounds (2d6 frio sem save + 2d6 ácido com save de Des por round
      ≈ 6d6 com save); concentração. Cegueira e terreno difícil ainda não entram no controle."""
    from dh.premissas import P
    pn = PACTO[L][1]; pl = str(pn); R = P('base.rounds_por_luta'); p0 = f['linhas'][0]
    d0 = json.loads(json.dumps(p0['dano'])); df0 = dict(p0.get('defesa') or {})
    ret = 5 * pn * (1.0 if front else 0.4) / R
    da = dict(d0, por_turno=d0.get('por_turno', []) + [{"dano": f"{ret:.2f}", "nota": "Armor of Agathys: retaliação (1×/luta)"}])
    f['linhas'].append(dict(id="agathys", herda="principal", hipotese=f"Armor of Agathys ({pn}º: {5 * pn} PV temporários + retaliação)",
                            dano=da, defesa=dict(df0, pvt_luta=df0.get('pvt_luta', 0) + 5 * pn), gasta={"espacos": {pl: 1}}))
    if L >= 3:
        dt = dict(d0, ataques=[dict(x, vantagem=0.75) for x in d0['ataques']], concentracao="darkness")
        f['linhas'].append(dict(id="trevas", herda="principal", hipotese="Darkness + Devil's Sight: vantagem nos ataques, desvantagem contra ele",
                                dano=dt, defesa=dict(df0, adv=-1), gasta={"espacos": {pl: 1}}))
    if L >= 5:
        f['linhas'].append(dict(id="hadar", herda="principal", hipotese="Hunger of Hadar (≈2 rounds de dano na área)",
                                area=[{"nome": "Hunger of Hadar", "concentracao": "hunger_of_hadar",
                                       "usos": [{"alvos": 3, "dano": "6d6", "cd": cd, "slot": pn}]}],
                                gasta={"espacos": {pl: 1}}))
    return f


CHA={3:3,5:4,7:4,9:5,11:5}
def gera(id_,slug,nome,build,desc,sub):
    F={}
    for L in (3,5,7,9,11):
        c=CHA[L]; cd=dc(L,c); a=at(L,c); con=2; dx=2 if sub!='hexblade' else 1
        m=M(0,dx,con,0,1,c); pv=hpcalc([8]*L,con)
        ca=15 if sub!='hexblade' else (17 if L<5 else 18)
        o=sub_cfg(sub,L,c,cd,a)
        cant=o.get('cant') or (lambda n,L=L,a=a,c=c: eb(L,a,c,n))
        f=fatia(L,L,0,m,('sab','car'),ca,pv,cant,o.get('ctrl',ctrl_pad(L,cd)),None,o.get('areas',[SHAT(cd)]+([FIRE(cd)] if False else [])),
                o.get('inv',inv_pad(L,a)),o.get('extra',[]),shield=False,mage_armor=False,
                papel=o.get('papel','conjurador'),front=o.get('front',False),ctl_extra=o.get('ctl_extra',()))
        pl=str(PACTO[L][1])
        hx=dict(id="hex",herda="principal",hipotese="Hex (1 hora: 0,5 espaço por luta) no truque principal",
                dano=o.get('cant_hex',lambda n: eb(L,a,c,n,True))(1.0),gasta={"espacos":{pl:0.5}})
        f['linhas'].insert(1,hx)
        if L>=11:   # passada 2: Mystic Arcanum (6º, 1/descanso longo) = Mass Suggestion (não concentração)
            mf=U("Mass Suggestion (Mystic Arcanum)","mass_suggestion",cd,6,area=True)['f']
            f['linhas'].append(dict(id="arcano",herda="principal",hipotese="Mystic Arcanum: Mass Suggestion no pico",
                dano=cant(0.75),controle={"atencao":AT(o.get('front',False),o.get('papel','conjurador')),"fontes":[mf]},gasta={"arcano":1}))
            o.setdefault('outros',{})['arcano']={"qtd":1,"volta":"longo"}
        # passada 2: Hex (concentração, 1 hora) junto com linhas sem concentração (área, Mass Suggestion): variante "+hex"
        n0=f['linhas'][0]['dano']['ataques'][0]['n']
        for l in list(f['linhas']):
            if l['id'] in ('area','arcano'):
                fr=l['dano']['ataques'][0]['n']/n0; g=json.loads(json.dumps(l.get('gasta',{})))
                g.setdefault('espacos',{}); g['espacos']['9']=0.5   # 9 = marcador; ajusta() junta no nível do pacto
                f['linhas'].append(dict(l,id=l['id']+'+hex',hipotese=l.get('hipotese',l['id'])+' + Hex',
                    dano=o.get('cant_hex',lambda n: eb(L,a,c,n,True))(fr),gasta=g))
        kit_m4(f, L, cd, o.get('front', False))   # M4 (23/11)
        for kk,v in o.get('corpo',{}).items(): f['corpo'][kk]=v
        if o.get('outros'): f['recursos']['outros']=o['outros']
        for l in f['linhas']:
            for kk,v in o.get('todas',{}).items():
                if not l.get(kk): l[kk]=json.loads(json.dumps(v))
        F[L]=ajusta(f,L); F[L]['_texto']=f"Warlock {L}; Car {10+2*c}; pacto {PACTO[L][0]}×{PACTO[L][1]}º."+o.get('txt','')
    escrever(id_,slug,nome,build,desc,F)
def sub_cfg(sub,L,c,cd,a):
    p=prof(L); o={}
    if sub=='hexblade':
        o['cant']=lambda n: lamina(L,a,c,n,False,p/2); o['cant_hex']=lambda n: lamina(L,a,c,n,True,p/2)
        o['papel']='striker'; o['front']=True
        ar=[SHAT(cd)]+([CONE(cd)] if L>=9 else []); o['areas']=ar
    elif sub=='fiend':
        o['corpo']={"pvt_luta":c+L}; o['txt']=" Dark One's Blessing: 1 abate por luta."
        o['areas']=[SHAT(cd)]+([FIRE(cd)] if L>=5 else [])
    elif sub=='genie':
        o['cant']=lambda n: dict(eb(L,a,c,n),por_turno=[{"dano":str(p),"nota":"Genie's Wrath (1×/turno)"}])
        o['cant_hex']=lambda n: dict(eb(L,a,c,n,True),por_turno=[{"dano":str(p),"nota":"Genie's Wrath (1×/turno)"}])
        o['areas']=[SHAT(cd)]+([FIRE(cd)] if L>=5 else [])
    elif sub=='great-old-one':
        o['ctrl']=ctrl_pad(L,cd,[(3,LAUG),(7,EVAR)])
        if L>=7: o['todas']={"defesa":{"reacoes":[{"tipo":"desvantagem","usos_luta":0.5}]}}
    elif sub=='celestial':
        hl={"nome":"Healing Light (levanta um caído)","lado":"def","modelo":"cura_na_luta","alcance":"distancia","usos_luta":1,"pv":round(min(c,5)*3.5,1)}
        o['todas']={"suporte":{"fontes":[hl]}}
    elif sub=='fathomless':
        t=min(1.0,p/4); dd="2d8" if L>=10 else "1d8"
        o['cant']=lambda n: {"ataques":eb(L,a,c,n)["ataques"]+[{"n":t,"bonus":a,"dano":dd,"nota":"Tentacle of the Deeps (PB/dia ÷ 4 lutas)"}]}
        o['cant_hex']=lambda n: {"ataques":eb(L,a,c,n,True)["ataques"]+[{"n":t,"bonus":a,"dano":dd,"nota":"Tentacle of the Deeps"}]}
        o['areas']=[SHAT(cd)]+([LBOL(cd)] if L>=5 else [])+([CONE(cd)] if L>=9 else [])
        if L>=7: o['todas']={"defesa":{"reacoes":[{"tipo":"reduz_dano","valor":4.5,"usos_luta":t}]}}
    elif sub=='undead':
        t=min(1.0,p/4); o['corpo']={"pvt_luta":round(t*(5.5+L),1)}; o['txt']=" Form of Dread: PB/dia ÷ 4 lutas."
    return o
FONTE_=lambda slug: {"tipo":"rpgbot","url":f"https://rpgbot.net/dnd5/characters/classes/warlock/subclasses/","nota":"Chassi do handbook por subclasse (2014). Passada 1 cega: só mecânica; premissas congeladas."}
wiz.FONTE=FONTE_; import wiz as _w
NM="Repelling Blast e outras invocações; cegueira e terreno difícil do Hunger of Hadar; aliados dentro do Darkness; Counterspell; Misty Step"   # M4 (23/11)
SUBS=[
 ('archfey','Archfey Warlock',"Fey Presence, Misty Escape, Beguiling Defenses"),
 ('celestial','Celestial Warlock',"Radiant Soul (EB é força), Celestial Resilience, Flaming Sphere"),
 ('fathomless','Fathomless Warlock',"Gift of the Sea, Oceanic Soul, Fathomless Plunge; Guardian Coil modelado como reduz_dano 4,5"),
 ('fiend','Fiend Warlock',"Dark One's Own Luck, Fiendish Resilience; Elemental Adept"),
 ('genie','Genie Warlock (Efreeti)',"Bottled Respite, Elemental Gift (voo), lista Dao/Djinni/Marid"),
 ('great-old-one','Great Old One Warlock',"Awakened Mind, Thought Shield; Entropic Ward como desvantagem 1/descanso curto (o ataque seguinte com vantagem não modelado)"),
 ('hexblade','Hexblade Warlock (Pact of the Blade)',"Hex Warrior, Accursed Specter, Armor of Hexes; Shield da lista expandida (custa espaço de pacto)"),
 ('undead','Undead Warlock',"Form of Dread (medo no acerto), Grave Touched, Necrotic Husk"),
 ('undying','Undying Warlock',"Among the Dead, Defy Death, Undying Nature"),
]
if __name__=='__main__':
    for slug,nome,nm in SUBS:
        b="Warlock ("+nome.split(' Warlock')[0]+"), humano variante; Car 16 (3), 18 (5), 20 (9); Agonizing Blast + Armor of Shadows"
        if slug=='hexblade': b="Warlock (Hexblade), Pact of the Blade, armadura média + escudo; Car 16/18/20; Thirsting Blade no 5"
        desc={"resumo":f"{nome}: Eldritch Blast com Agonizing Blast e Hex; espaços de pacto voltam no descanso curto." if slug!='hexblade' else "Hexblade de lâmina: espada do pacto com Carisma, Hexblade's Curse e Hex no alvo principal.",
              "estrategia":"Hex no início do dia (cobre ~2 lutas), controle (Hold Person, Hypnotic Pattern, Banishment, Hold Monster) ou invocação no espaço de pacto.",
              "nao_modelado":nm+"; "+NM}
        gera('rpgbot-warlock-'+slug,slug,nome+" (RPGBot: chassi do handbook)",b,desc,slug)
