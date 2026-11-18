
import numpy as np
import pandas as pd
from beams import ss_center

# Fixed random seed
rng=np.random.default_rng(42)

# Number of beams and points
n_beams=500
n_points=21

# Store generated data
data=[]

for beam_id in range(n_beams):

    # Generate random beam properties
    L=rng.uniform(1,3)
    P=rng.uniform(100,300)
    E=rng.uniform(190e9,210e9)
    I=rng.uniform(4e-6,12e-6)

    beam={"L":L,"E":E,"I":I,"P":P}

    # Generate 21 equally spaced positions
    x_values=np.linspace(0,L,n_points)

    for x in x_values:

        # Calculate deflection
        y=ss_center(x,beam)

        data.append([beam_id,x,L,E,I,P,y])

# Create DataFrame
df=pd.DataFrame(
    data,
    columns=["beam_id","x","L","E","I","P","y"]
)

# Save dataset
df.to_csv("beam_dataset.csv",index=False)

print("Dataset generated successfully!")
print("Total beams:",n_beams)
print("Points per beam:",n_points)
print("Total rows:",len(df))

print("\nProperty ranges:")
print(df[["L","P","E","I","y"]].agg(["min","max"]))

print("\nFirst five rows:")
print(df.head())
