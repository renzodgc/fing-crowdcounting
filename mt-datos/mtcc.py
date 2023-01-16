
import glob
import re
import json

import statistics


table = dict()
errores = dict()


for fn in glob.glob('./*/*.json'):
    print(fn)
    r = re.search(r"(\d+)/(.*).json", fn)
    u,d = r.groups()
    
    f = open(fn)
    data = json.load(f)
    table[d] = table.get(d, dict())
    if data['human_num'] != len(data['points']):
        print("Error: ", f)
        exit(1)
    table[d][u] = data['human_num'] 
    #table[d][u] = len(data['points'])

                
    

print('\t'.join(['    ']+list(map(str,range(1,13)))))


for i in sorted(table.keys()):
    print(i, end='\t') 
    vls = [] 
    for j in sorted(table[i].keys(), key=int):
        vls.append(table[i][j])
        
    mn = sum(vls)/len(vls)
    dv = statistics.pstdev(vls)
        
    for c, v in enumerate(vls, start=1): 
        if abs(v-mn) > dv:
            errores[c] = errores.get(c,0)+1
            print(v, end='*\t') 
        else:    
            print(v, end='\t') 
        
    print(str(int(mn))+'('+str(int(dv))+')') 
    
print(sorted(errores.items(), key=lambda x: x[0]))
    
        
        
        
