
import numpy as np
import pandas as pd
import json

# Load generated dataset
df=pd.read_csv("beam_dataset.csv")

# Get unique beam IDs
beam_ids=df["beam_id"].unique()

# Get unique beam IDs
beam_ids=df["beam_id"].unique()

# Shuffle beam IDs using a fixed seed
rng=np.random.default_rng(42)
rng.shuffle(beam_ids)

# Split into 70%, 15%, 15%
train_ids=beam_ids[:350]
val_ids=beam_ids[350:425]
test_ids=beam_ids[425:]

# Create datasets using beam IDs
train_df=df[df["beam_id"].isin(train_ids)].copy()
val_df=df[df["beam_id"].isin(val_ids)].copy()
test_df=df[df["beam_id"].isin(test_ids)].copy()

# Save raw datasets
train_df.to_csv("train_raw.csv",index=False)
val_df.to_csv("val_raw.csv",index=False)
test_df.to_csv("test_raw.csv",index=False)

# Input and output columns
input_cols=["x","L","E","I","P"]
target_col="y"

# Calculate statistics using training data only
X_mean=train_df[input_cols].mean()
X_std=train_df[input_cols].std()

y_mean=train_df[target_col].mean()
y_std=train_df[target_col].std()

# Normalize all datasets using training statistics
for name,data in [
    ("train",train_df),
    ("val",val_df),
    ("test",test_df)
]:
    data[input_cols]=(data[input_cols]-X_mean)/X_std
    data[target_col]=(data[target_col]-y_mean)/y_std

    data.to_csv(name+".csv",index=False)

# Save normalization statistics
stats={
    "X_mean":X_mean.to_dict(),
    "X_std":X_std.to_dict(),
    "y_mean":float(y_mean),
    "y_std":float(y_std)
}

with open("normalization_stats.json","w") as f:
    json.dump(stats,f,indent=4)

# Display results
print("Dataset split completed!")

print("\nDataset sizes:")
print("Training:",len(train_df),"rows,",len(train_ids),"beams")
print("Validation:",len(val_df),"rows,",len(val_ids),"beams")
print("Testing:",len(test_df),"rows,",len(test_ids),"beams")

print("\nTraining input means:")
print(X_mean)

print("\nTraining input standard deviations:")
print(X_std)

print("\nTarget mean:",y_mean)
print("Target standard deviation:",y_std)

print("\nFiles saved successfully!")
