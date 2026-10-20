import json,random
b=json.load(open('assessment/bank_v2.json'))
items=b['items']
pts={i['id']:[p for _,p in i['o']] for i in items if i.get('type')!='num'}
nums={i['id']:[i['answer'],i['tol']] for i in items if i.get('type')=='num'}
cats={}
for i in items: cats.setdefault(i['cat'],[]).append(i['id'])
J=lambda o:json.dumps(o).replace("'","''")
samples=[('nour',.82,78,1,3,2),('youssef',.9,85,2,2,1),('laila',.6,72,0,2,3),('omar',.62,55,1,1,1),('mariam',.78,80,0,3,2),('karim',.55,60,1,2,0),('salma',.7,88,2,0,2),('hana',.4,50,0,1,1)]
def score(ans,ws,i_,p_,a_,ver=True):
    res={}
    for c,ids in cats.items():
        s=0
        for q in ids:
            a=ans.get(q)
            if q in nums:
                try: s+=3 if abs(float(a)-nums[q][0])<=nums[q][1] else 0
                except: pass
            elif isinstance(a,int) and 0<=a<=3: s+=pts[q][a]
        res[c]=round(s/(3*len(ids))*100)
    if ws is not None: res['comm']=round((res['comm']+ws)/2)
    e=min(100,min(3,i_)*35+p_*15+a_*10); res['exp']=e if ver else min(e,50)
    return res,round(.2*res['comm']+.2*res['prob']+.2*res['prof']+.15*res['digi']+.25*res['exp'])
rows=[];report=[]
for name,qual,ws,i_,p_,a_ in samples:
    rnd=random.Random(name)
    ans={}
    for it in items:
        if it.get('type')=='num':
            ans[it['id']]=str(it['answer']) if rnd.random()<qual else str(it['answer']+rnd.choice([-15,10,25]))
        else:
            order=sorted(range(4),key=lambda k:-it['o'][k][1])
            r=rnd.random()
            ans[it['id']]=order[0] if r<qual else order[1] if r<qual+(1-qual)*.6 else order[2]
    sc,t=score(ans,ws,i_,p_,a_)
    report.append((name,t,sc))
    rows.append(f"('{name}.sample@example.com','{J(ans)}'::jsonb,{ws})")
sql=open('supabase/05_assessment_v2.template.sql').read()
sql=sql.replace('__PTS__',J(pts)).replace('__NUMS__',J(nums)).replace('__CATS__',J(cats)).replace('__SAMPLES__',',\n  '.join(rows))
open('supabase/05_assessment_v2.sql','w').write(sql)
for r in report: print(r)
