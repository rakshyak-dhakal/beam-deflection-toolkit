
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

def create_plot(case,load,load_unit):
    data=pd.read_csv("outputs/"+case+".csv")
    data=data[data["load"]==load]

    plt.figure(figsize=(9,6))

    for span in sorted(data["span_m"].unique()):
        beam_data=data[data["span_m"]==span]

        x=beam_data["position_m"].to_numpy()
        y=beam_data["deflection_m"].to_numpy()

        plt.plot(x,y,label=f"Span = {span} m")

        max_index=np.argmax(y)
        plt.scatter(x[max_index],y[max_index],marker="o")

    plt.xlabel("Position along beam (m)")
    plt.ylabel("Deflection (m)")
    plt.title(f"{case} - Load = {load} {load_unit}")
    plt.legend()
    plt.grid(True)
    plt.gca().invert_yaxis()

    os.makedirs("outputs",exist_ok=True)
    plt.savefig("outputs/"+case+".png",dpi=300,bbox_inches="tight")
    plt.close()

