# -*- coding: utf-8 -*-
"""
Created on Tue Oct 27 21:45:37 2026

@author: ASUS
"""



beam={"material":"Steel","E":200e9,"I":8e-6}

loads=[100,200,300,400,500]
spans=[1,2,3,4,5]

def deflection(x,L,P,beam):
    E=beam["E"]
    I=beam["I"]
    v=-P*x**2*(3*L-x)/(6*E*I)
    return v

results=[]

for P in loads:
    for L in spans:
        x=L
        v=deflection(x,L,P,beam)*1000
        results.append([P,L,x,v])
        print("Load:",P,"N, Span:",L,"m, Deflection:",format(v,".4f"),"mm")

with open("beam results.csv","w") as f:
    f.write("Load_N,Span_m,Position_m,Deflection_mm\n")
    for r in results:
        f.write(f"{r[0]},{r[1]},{r[2]},{r[3]:.4f}\n")

print("Total cases:",len(results))
