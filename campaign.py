
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from specimen import Specimen, TensileTest


class TestCampaign:

    def __init__(self,metadata_file="tensile_dataset/data/specimens.csv",
                 data_folder="tensile_dataset/data/raw"):

        self.metadata_file=Path(metadata_file)
        self.data_folder=Path(data_folder)

        self.metadata=pd.read_csv(self.metadata_file)
        self.tests=[]
        self.results=[]

    def analyze_all(self):

        self.tests=[]
        self.results=[]

        for _,row in self.metadata.iterrows():

            test_id=row["test_id"]
            material=row["material"]

            result={
                "test_id":test_id,
                "material":material,
                "E_GPa":np.nan,
                "yield_MPa":np.nan,
                "uts_MPa":np.nan,
                "fracture_strain":np.nan,
                "complete":False
            }

            try:
                specimen=Specimen(
                    test_id=test_id,
                    material=material,
                    area=row["area_mm2"],
                    gauge_length=row["gauge_length_mm"]
                )

                test=TensileTest(specimen,data_folder=self.data_folder)

                test.load_data()
                test.clean_data()
                test.calculate_stress_strain()

                result["E_GPa"]=test.calculate_youngs_modulus()
                result["yield_MPa"]=test.calculate_yield_strength()
                result["uts_MPa"]=test.calculate_ultimate_tensile_strength()
                result["complete"]=bool(test.complete)

                if test.complete:
                    result["fracture_strain"]=test.calculate_elongation_at_fracture()

                self.tests.append(test)

            except Exception as error:
                print(f"Could not process {test_id}: {error}")

            self.results.append(result)

        return self.get_summary()

    def get_summary(self):

        columns=[
            "test_id",
            "material",
            "E_GPa",
            "yield_MPa",
            "uts_MPa",
            "fracture_strain",
            "complete"
        ]

        return pd.DataFrame(self.results,columns=columns)

    def save_summary(self,output_file="outputs/summary.csv"):

        summary=self.get_summary()

        output_path=Path(output_file)
        output_path.parent.mkdir(parents=True,exist_ok=True)

        summary.to_csv(output_path,index=False)

        print(f"Saved campaign summary: {output_path}")

        return summary

    def plot_stress_strain_by_material(self,output_folder="outputs"):

        output_path=Path(output_folder)
        output_path.mkdir(parents=True,exist_ok=True)

        materials=sorted(set(test.specimen.material for test in self.tests))

        for material in materials:

            plt.figure(figsize=(9,6))

            for test in self.tests:

                if test.specimen.material!=material:
                    continue

                data=test.data

                strain=data["strain"]
                stress=data["stress_MPa"]

                plt.plot(strain,stress,label=test.specimen.test_id)

                yield_strength=test.calculate_yield_strength()
                yield_strain=test.yield_strain

                if not np.isnan(yield_strength):
                    plt.scatter(
                        yield_strain,
                        yield_strength,
                        marker="o",
                        s=35
                    )

                if test.complete:
                    peak_index=stress.idxmax()

                    plt.scatter(
                        strain.loc[peak_index],
                        stress.loc[peak_index],
                        marker="^",
                        s=45
                    )

            plt.xlabel("Engineering Strain")
            plt.ylabel("Engineering Stress (MPa)")
            plt.title(f"Stress-Strain Curves - {material.capitalize()}")
            plt.legend(fontsize=8)
            plt.grid(True)
            plt.tight_layout()

            filename=output_path/f"{material}_stress_strain.png"

            plt.savefig(filename,dpi=300)
            plt.close()

            print(f"Saved: {filename}")

    def plot_yield_strength_boxplot(self,output_file="outputs/yield_strength_boxplot.png"):

        output_path=Path(output_file)
        output_path.parent.mkdir(parents=True,exist_ok=True)

        summary=self.get_summary()
        summary=summary.dropna(subset=["yield_MPa"])

        materials=sorted(summary["material"].unique())

        values=[
            summary.loc[
                summary["material"]==material,
                "yield_MPa"
            ].values
            for material in materials
        ]

        plt.figure(figsize=(8,6))

        plt.boxplot(values,tick_labels=materials)

        plt.xlabel("Material")
        plt.ylabel("Yield Strength (MPa)")
        plt.title("Yield Strength Distribution by Material")
        plt.grid(axis="y")
        plt.tight_layout()

        plt.savefig(output_path,dpi=300)
        plt.close()

        print(f"Saved: {output_path}")


if __name__=="__main__":

    campaign=TestCampaign()

    summary=campaign.analyze_all()

    campaign.save_summary()

    campaign.plot_stress_strain_by_material()
    campaign.plot_yield_strength_boxplot()

    print("\nTests processed:",len(summary))
    print("Complete tests:",summary["complete"].sum())
    print("Incomplete or failed tests:",(~summary["complete"]).sum())
