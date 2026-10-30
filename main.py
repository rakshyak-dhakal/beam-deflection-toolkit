
import json
import csv
import os
import numpy as np
import pandas as pd
import beams
import beam_plotting as plotting

try:
    with open("config.json","r") as f:
        data=json.load(f)

    E=data["E"]
    I=data["I"]
    spans=data["spans"]
    point_loads=data["point_loads"]
    uniform_loads=data["uniform_loads"]
    fraction=data["off_center_fraction"]
    cases=data["beam_cases"]

    if E<=0 or I<=0:
        raise ValueError("E and I must be positive")

    if any(L<=0 for L in spans):
        raise ValueError("Spans must be positive")

    if any(P<=0 for P in point_loads+uniform_loads):
        raise ValueError("Loads must be positive or non zero")

    if fraction<=0 or fraction>=1:
        raise ValueError("Off-center fraction must be between 0 and 1")

    functions={
        "ss_center":beams.ss_center,
        "ss_point":beams.ss_point,
        "ss_udl":beams.ss_udl,
        "cantilever_point":beams.cantilever_point,
        "cantilever_udl":beams.cantilever_udl
    }

    for case in cases:
        if case not in functions:
            raise ValueError("Unknown beam case: "+case)

    

    results=[]
    os.makedirs("outputs",exist_ok=True)

    for case in cases:
        case_frames=[]

        if case in ["ss_center","ss_point","cantilever_point"]:
            loads=point_loads
        else:
            loads=uniform_loads

        for L in spans:
            for load in loads:
                beam={"L":L,"E":E,"I":I}

                if case in ["ss_center","cantilever_point"]:
                    beam["P"]=load
                elif case=="ss_point":
                    beam["P"]=load
                    beam["a"]=fraction*L
                else:
                    beam["w"]=load

                x_values=np.linspace(0,L,101)
                deflections=functions[case](x_values,beam)

                frame=pd.DataFrame({
                    "beam_type":case,
                    "span_m":L,
                    "load":load,
                    "position_m":x_values,
                    "deflection_m":deflections
                })

                case_frames.append(frame)

                max_deflection=np.max(deflections)
                results.append([case,L,load,max_deflection])

        case_data=pd.concat(case_frames,ignore_index=True)
        case_data.to_csv("outputs/"+case+".csv",index=False)
        load_unit="N" if case in ["ss_center","ss_point","cantilever_point"] else "N/m"
        plotting.create_plot(case,loads[len(loads)//2],load_unit)

    with open("results.csv","w",newline="") as f:
        writer=csv.writer(f)
        writer.writerow(["beam_type","span_m","load_N_or_N_per_m","max_deflection_m"])
        writer.writerows(results)

    with open("results.csv","w",newline="") as f:
        writer=csv.writer(f)
        writer.writerow(["beam_type","span_m","load_N_or_N_per_m","max_deflection_m"])
        writer.writerows(results)

    with open("results.csv","r") as f:
        reader=csv.reader(f)
        next(reader)
        saved_results=list(reader)

    print("Total cases:",len(saved_results))
    print("Results saved to results.csv")

    for case in cases:
        case_results=[r for r in saved_results if r[0]==case]
        largest=max(case_results,key=lambda r:float(r[3]))
        print(case,": span =",largest[1],"m, load =",largest[2],
              ", maximum deflection =",format(float(largest[3]),".6e"),"m")
    
    
    print("\nSELF-CHECKS")
    print(f"{'Beam case':<22}{'Span':>6}{'Load':>8}{'Numerical':>16}{'Analytical':>16}{'Result':>10}")

    checks=[
        ("ss_center",point_loads),
        ("ss_udl",uniform_loads),
        ("cantilever_point",point_loads),
        ("cantilever_udl",uniform_loads)
    ]

    for case,loads_to_use in checks:
        for L in spans:
            for load in loads_to_use:
                row=next(r for r in results
                         if r[0]==case and r[1]==L and r[2]==load)

                numerical=row[3]

                if case=="ss_center":
                    analytical=load*L**3/(48*E*I)
                elif case=="ss_udl":
                    analytical=5*load*L**4/(384*E*I)
                elif case=="cantilever_point":
                    analytical=load*L**3/(3*E*I)
                else:
                    analytical=load*L**4/(8*E*I)

                error=abs(numerical-analytical)/abs(analytical)
                status="PASS" if error<=1e-9 else "FAIL"

                print(f"{case:<22}{L:>6}{load:>8}{numerical:>16.6e}{analytical:>16.6e}{status:>10}")

    print("\nPIECEWISE FUNCTION CHECKS")
    print(f"{'Beam case':<22}{'Continuity':>14}{'Supports':>12}")

    for case in ["ss_center","ss_point"]:
        L=2
        beam={"L":L,"E":E,"I":I,"P":200}

        if case=="ss_point":
            beam["a"]=fraction*L
            break_point=beam["a"]
        else:
            break_point=L/2

        func=functions[case]

        left=func(break_point-1e-8,beam)
        right=func(break_point+1e-8,beam)
        start=func(0,beam)
        end=func(L,beam)

        continuous=abs(left-right)<1e-10
        supports=abs(start)<1e-12 and abs(end)<1e-12

        continuity_status="PASS" if continuous else "FAIL"
        support_status="PASS" if supports else "FAIL"

        print(f"{case:<22}{continuity_status:>14}{support_status:>12}")

    print("\nLIST COMPREHENSION CHECK")

    loop_squares=[]
    for i in range(1,11):
        loop_squares.append(i**2)

    comprehension_squares=[i**2 for i in range(1,11)]

    print("Loop result:         ",loop_squares)
    print("Comprehension result:",comprehension_squares)
    print("Same result:",loop_squares==comprehension_squares)





    
except FileNotFoundError:
    print("Error: config.json was not found.")

except (ValueError, KeyError, TypeError) as e:
    print("Error:",e)

except OSError:
    print("Error: Could not read or write a file.")

 