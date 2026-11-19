import json,math
R='/home/claude/dh-metricas/'
def prof(L): return 2+(L-1)//4
def built(slug,L): return json.load(open(f'{R}builds/rpgbot-fighter-{slug}-{L}.json'))
def bon(b):
    p=[l for l in b['linhas'] if l.get('principal') or l['id']=='principal'][0]
    out=[]
    for a in p['dano']['ataques']:
        if 'nota' in a and ('oportunidade' in a['nota'] or 'Unleash' in a['nota'] or 'Mark' in a['nota']): continue
        out+= [a['bonus']]*int(math.floor(a['n']))
    return out or [p['dano']['ataques'][0]['bonus']]
def aplicar(slug, fontes_por_nivel, linhas_extra=None):
    f=f'{R}progressoes/rpgbot-fighter-{slug}.json'; P=json.load(open(f))
    for L in (3,5,7,9,11):
        b=built(slug,L); fx=fontes_por_nivel(L,b)
        if fx is None: continue
        alvo=P['base'] if L==3 else P['niveis'][str(L)]
        ls=alvo.setdefault('linhas',[])
        for l in b['linhas']:
            ctl=json.loads(json.dumps(l.get('controle') or {}))
            if not ctl: continue
            if l['id']!='principal' and not any(x['id']==l['id'] and 'controle' in x for x in ls): continue
            ctl['fontes']=[x for x in ctl.get('fontes',[]) if x.get('_p2')!=True]+[dict(x,_p2=True) for x in fx]
            pt=next((x for x in ls if x['id']==l['id']),None)
            if pt is None: pt={'id':l['id']}; ls.append(pt)
            pt['controle']=ctl
    json.dump(P,open(f,'w'),ensure_ascii=False,indent=1)

# Battle Master: Menacing Attack com os dados de superioridade (mesmos usos já somados no dano)
dex={3:3,5:3,7:3,9:4,11:4}; us={3:2,5:2,7:2.5,9:2.5,11:2.5}
aplicar('battle-master',lambda L,b:[{"tipo":"condicao_no_acerto","nome":"Menacing Attack (dado de superioridade)","efeito":"cond_amedrontado_um_turno","cd":8+prof(L)+dex[L],"bonus":bon(b),"usos":us[L]}])
# Cavalier: Unwavering Mark = marca no acerto (desvantagem contra outros), mesmo motor do Ancestral Protectors
aplicar('cavalier',lambda L,b:[{"tipo":"ancestral_protectors","nome":"Unwavering Mark (marca no acerto)","bonus":bon(b)[0]}])
# Arcane Archer: Shadow Arrow 1/luta
intm={3:3,5:3,7:3,9:3,11:3}
aplicar('arcane-archer',lambda L,b:[{"tipo":"condicao_no_acerto","nome":"Shadow Arrow (Arcane Shot)","efeito":"cond_cego_um_turno","cd":8+prof(L)+intm[L],"bonus":bon(b),"usos":1}])
# Rune Knight: Fire Rune (no acerto) e Stone Rune (reação), 1/descanso curto cada = 0,5 por luta
aplicar('rune-knight',lambda L,b:[{"tipo":"condicao_no_acerto","nome":"Fire Rune","efeito":"cond_impedido","cd":8+prof(L)+3,"bonus":bon(b),"usos":0.5},
                                  {"tipo":"condicao_no_acerto","nome":"Stone Rune (reação)","efeito":"cond_incapacitado","cd":8+prof(L)+3,"no_acerto":False,"usos":0.5}])
# Psi Warrior: Telekinetic Thrust no Psionic Strike (a partir do 7), mesmos dados do dano
ps={7:2,9:2.5,11:2.5}
aplicar('psi-warrior',lambda L,b:[{"tipo":"condicao_no_acerto","nome":"Telekinetic Thrust (Psionic Strike)","efeito":"cond_derrubado","cd":8+prof(L)+3,"bonus":bon(b),"usos":ps[L]}] if L>=7 else None)
# PDK: Form of Dread (no acerto, 1×/turno) a partir do 5
cha={5:3,7:3,9:4,11:5}
aplicar('purple-dragon-knight',lambda L,b:[{"tipo":"condicao_no_acerto","nome":"Form of Dread","efeito":"cond_amedrontado_um_turno","cd":8+prof(L)+cha[L],"bonus":bon(b),"usos":4*min(1,prof(L)/4)}] if L>=5 else None)
