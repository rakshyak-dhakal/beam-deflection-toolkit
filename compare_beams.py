
import json
import numpy as np
import beams
import beams_loop

with open("config.json","r") as f:
    config=json.load(f)

functions={
    "ss_center":(beams.ss_center,beams_loop.ss_center),
    "ss_point":(beams.ss_point,beams_loop.ss_point),
    "ss_udl":(beams.ss_udl,beams_loop.ss_udl),
    "cantilever_point":(beams.cantilever_point,beams_loop.cantilever_point),
    "cantilever_udl":(beams.cantilever_udl,beams_loop.cantilever_udl)
}

for case,(new_func,old_func) in functions.items():
    for L in config["spans"]:
        loads=config["point_loads"] if case in ["ss_center","ss_point","cantilever_point"] else config["uniform_loads"]

        for load in loads:
            beam={"L":L,"E":config["E"],"I":config["I"]}

            if case in ["ss_center","cantilever_point"]:
                beam["P"]=load
            elif case=="ss_point":
                beam["P"]=load
                beam["a"]=config["off_center_fraction"]*L
            else:
                beam["w"]=load

            x=np.linspace(0,L,101)
            new_result=new_func(x,beam)
            old_result=np.array([old_func(float(pos),beam) for pos in x])

            assert np.allclose(new_result,old_result),f"Mismatch: {case}, L={L}, load={load}"

print("PASS: All 45 cases match the original loop calculations.")
