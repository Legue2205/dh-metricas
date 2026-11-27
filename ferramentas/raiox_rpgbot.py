"""Raio-x das builds do RPGBot (painel Data, 27/11). Uso: python ferramentas/raiox_rpgbot.py [saida.json]"""
import json, subprocess, sys, glob, os, re
SAIDA = sys.argv[1] if len(sys.argv) > 1 else 'builds-rpgbot.json'
R=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'); sys.path.insert(0,R+'/calibracao')
from comparar_chassi import pista, ESCALA, HOLDOUT, dados, rotulos, val
def cmp(g): return json.loads(subprocess.run([sys.executable,'-m','dh','comparar','--grupo',g,'--json','--visao','misto'],cwd=R,capture_output=True,text=True,check=True).stdout)
rb=cmp('RPGBot'); ch=dados('misto')
EIX=['dano','deff','defm','controle','area','suporte','corpo']
classes=sorted({f.split('rpgbot-')[1].split('.json')[0] for f in glob.glob(R+'/calibracao/rpgbot-*.json')})
gab={c:json.load(open(f'{R}/calibracao/rpgbot-{c}.json'))['subclasses'] for c in classes if c not in HOLDOUT}
rot=rotulos(True); chid={(r['classe'],r['subclasse']):b for b,r in rot.items() if r['variante']=='sem-feat'}
NOTA={'azul':4,'verde':3,'laranja':2,'vermelho':1}
out=[]
ids=sorted({b for e in EIX for b in rb.get(e,{})})
for bid in ids:
    rest=bid[len('rpgbot-'):]; cl=rest.split('-')[0]
    if cl in HOLDOUT or cl not in gab: continue
    sub=rest[len(cl)+1:]; var='padrao'
    if sub.endswith('-puro'): sub=sub[:-5]; var='puro'
    g=gab[cl].get(sub,{})
    cor=g.get('nota')
    for nv in (3,5,7,9,11):
        row=dict(id=bid,classe=cl,sub=sub,var=var,nv=nv,cor=cor)
        for e in EIX: row[e]=rb.get(e,{}).get(bid,{}).get(str(nv))
        for ge,me in (('dano','dano'),('defesa','deff'),('controle','controle'),('area','area'),('suporte','suporte'),('corpo','corpo')):
            t=(g.get('eixos') or {}).get(ge); row['p_'+me]=pista(t,nv) if t else None
        cb=chid.get((cl,sub))
        for e in EIX: row['c_'+e]=val(ch,e,cb,nv) if cb else None
        out.append(row)
print(len(out), len({r['id'] for r in out}), 'cores', sum(1 for r in out if r['cor'])/5)
print(out[0])

# ---- rótulos curtos, deltas e arquivo final {rows, meta}
AB={'barbarian':'Bar','bard':'Brd','cleric':'Clr','druid':'Drd','fighter':'Ftr','monk':'Mnk','paladin':'Pal','ranger':'Rgr','warlock':'Wlk','wizard':'Wiz'}
CURTO={'ancestral-guardian':'Ancestral','battle-master':'BattleMstr','purple-dragon-knight':'PurpleDrg','eldritch-knight':'EldKnight','arcane-archer':'ArcArcher',
 'order-of-scribes':'Scribes','great-old-one':'GOO','drunken-master':'Drunken','four-elements':'4Elem','ascendant-dragon':'AscDragon','astral-self':'Astral',
 'long-death':'LongDeath','open-hand':'OpenHand','sun-soul':'SunSoul','horizon-walker':'Horizon','gloom-stalker':'Gloom','monster-slayer':'MonSlayer',
 'beast-master':'BeastMstr','fey-wanderer':'FeyWand','totem-warrior':'Totem','storm-herald':'StormHer','wild-magic':'WildMag','psi-warrior':'PsiWar',
 'rune-knight':'RuneKn','echo-knight':'Echo','war-magic':'WarMagic'}
def curto(s): return CURTO.get(s, s.split('-')[0].capitalize()[:10])
prev={}
for r in sorted(out,key=lambda r:(r['id'],r['nv'])):
    r['rotulo']=f"{AB.get(r['classe'],r['classe'][:3])}·{curto(r['sub'])}"+('·p' if r['var']=='puro' else '')
    p=prev.get(r['id'])
    for e in EIX:
        r['d_'+e]=round(r[e]-p[e],2) if p and r[e] is not None and p[e] is not None else None
        r['r_'+e]=round(r[e]-r['c_'+e],2) if r[e] is not None and r['c_'+e] is not None else None
    prev[r['id']]=r
code=open(__file__).read()
json.dump({'rows':out,'meta':[{'label':'extrai_dash.py','value':code,'type':'code','lang':'python'},
  {'label':'Entrada','value':'dh comparar --grupo RPGBot/Chassi --visao misto (resultados do CI de 27/11), calibracao/rpgbot-<classe>.json'},
  {'label':'Fora','value':'Artificer, Rogue e Sorcerer (holdout do sprint)'}]},
  open(SAIDA,'w'),ensure_ascii=False)
print('ok', len(out), os.path.getsize(SAIDA))
