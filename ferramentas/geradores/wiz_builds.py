import sys; sys.path.insert(0,__import__('os').path.dirname(__file__))
from wiz import *
def P_(L): return prof(L)
def dc(L,i): return 8+prof(L)+i
def at(L,i): return prof(L)+i
SHAT=lambda cd: area_sp("Shatter",2,"3d8",cd,2)

# ---------- Abjuration ----------
F={}
for L,i in ((3,3),(5,4),(7,4),(9,5),(11,5)):
    wl=L-1; cd=dc(L,i); a=at(L,i); m=M(-1,3,3,i,-1,-1)
    ward=2*wl+i; pv=hpcalc([8]+[6]*(L-1),3)+ward
    ctrl=[];ar=[];inv=None;bar=None
    if L>=5: ctrl=[WEB(cd)]; ar=[SHAT(cd)]
    if L>=7: ar=[FB(cd)]; inv=dict(i=summon('fey',4,a),slot=4)
    if L>=9: inv=dict(i=summon('aberration',5,a),slot=5)
    if L>=11: ctrl=[WEB(cd),HM(cd),WOF(cd)]; bar=WEB(cd); inv=dict(i=summon('aberration',6,a),slot=6)
    F[L]=fatia(L,L,wl,m,('con','int'),18,pv,lambda n,L=L,cd=cd: toll(L,cd,n),ctrl,bar,ar,inv,mage_armor=False)
    F[L]['_texto']=f"Artificer 1 / Wizard {wl}; Arcane Ward {ward} somado ao PV."
escrever('rpgbot-wizard-abjuration','abjuration','Abjuration Wizard (RPGBot: Krump Your Pointy Hat Pajama Man)',
 "Artificer 1 / Wizard (Abjuration), Orc (MMoM), armadura média + escudo; Int 18 (personagem 5), Int 20 (9)",
 {"resumo":"Abjurador com armadura média e escudo (dip de Artificer), Arcane Ward como PV extra, que joga de invocador (Summon Fey/Aberration).",
  "estrategia":"Toll the Dead e Shield no dia a dia; Web para controlar, Fireball em grupos, invocações de 1 hora para cobrir duas lutas.",
  "nao_modelado":"Recarga do Arcane Ward durante a luta e Projected Ward; Counterspell e Improved Abjuration; Absorb Elements; Grease, Fog Cloud, Mind Whip, Sickening Radiance; Greater Invisibility."},F)

# ---------- Bladesinging ----------
F={}
for L,dx,i in ((3,3,3),(5,3,3),(7,3,3),(9,4,4),(11,4,4)):
    cd=dc(L,i); a=at(L,i); m=M(-1,dx,2,i,0,-1); p=prof(L); ab=dx+p
    pv=hpcalc([6]*L,2); ca=13+dx; song=ca+i
    bb=f"1d6+{dx}"+("+1d8" if 5<=L<11 else "+2d8" if L>=11 else "")
    mel=[{"n":1,"bonus":ab,"dano":bb,"nota":"Booming Blade (espada curta)"}]
    if L>=7: mel.append({"n":1,"bonus":ab,"dano":f"1d6+{dx}","nota":"Extra Attack"})
    mel.append({"n":1,"bonus":ab,"dano":"1d6","nota":"espada curta na mão inábil (ação bônus)"})
    pt=[{"dano":"0.75","nota":"Piercer"},{"dano":"1d6","gatilho":"critico"}] if L>=5 else []
    fury=[{"usos_dia":p,"dano":str(p),"nota":"Fury of the Small (PB/dia)"}]
    def cant(n,L=L,a=a,dx=dx,ab=ab):
        if L<5: return xbow(L,ab,dx,n)
        d=fire_bolt(L,a,n)
        if L>=7: d["ataques"].append({"n":n,"bonus":ab,"dano":f"1d8+{dx}","nota":"besta leve (Extra Attack com truque)"})
        return d
    ctrl=[];ar=[]
    if L>=5: ar=[FB(cd)]
    if L>=7: ctrl=[U("Polymorph","polymorph",cd,4)]
    if L>=9: ctrl=[U("Polymorph","polymorph",cd,4),WOF(cd)]
    f=fatia(L,L,L,m,('int','sab'),ca,pv,cant,ctrl,None,ar)
    canto=dict(id="canto",herda="principal",hipotese="Bladesong + corpo a corpo (Booming Blade)",corpo={"ca":song},
        dano=dict(ataques=mel,por_luta=fury,**({"por_turno":pt} if pt else {})),
        controle={"atencao":dict(AT(True,'striker'),dpr="auto"),"fontes":[{"tipo":"ameaca","nome":"Corpo (ameaça)"}]},
        defesa=SH,reacao=RE,gasta={"bladesong":1,"espacos":{"1":1}},area=[],invocacoes=[])
    f['linhas'].append(canto)
    if L>=5:
        hz=dict(canto,id="canto-haste",hipotese="Bladesong + Haste em si mesmo",corpo={"ca":song+2},
                dano=dict(canto['dano'],ataques=mel+[{"n":0.75,"bonus":ab,"dano":f"1d6+{dx}","nota":"ataque do Haste"}]),
                gasta={"bladesong":1,"espacos":{"1":1,"3":1}},plano="prioritaria")
        f['linhas'].append(hz)
    if L>=11:
        t=[{"n":2,"bonus":ab,"dano":f"1d6+{dx}+2d12","vantagem":1.0},{"n":1,"bonus":ab,"dano":"1d6+2d12","vantagem":1.0,"nota":"mão inábil"}]
        f['linhas'].append(dict(canto,id="canto-tenser",hipotese="Bladesong + Tenser's Transformation (1/dia, sem magias)",
            dano=dict(ataques=t,por_luta=fury,por_turno=pt),defesa={},reacao=[],gasta={"bladesong":1,"espacos":{"6":1}},plano="prioritaria"))
    f['recursos']['outros']={"bladesong":{"qtd":p,"volta":"longo"}}
    f['_texto']=f"Wizard {L}; Bladesong {p}/dia (CA {song})."
    F[L]=f
escrever('rpgbot-wizard-bladesinging','bladesinging','Bladesinging Wizard (RPGBot: Goblin Bladesinger)',
 "Wizard (Bladesinging), Goblin (MMoM), duas espadas curtas + Booming Blade; Piercer 4, Des/Int 18 (8)",
 {"resumo":"Bladesinger goblin de duas espadas curtas: Booming Blade com Bladesong e Haste, Fireball e Wall of Force quando vale mais ser mago.",
  "estrategia":"Liga o Bladesong nas lutas em que entra no corpo a corpo; fora delas, besta e Fire Bolt de longe.",
  "nao_modelado":"Dano secundário do Booming Blade; Song of Defense; disengage do Goblin; Absorb Elements; Magic Weapon e Shadow Blade; Greater Invisibility; Polymorph em si mesmo."},F)

# ---------- Chronurgy ----------
F={}
for L,i in ((3,3),(5,4),(7,4),(9,5),(11,5)):
    wl=L-1; cd=dc(L,i); a=at(L,i); m=M(-1,2,2,i,2,-1)
    pv=hpcalc([8]+[6]*(L-1),2)
    ctrl=[];bar=None
    if L>=5: ctrl=[WEB(cd)]
    if L>=7: ctrl=[WEB(cd),HYP(cd)]; bar=WEB(cd)
    if L>=9: ctrl=[WEB(cd),HYP(cd),EBT(cd),BAN(cd)]
    if L>=11: ctrl=[WEB(cd),HYP(cd),EBT(cd),BAN(cd),HM(cd)]
    f=fatia(L,L,wl,m,('sab','car'),18,pv,lambda n,L=L,a=a: fire_bolt(L,a,n),ctrl,bar,mage_armor=False,ff=0.5)
    if L>=7:
        f['linhas'].append({"id":"estase","herda":"principal","hipotese":"Momentary Stasis num alvo (Int/dia ÷ 4 lutas), no lugar de 1 truque",
            "dano":fire_bolt(L,a,0.75),"controle":{"atencao":AT(),"fontes":[{"tipo":"condicao_no_acerto","nome":"Momentary Stasis","efeito":"cond_estase","cd":cd,"no_acerto":False,"usos":round(i/4,2)}]},
            "area":[],"invocacoes":[],"defesa":{}})
    f['_texto']=f"Cleric 1 (Twilight) / Wizard {wl}."
    F[L]=f
escrever('rpgbot-wizard-chronurgy','chronurgy-magic','Chronurgy Wizard (RPGBot: Hare Today, Gone Tomorrow)',
 "Cleric 1 (Twilight) / Wizard (Chronurgy), Harengon, armadura média + escudo; Int 18 (personagem 5), Int 20 (9)",
 {"resumo":"Cronurgista com dip de Clérigo da Twilight (armadura, escudo, vantagem na iniciativa): vence a iniciativa e abre com área de controle.",
  "estrategia":"Fire Bolt no dia a dia; Web e Hypnotic Pattern no 1º round, Momentary Stasis num alvo isolado.",
  "nao_modelado":"Iniciativa (Temporal Awareness, Vigilant Blessing); Chronal Shift fora do save das magias (aliados, críticos); Arcane Abeyance; Silvery Barbs; magias de Clérigo (Bless, Healing Word, Faerie Fire); Counterspell; Sickening Radiance."},F)

# ---------- Conjuration ----------
F={}
for L,i in ((3,3),(5,4),(7,4),(9,5),(11,5)):
    cd=dc(L,i); a=at(L,i); m=M(-1,3,2,i,1,-1); pv=hpcalc([6]*L,2)
    ctrl=[WEB(cd)]; inv=None; bar=None
    if L>=5: inv=dict(i=summon('shadowspawn',3,a),slot=3)
    if L>=7: ctrl=[WEB(cd),EBT(cd)]; bar=WEB(cd); inv=dict(i=summon('shadowspawn',4,a),slot=4)
    if L>=9: inv=dict(i=summon('shadowspawn',5,a),slot=5)
    if L>=11: inv=dict(i=summon('shadowspawn',6,a),slot=6)
    F[L]=fatia(L,L,L,m,('int','sab'),17,pv,lambda n,L=L,cd=cd: sliver(L,cd,n),ctrl,bar,(),inv,mage_armor=False)
    F[L]['_texto']=f"Wizard {L}; Tortle (CA 17)."
escrever('rpgbot-wizard-conjuration','conjuration','Conjuration Wizard (RPGBot: Generic Conjurer)',
 "Wizard (Conjuration), Tortle, Int 18 (4), Int 20 (8); Summon Shadowspawn como invocação padrão",
 {"resumo":"Conjurador invocador (Tortle, CA 17): Summon Shadowspawn de 1 hora para cobrir lutas, Web e Black Tentacles quando a invocação cai.",
  "estrategia":"Abre com a invocação no maior espaço e Mind Sliver; Web para segurar grupos.",
  "nao_modelado":"Benign Transposition, Focused Conjuration, Durable Summons; Conjure Woodland Beings; Steel Wind Strike; Vortex Warp; Scatter; Absorb Elements."},F)

# ---------- Divination ----------
F={}
for L in (3,5,7,9,11):
    i=3; cd=dc(L,i); a=at(L,i); m=M(-1,2,1,i,2,-1); pv=hpcalc([6]*L,1)
    SUG=U("Suggestion","suggestion",cd,2)
    ctrl=[WEB(cd),SUG]; inv=None; bar=None
    if L>=5: ctrl=[WEB(cd),SUG,HYP(cd)]; bar=WEB(cd); inv=dict(i=summon('undead',3,a),slot=3)
    if L>=7: inv=dict(i=summon('aberration',4,a),slot=4)
    if L>=9: ctrl=[WEB(cd),SUG,HYP(cd),BAN(cd),dict(f={"tipo":"condicao_no_acerto","nome":"Psychic Lance","efeito":"psychic_lance","cd":cd,"no_acerto":False,"usos":1},slot=4),WOF(cd)]; inv=dict(i=summon('aberration',5,a),slot=5)
    if L>=11: ctrl=ctrl+[HM(cd),SYN(cd)]; inv=dict(i=summon('aberration',6,a),slot=6)
    F[L]=fatia(L,L,L,m,('int','sab'),15,pv,lambda n,L=L,cd=cd: sliver(L,cd,n),ctrl,bar,(),inv,ff=0.5)
    F[L]['_texto']=f"Wizard {L}; Portent 2/dia; Int 17 (Bountiful Luck 4, Lucky 8)."
escrever('rpgbot-wizard-divination','divination','Divination Wizard (RPGBot: Probability and I Don\'t Get Along)',
 "Wizard (Divination), Halfling, Int 17 até o 11; Bountiful Luck 4, Lucky 8, Fey Touched 12",
 {"resumo":"Adivinho que manipula os dados: Portent, Lucky e Silvery Barbs garantem os saves das magias de controle; evita rolar ataques.",
  "estrategia":"Mind Sliver antes do save; Web, Hypnotic Pattern, Banishment e Psychic Lance escolhidos pelo save fraco do alvo.",
  "nao_modelado":"Portent nos aliados (ataques e saves) e nos ataques inimigos (só entra forçando falha no save das magias); Lucky, Bountiful Luck e Silvery Barbs; Expert Divination; Create Bonfire; Dragon's Breath no familiar; Mind Spike."},F)

# ---------- Enchantment ----------
F={}
for L,i in ((3,3),(5,3),(7,3),(9,4),(11,4)):
    cd=dc(L,i); a=at(L,i); m=M(-1,2,2,i,-1,2); pv=hpcalc([6]*L,2)
    THL=U("Tasha's Hideous Laughter","tashas_hideous_laughter",cd,1)
    ctrl=[THL]; bar=None
    if L>=5: ctrl=[THL,HP_(cd)]; bar=THL
    if L>=7: ctrl=[THL,HP_(cd),dict(f={"tipo":"condicao_no_acerto","nome":"Psychic Lance","efeito":"psychic_lance","cd":cd,"no_acerto":False,"usos":1},slot=4)]
    if L>=9: ctrl=[HP_(cd),dict(f={"tipo":"condicao_no_acerto","nome":"Psychic Lance","efeito":"psychic_lance","cd":cd,"no_acerto":False,"usos":1},slot=4),BAN(cd),HM(cd)]; bar=HP_(cd)
    if L>=11: ctrl=[HP_(cd),dict(f={"tipo":"condicao_no_acerto","nome":"Psychic Lance (Split Enchantment: 2 alvos)","efeito":"psychic_lance","cd":cd,"no_acerto":False,"usos":2},slot=4),BAN(cd),U("Hold Monster (Split Enchantment)","hold_monster",cd,5,alvos=2)]
    f=fatia(L,L,L,m,('int','sab'),15,pv,lambda n,L=L,cd=cd: sliver(L,cd,n),ctrl,bar)
    f['linhas'].append({"id":"olhar","herda":"principal","hipotese":"Hypnotic Gaze: chega a 5 pés e gasta a ação para manter um alvo incapacitado (sem truques)",
        "dano":{"ataques":[]},"controle":{"atencao":AT(True),"fontes":[{"tipo":"condicao_no_acerto","nome":"Hypnotic Gaze","efeito":"cond_hipnotizado","cd":cd,"no_acerto":False,"usos":2},{"tipo":"ameaca","nome":"Corpo (ameaça)"}]},
        "defesa":SH,"reacao":RE,"gasta":{"espacos":{"1":1}},"area":[],"invocacoes":[]})
    f['_texto']=f"Wizard {L}."+(" Split Enchantment: Hold Monster e Psychic Lance em 2 alvos." if L>=11 else "")
    F[L]=f
escrever('rpgbot-wizard-enchantment','enchantment','Enchantment Wizard (RPGBot: Say the Magic Word(s))',
 "Wizard (Enchantment), Kenku, Car 14 para Face; Telekinetic 4, Int 18 (8)",
 {"resumo":"Encantador que também é Face: Hypnotic Gaze sem custo, Hold Person/Monster e Psychic Lance, em dois alvos a partir do 10.",
  "estrategia":"Mind Sliver de longe; olhar hipnótico no alvo prioritário quando a party está em vantagem numérica; Hold Monster no chefe.",
  "nao_modelado":"Instinctive Charm; Enemies Abound; Mind Whip; Sleep; Otto's Irresistible Dance; Telekinetic (empurrão); Face fora de combate."},F)

# ---------- Evocation ----------
F={}
for L,i in ((3,3),(5,3),(7,3),(9,4),(11,4)):
    cd=dc(L,i); a=at(L,i); m=M(-1,3,3,i,-1,-1); pv=hpcalc([6]*L,3)
    emp=i if L>=11 else 0; pot=L>=7
    ar=[area_sp("Shatter",2,"3d8",cd,2,sel=True)]; ctrl=[]
    if L>=5: ar=[FB(cd,emp,sel=True)]
    if L>=7: ctrl=[HYP(cd)]
    if L>=9: ctrl=[HYP(cd),SYN(cd)]; ar=[FB(cd,emp,sel=True),area_sp("Cone of Cold",6,"8d8"+(f"+{emp}" if emp else ""),cd,5,sel=True)]
    if L>=11: ar=ar+[area_sp("Chain Lightning",4,f"10d8+{emp}",cd,6,sel=True)]
    F[L]=fatia(L,L,L,m,('int','sab','con'),16,pv,lambda n,L=L,cd=cd,pot=pot: toll(L,cd,n,pot),ctrl,None,ar)
    F[L]['_texto']=f"Wizard {L}."+(" Potent Cantrip." if pot else "")+(" Empowered Evocation (+Int)." if emp else "")
escrever('rpgbot-wizard-evocation','evoker','Evocation Wizard (RPGBot: The Grenadiers March)',
 "Wizard (Evocation), Humano Variante (Resilient Con), War Caster 4; Int 18 (8), Int 20 (12)",
 {"resumo":"Evocador explosivo: Fireball, Cone of Cold e Chain Lightning sem atingir aliados, Toll the Dead com Potent Cantrip.",
  "estrategia":"Área no 1º round das lutas com grupos; Hypnotic Pattern quando precisa tirar inimigos da luta; truques no resto.",
  "nao_modelado":"Sculpt Spells (fogo amigo não entra no modelo); Mind Whip; Wall of Fire e Sickening Radiance; Thunderclap; Silvery Barbs; vantagem de concentração do War Caster."},F)

# ---------- Graviturgy ----------
F={}
for L,i in ((3,4),(5,5),(7,5),(9,5),(11,5)):
    cd=dc(L,i); a=at(L,i); m=M(-1,2,2,i,0,-1); pv=hpcalc([6]*L,2)
    ctrl=[WEB(cd),PF(cd)]; ar=[]; bar=None
    if L>=5: ar=[area_sp("Pulse Wave",3,"6d6",cd,3)]
    if L>=7: ctrl=[WEB(cd),PF(cd),EBT(cd)]; bar=WEB(cd)
    if L>=9: ctrl=ctrl+[HM(cd)]; ar=ar+[area_sp("Gravity Fissure",4,"8d8",cd,5)]
    F[L]=fatia(L,L,L,m,('int','sab'),15,pv,(lambda n,L=L,a=a: fire_bolt(L,a,n)) if L<5 else (lambda n,L=L,a=a: ray_frost(L,a,n)),ctrl,bar,ar)
    F[L]['_texto']=f"Wizard {L}."
escrever('rpgbot-wizard-graviturgy','graviturgy-magic','Graviturgy Wizard (RPGBot: Pull!)',
 "Wizard (Graviturgy), Custom Lineage (Telekinetic, Int 18 no 1), Int 20 (4); Metamagic Adept 8",
 {"resumo":"Graviturgo controlador: área de controle no início e o resto da luta empurrando inimigos para dentro dela.",
  "estrategia":"Web ou Black Tentacles, depois Ray of Frost, Telekinetic e Gravity Well para manter todos dentro; Pulse Wave e Gravity Fissure de dano.",
  "nao_modelado":"Reposicionamento (Gravity Well, Telekinetic, Ray of Frost) que prolonga as áreas; Violent Attraction; Wall of Fire; Gravity Sinkhole; Silvery Barbs; Counterspell."},F)

# ---------- Illusion ----------
F={}
for L,i in ((3,3),(5,4),(7,4),(9,5),(11,5)):
    cd=dc(L,i); a=at(L,i); m=M(-1,2,2,i,-1,1); pv=hpcalc([6]*L,2)
    ctrl=[PF(cd)]; bar=None
    if L>=5: ctrl=[PF(cd),HYP(cd)]; bar=PF(cd)
    if L>=7: ctrl=[PF(cd),HYP(cd),U("Phantasmal Killer","phantasmal_killer",cd,4)]
    F[L]=fatia(L,L,L,m,('int','sab'),15,pv,lambda n,L=L,cd=cd: sliver(L,cd,n),ctrl,bar)
    F[L]['_texto']=f"Wizard {L}."
escrever('rpgbot-wizard-illusion','illusion','Illusion Wizard (RPGBot: Everything is an Illusion)',
 "Wizard (Illusion), Kenku, Telekinetic 4, Int 20 (8)",
 {"resumo":"Ilusionista batedor e controlador: Phantasmal Force como jaula barata, Hypnotic Pattern em grupos, Phantasmal Killer em alvos de Sab fraca.",
  "estrategia":"Esconde-se atrás de ilusões e usa Mind Sliver; controle no alvo ou grupo prioritário.",
  "nao_modelado":"Usos criativos de Minor/Silent/Major Image; Mirror Image; Illusory Self; dano do Phantasmal Killer e do Phantasmal Force; Mental Prison; Invisibility."},F)

# ---------- Necromancy ----------
F={}
for L,dx,i in ((3,3,3),(5,3,4),(7,3,4),(9,3,5),(11,3,5)):
    wl=L; cd=dc(L,i); a=at(L,i); m=M(-1,dx,1,i,-1,1); pv=hpcalc([6]*L,1); p=prof(L)
    ctrl=[EG(cd),PF(cd)]; ar=[]
    if L>=5: ar=[FB(cd)]
    if L>=9: ctrl=[EG(cd),PF(cd),EBT(cd)]
    if L>=11: ctrl=ctrl+[SYN(cd)]
    inv=dict(i=summon('undead',min(5,max(3,{3:2,5:3,7:4,9:5,11:6}[L])),a),slot={5:3,7:4,9:5,11:6}.get(L,3)) if L>=7 else None
    f=fatia(L,L,L,m,('int','sab'),16,pv,(lambda n,L=L,dx=dx,p=p: xbow(L,dx+p,dx,n)) if L<5 else (lambda n,L=L,a=a: fire_bolt(L,a,n)),ctrl,EG(cd),ar,inv)
    if L>=7:
        q=4 if L==7 else 6
        esq={"nome":"esqueletos (Undead Thralls)","quantidade":q,"pv":13+wl,"ca":16,"ataque":{"bonus":4,"dano":f"1d6+{2+p}"},"nota":"armadura média; arco curto; +PB de dano e +nível de PV"}
        for l in f['linhas']:
            l['invocacoes']=[esq]+[x for x in l.get('invocacoes',[]) if 'Summon' in x['nome']]
        s="3" if L==7 else "4"; f['recursos']['espacos'][s]-=1
    f['_texto']=f"Wizard {L}."+(f" {4 if L==7 else 6} esqueletos mantidos (1 espaço de {'3º' if L==7 else '4º'} por dia)." if L>=7 else "")
    F[L]=f
escrever('rpgbot-wizard-necromancy','necromancy','Necromancy Wizard (RPGBot: The Queen Decrees: Six Linked Minions)',
 "Wizard (Necromancy), Fairy, Telekinetic 4, Int 20 (8); esqueletos com Undead Thralls a partir do 6",
 {"resumo":"Necromante fada com uma tropa de esqueletos reforçados (Undead Thralls) que protege a party, mais Summon Undead e Fireball.",
  "estrategia":"Os esqueletos ficam junto dos aliados e atiram; o mago controla com Earthen Grasp e Phantasmal Force ou solta Fireball.",
  "nao_modelado":"Grim Harvest; Faerie Fire racial; Haste; Inspiring Leader nos esqueletos (12); Vampiric Touch; Wither and Bloom; Danse Macabre."},F)

# ---------- Order of Scribes ----------
F={}
for L,i in ((3,3),(5,4),(7,4),(9,5),(11,5)):
    cd=dc(L,i); a=at(L,i); m=M(-1,2,2,i,1,-1); pv=hpcalc([6]*L,2)
    ctrl=[EG(cd),PF(cd)]; ar=[]; inv=None; bar=EG(cd)
    if L>=5: ctrl=ctrl+[WEB(cd)]; ar=[FB(cd)]
    if L>=7: ctrl=ctrl+[BAN(cd),U("Polymorph","polymorph",cd,4)]; inv=dict(i=summon('undead',4,a),slot=4)
    if L>=9: ctrl=ctrl+[EBT(cd),SYN(cd)]; inv=dict(i=summon('undead',5,a),slot=5)
    if L>=11: ctrl=ctrl+[WOF(cd)]; inv=dict(i=summon('undead',6,a),slot=6)
    F[L]=fatia(L,L,L,m,('int','sab'),16,pv,lambda n,L=L,a=a: fire_bolt(L,a,n),ctrl,bar,ar,inv)
    F[L]['_texto']=f"Wizard {L}; Warforged (+1 CA)."
escrever('rpgbot-wizard-order-of-scribes','scribes','Order of Scribes Wizard (RPGBot: RPGBOT Self-Insert)',
 "Wizard (Order of Scribes), Warforged, Telekinetic 4, Int 20 (8), Resilient Con 12",
 {"resumo":"Escriba warforged, o mago mais mago: troca o tipo de dano das magias para fugir de resistências e controla com o melhor de cada nível.",
  "estrategia":"Fire Bolt ou Mind Sliver; Earthen Grasp/Phantasmal Force/Web no alvo ou grupo certo; Summon Undead quando não precisa concentrar em controle.",
  "nao_modelado":"Awakened Spellbook (troca de tipo de dano: resistências não entram no modelo); Manifest Mind; Master Scrivener; Enemies Abound; Wall of Fire; Eyebite."},F)

# ---------- Transmutation ----------
F={}
for L,i,c in ((3,3,3),(5,4,3),(7,4,3),(9,5,3),(11,5,3)):
    cd=dc(L,i); a=at(L,i); m=M(-1,2,c,i,0,-1); pv=hpcalc([6]*L,c)+L
    ctrl=[EG(cd)]; ar=[]; bar=None
    if L>=5: ctrl=[EG(cd)] ; ar=[FB(cd)]; bar=EG(cd)
    profs=('int','sab','con') if L>=7 else ('int','sab')
    f=fatia(L,L,L,m,profs,12,pv,lambda n,L=L,a=a: fire_bolt(L,a,n),ctrl,bar,ar,mage_armor=False)
    if L>=7:
        if L==7: forma=dict(ca=12,pv=157,at=[{"n":2,"bonus":9,"dano":"3d10+6","nota":"Giant Ape, punho"}],nome="Giant Ape")
        else: forma=dict(ca=13,pv=136,at=[{"n":1,"bonus":10,"dano":"4d12+7","nota":"T-Rex, mordida"},{"n":1,"bonus":10,"dano":"3d8+7","nota":"T-Rex, cauda"}],nome="Tyrannosaurus Rex")
        f['linhas'].append({"id":"polimorfo","herda":"principal","hipotese":f"Polymorph em si mesmo ({forma['nome']}); PV da forma somados aos do mago",
            "corpo":{"ca":forma['ca'],"pv":pv+forma['pv']},"dano":{"ataques":forma['at']},
            "controle":{"atencao":{"papel":"tank","front":True,"soft":0.15,"dpr":"auto","conc":True},"fontes":[{"tipo":"ameaca","nome":"Corpo (ameaça)"}]},
            "defesa":{},"reacao":[],"gasta":{"espacos":{"4":1}},"area":[],"invocacoes":[]})
    f['_texto']=f"Wizard {L}."+(" Transmuter's Stone: proficiência em Con." if L>=7 else "")
    F[L]=f
escrever('rpgbot-wizard-transmutation','transmutation','Transmutation Wizard (RPGBot: Polymorph into a Problem)',
 "Wizard (Transmutation), Anão da Colina, Int 19 (4), Int 20 (8); Resilient Con 12",
 {"resumo":"Transmutador que vira um monstro: Polymorph em si mesmo (Giant Ape, depois T-Rex) e volta a ser mago quando a forma cai.",
  "estrategia":"Polymorph nas lutas importantes; fora delas, Fire Bolt, Earthen Grasp, Slow e Fireball.",
  "nao_modelado":"False Life, Fire Shield e Longstrider antes da forma; Slow (a biblioteca só tem Slow em alvo único); Levitate; Telekinesis; Animate Objects; Minor Alchemy; Transmuter's Stone fora da Con."},F)

# ---------- War Magic ----------
F={}
for L,i in ((3,3),(5,4),(7,4),(9,5),(11,5)):
    wl=L-1; cd=dc(L,i); a=at(L,i); m=M(-1,3,3,i,-1,-1); pv=hpcalc([8]+[6]*(L-1),3)
    ctrl=[]; ar=[]; bar=None
    if L>=5: ctrl=[WEB(cd),HP_(cd)]
    if L>=7: ctrl=ctrl+[HYP(cd)]; ar=[FB(cd)]; bar=WEB(cd)
    if L>=9: ctrl=ctrl+[U("Phantasmal Killer","phantasmal_killer",cd,4)]
    if L>=11: ctrl=ctrl+[HM(cd)]
    f=fatia(L,L,wl,m,('con','int'),18,pv,lambda n,L=L,a=a: fire_bolt(L,a,n),ctrl,bar,ar,mage_armor=False)
    if L>=11:
        p=prof(L); sv={k_:m[k_]+(p if k_ in ('con','int') else 0)+2 for k_ in m}
        for l in f['linhas']:
            if l['id'] in ('controle','controle-barato','combo'):
                l['corpo']={"ca":20,"saves":{"sv":sv,"conjurador":True}}
    f['_texto']=f"Artificer 1 / Wizard {wl}."+(" Durable Magic: +2 CA e saves concentrando." if L>=11 else "")
    F[L]=f
escrever('rpgbot-wizard-war-magic','war-magic','War Magic Wizard (RPGBot: Trigger Discipline)',
 "Artificer 1 / Wizard (War Magic), Harengon, armadura média + escudo; Int 18 (personagem 5), Int 20 (9)",
 {"resumo":"Mago de guerra que sempre age primeiro (Harengon + Tactical Wit), com armadura e escudo, e abre a luta com controle.",
  "estrategia":"Vence a iniciativa e solta Web, Hold Person ou Hypnotic Pattern antes de todos; Fire Bolt no resto.",
  "nao_modelado":"Iniciativa (Tactical Wit, Hare Trigger, Alert); Arcane Deflection; Power Surge; Sleep e Fog Cloud; Polymorph; Sickening Radiance e Wall of Fire."},F)

# ================= extensões simples (sem multiclasse) =================
PURO="Extensão simples da build do RPGBot sem a multiclasse (níveis adiantados, atributos e feats remendados); a build original continua como referência."
# Abjuration pura
F={}
for L,i in ((3,3),(5,4),(7,4),(9,5),(11,5)):
    cd=dc(L,i); a=at(L,i); m=M(-1,3,3,i,-1,-1); ward=2*L+i; pv=hpcalc([6]*L,3)+ward
    ctrl=[WEB(cd)]; ar=[SHAT(cd)]; inv=None; bar=None
    if L>=5: ar=[FB(cd)]
    if L>=7: inv=dict(i=summon('aberration',4,a),slot=4)
    if L>=9: ctrl=[WEB(cd),HM(cd),WOF(cd)]; bar=WEB(cd); inv=dict(i=summon('aberration',5,a),slot=5)
    if L>=11: inv=dict(i=summon('aberration',6,a),slot=6)
    F[L]=fatia(L,L,L,m,('int','sab'),16,pv,lambda n,L=L,cd=cd: toll(L,cd,n),ctrl,bar,ar,inv)
    F[L]['_texto']=f"Wizard {L} (sem Artificer): Mage Armor + Shield; Arcane Ward {ward}."
escrever('rpgbot-wizard-abjuration-puro','abjuration','Abjuration Wizard puro (extensão da build do RPGBot)',
 "Wizard (Abjuration) sem multiclasse, Orc (MMoM), Mage Armor; Int 18 (4), Int 20 (8), Resilient Con no 12 no lugar do Medium Armor Master",
 {"resumo":"A build Krump Your Pointy Hat Pajama Man sem o nível de Artificer: Mage Armor e Shield no lugar de armadura e escudo, magias um nível antes.",
  "estrategia":PURO,
  "nao_modelado":"Recarga do Arcane Ward durante a luta e Projected Ward; Counterspell e Improved Abjuration; Absorb Elements; sem proficiência em Con até o 12."},F)
# Chronurgy pura
F={}
for L,i in ((3,3),(5,4),(7,4),(9,5),(11,5)):
    cd=dc(L,i); a=at(L,i); m=M(-1,2,3,i,1,-1); pv=hpcalc([6]*L,3)
    ctrl=[WEB(cd)]; bar=None
    if L>=5: ctrl=[WEB(cd),HYP(cd)]; bar=WEB(cd)
    if L>=7: ctrl=[WEB(cd),HYP(cd),EBT(cd),BAN(cd)]
    if L>=9: ctrl=ctrl+[HM(cd)]
    f=fatia(L,L,L,m,('int','sab'),15,pv,lambda n,L=L,a=a: fire_bolt(L,a,n),ctrl,bar,ff=0.5)
    if L>=7:
        f['linhas'].append({"id":"estase","herda":"principal","hipotese":"Momentary Stasis num alvo (Int/dia ÷ 4 lutas)",
            "dano":fire_bolt(L,a,0.75),"controle":{"atencao":AT(),"fontes":[{"tipo":"condicao_no_acerto","nome":"Momentary Stasis","efeito":"cond_estase","cd":cd,"no_acerto":False,"usos":round(i/4,2)}]},
            "area":[],"invocacoes":[],"defesa":{}})
    f['_texto']=f"Wizard {L} (sem Cleric): Mage Armor; Int 18 (4), 20 (8)."
    F[L]=f
escrever('rpgbot-wizard-chronurgy-puro','chronurgy-magic','Chronurgy Wizard puro (extensão da build do RPGBot)',
 "Wizard (Chronurgy) sem multiclasse, Harengon, Mage Armor; Int 18 (4), Int 20 (8)",
 {"resumo":"A build Hare Today, Gone Tomorrow sem o nível de Clérigo: perde armadura e escudo e a vantagem de iniciativa, ganha magias e Chronal Shift um nível antes.",
  "estrategia":PURO,"nao_modelado":"Iniciativa; Chronal Shift fora do save das magias; Arcane Abeyance; Silvery Barbs; Counterspell."},F)
# War Magic pura
F={}
for L,i in ((3,3),(5,4),(7,4),(9,5),(11,5)):
    cd=dc(L,i); a=at(L,i); m=M(-1,3,3,i,-1,-1); pv=hpcalc([6]*L,3)
    ctrl=[WEB(cd),HP_(cd)]; ar=[]; bar=None
    if L>=5: ctrl=ctrl+[HYP(cd)]; ar=[FB(cd)]; bar=WEB(cd)
    if L>=7: ctrl=ctrl+[U("Phantasmal Killer","phantasmal_killer",cd,4)]
    if L>=9: ctrl=ctrl+[HM(cd)]
    f=fatia(L,L,L,m,('int','sab'),16,pv,lambda n,L=L,a=a: fire_bolt(L,a,n),ctrl,bar,ar)
    if L>=11:
        p=prof(L); sv={k_:m[k_]+(p if k_ in ('int','sab') else 0)+2 for k_ in m}
        for l in f['linhas']:
            if l['id'] in ('controle','controle-barato','combo'): l['corpo']={"ca":18,"saves":{"sv":sv,"conjurador":True}}
    f['_texto']=f"Wizard {L} (sem Artificer): Mage Armor + Shield."+(" Durable Magic." if L>=11 else "")
    F[L]=f
escrever('rpgbot-wizard-war-magic-puro','war-magic','War Magic Wizard puro (extensão da build do RPGBot)',
 "Wizard (War Magic) sem multiclasse, Harengon, Mage Armor; Int 18 (4), Int 20 (8), Resilient Con no 12 no lugar do Alert",
 {"resumo":"A build Trigger Discipline sem o nível de Artificer: Mage Armor e Shield, magias e Durable Magic um nível antes.",
  "estrategia":PURO,"nao_modelado":"Iniciativa; Arcane Deflection; Power Surge; sem proficiência em Con até o 12."},F)
