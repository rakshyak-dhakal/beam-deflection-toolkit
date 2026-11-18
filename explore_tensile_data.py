
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

data_folder=Path("tensile_dataset/data/raw")
output_folder=Path("tensile_dataset/exploratory_plots")
output_folder.mkdir(parents=True,exist_ok=True)

tests=["test_01","test_02"]

for test_id in tests:
    file=data_folder/f"{test_id}.csv"
    df=pd.read_csv(file)

    displacement_col=[c for c in df.columns if c.startswith("displacement")][0]

    if displacement_col=="displacement_m":
        df["displacement_mm"]=df[displacement_col]*1000
    else:
        df["displacement_mm"]=df[displacement_col]

    df=df.dropna(subset=["displacement_mm","force_N"])

    plt.figure(figsize=(9,5))
    plt.plot(df["displacement_mm"],df["force_N"],linewidth=1)

    plt.xlabel("Displacement (mm)")
    plt.ylabel("Force (N)")
    plt.title(f"Force vs Displacement - {test_id}")
    plt.grid(True)
    plt.tight_layout()

    output_file=output_folder/f"{test_id}_force_displacement.png"
    plt.savefig(output_file,dpi=300)
    plt.show()

    print(f"Saved: {output_file}")
