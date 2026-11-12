import json, re, glob, os, collections
FILES = {  # label -> json
 'V2021':'20211115_CurriculumFramework_BSCS_V2021_ForIntake2Onward','V2023-i4':'20230113_CurriculumFrameowork_BSCS_V2023_ForIntake4',
 '23-27':'vF_250820_BSCS_23_27_CurriculumFrameowork','AY24-25c5':'20240905_CurriculumFrameowork_BSCS_Cohort-5_AY24-25_vF','24-28':'vF_250816_BSCS_24-28_Curriculum-Framework'}
ALIAS = {'statistics and probability':'probability and statistics','statistics':'probability and statistics'}
def norm(s):
    s=s.lower().replace('&',' and ').replace('�',"'"); s=re.sub(r'\(.*?\)','',s); s=re.sub(r'\s*-\s*','-',s)
    return re.sub(r'[^a-z0-9\-]+',' ',s).strip()
def resolve(rec, names):
    raw=rec['prereq_raw'] or ''; t=norm(raw)
    if re.match(r'^(none|n a|na)\b',t): return [], 'none', ''
    keys=sorted(list(names)+list(ALIAS), key=len, reverse=True); found=[]; rest=t
    while rest:
        rest=rest.lstrip(' ,;')
        rest=re.sub(r'^(and|or)\s+','',rest)
        for k in keys:
            if rest.startswith(k) and (len(rest)==len(k) or rest[len(k)]==' '):
                found.append(ALIAS.get(k,k)); rest=rest[len(k):]; break
        else: break
    # leftover that continues into description prose is expected; flag if leftover begins with a short token run before 'this'/'the'
    flag = '' if (not found and t=='') else ''
    first=rest.split(' ')[0] if rest else ''
    if not found: flag='UNRESOLVED'
    return found, ('ok' if found else 'review'), (rest[:60] if not found or first in ('and','or','in','of','students') else '')
data={}
for lab,f in FILES.items():
    recs=json.load(open(f'json/{f}.json',encoding='utf-8'))
    names={norm(re.sub(r'\(.*?\)','',r['name'])):r for r in recs}
    g={}
    for r in recs:
        pre,st,note=resolve(r,names)
        g[norm(re.sub(r'\(.*?\)','',r['name']))]={'code':r['code'],'name':r['name'],'cr':r['credits'],'pre':pre,'st':st,'note':note,'raw':(r['prereq_raw'] or '')[:90]}
    data[lab]=g
out=[]
P=out.append
P('# BSCS – đồ thị môn học & tiên quyết (phân tích tự động, CẦN người duyệt)\n')
P('Nguồn: `sources/text/curriculum-frameworks/bscs/` (S001 và các bản cũ). Parser: `parse_catalog.py` + `analyze_bscs.py` (heuristic). Chỉ phần *mô tả môn* được dùng; bảng khung chương trình chưa parse.\n')
# stats
P('## 1. Số liệu mỗi phiên bản\n'); P('| Phiên bản | Số môn parse | Có tiên quyết resolve được | Không có (None/N/A) | Cần review |'); P('|---|---|---|---|---|')
for lab,g in data.items():
    n=len(g); ok=sum(1 for v in g.values() if v['st']=='ok'); no=sum(1 for v in g.values() if v['st']=='none'); rv=sum(1 for v in g.values() if v['st']=='review')
    P(f'| {lab} | {n} | {ok} | {no} | {rv} |')
cur=data['24-28']
# graph for 24-28
P('\n## 2. Đồ thị tiên quyết BSCS 2024-28 (môn có tiên quyết)\n'); P('| Môn (mã trong mô tả) | TC | Tiên quyết (resolve) | Ghi chú |'); P('|---|---|---|---|')
for k,v in cur.items():
    if v['pre'] or v['st']=='review':
        names=', '.join(cur[p]['name'].split(' (')[0] if p in cur else f'⚠{p}' for p in v['pre'])
        P(f"| {v['code']} {v['name'][:38]} | {v['cr']:g} | {names or '—'} | {'⚠ REVIEW: '+v['raw'][:70] if v['st']=='review' else ''} |")
# DAG depth
depth={}
def d(k,seen=()):
    if k in depth: return depth[k]
    if k in seen: return 0
    ps=[p for p in cur[k]['pre'] if p in cur]
    depth[k]=1+max([d(p,seen+(k,)) for p in ps],default=-1); return depth[k]
for k in cur: d(k)
mx=max(depth.values()); chains=[k for k in cur if depth[k]==mx]
P(f'\n**Chuỗi tiên quyết dài nhất:** {mx+1} môn liên tiếp. Môn cuối chuỗi: '+', '.join(cur[k]['name'].split(' (')[0] for k in chains)+'.')
outdeg=collections.Counter(p for v in cur.values() for p in v['pre'])
P('\n**Môn là tiên quyết của nhiều môn nhất (điểm nghẽn):** '+', '.join(f"{cur[k]['name'].split(' (')[0]} ({n})" for k,n in outdeg.most_common(6) if k in cur))
P('\n**Tiên quyết trỏ tới môn không có trong mô tả (⚠):** '+(', '.join(sorted({p for v in cur.values() for p in v['pre'] if p not in cur})) or 'không'))
# diffs
P('\n## 3. Khác biệt giữa các phiên bản (theo tên môn)\n')
order=list(FILES)
for a,b in zip(order,order[1:]):
    A,B=data[a],data[b]
    add=[B[k]['name'].split(' (')[0] for k in B if k not in A]; rem=[A[k]['name'].split(' (')[0] for k in A if k not in B]
    cr=[f"{B[k]['name'].split(' (')[0]}: {A[k]['cr']:g}→{B[k]['cr']:g}" for k in B if k in A and A[k]['cr']!=B[k]['cr']]
    pr=[f"{B[k]['name'].split(' (')[0]}: [{', '.join(A[k]['pre']) or '∅'}]→[{', '.join(B[k]['pre']) or '∅'}]" for k in B if k in A and A[k]['pre']!=B[k]['pre'] and A[k]['st']!='review' and B[k]['st']!='review']
    P(f'### {a} → {b}'); P(f'- Thêm ({len(add)}): '+('; '.join(add) or '—')); P(f'- Bỏ ({len(rem)}): '+('; '.join(rem) or '—')); P(f'- Đổi tín chỉ ({len(cr)}): '+('; '.join(cr) or '—')); P(f'- Đổi tiên quyết ({len(pr)}): '+('; '.join(pr) or '—')+'\n')
open('bscs-prereq-graph.md','w',encoding='utf-8').write('\n'.join(out))
json.dump(data,open('json/_resolved_bscs.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
print('\n'.join(out))
