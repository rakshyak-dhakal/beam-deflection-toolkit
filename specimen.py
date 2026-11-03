
from dataclasses import dataclass
from pathlib import Path
import numpy as np
import pandas as pd


@dataclass
class Specimen:
    test_id: str
    material: str
    area: float
    gauge_length: float


class TensileTest:

    def __init__(self,specimen,data_folder="tensile_dataset/data/raw"):
        self.specimen=specimen
        self.file_path=Path(data_folder)/f"{specimen.test_id}.csv"

        self.data=None

        self.complete=False
        self.completion_reason="Not evaluated"

        self.corrected_spike_indices=[]
        self.slack_removed_count=0
        self.slack_threshold_N=np.nan

        self.elastic_fit_r2=np.nan
        self.yield_strain=np.nan
        self.peak_index=None
        self.fracture_index=None

    def load_data(self):

        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {self.file_path}")

        self.data=pd.read_csv(self.file_path)

        return self.data

    def clean_data(self):

        if self.data is None:
            self.load_data()

        displacement_columns=[
            col for col in self.data.columns
            if col.startswith("displacement")
        ]

        if len(displacement_columns)!=1:
            raise ValueError("Invalid displacement column")

        displacement_col=displacement_columns[0]

        if displacement_col not in ["displacement_m","displacement_mm"]:
            raise ValueError("Unsupported displacement unit")

        required_columns=[displacement_col,"force_N"]

        for col in required_columns:
            self.data[col]=pd.to_numeric(
                self.data[col],
                errors="coerce"
            )

        self.data=self.data.replace(
            [np.inf,-np.inf],
            np.nan
        )

        self.data=self.data.dropna(
            subset=required_columns
        )

        self.data=self.data.drop_duplicates().reset_index(drop=True)

        if len(self.data)<20:
            raise ValueError("Insufficient valid measurements")

        displacement=self.data[displacement_col].to_numpy(dtype=float)
        force=self.data["force_N"].to_numpy(dtype=float)

        if displacement_col=="displacement_m":
            displacement=displacement*1000

        self.data["displacement_mm"]=displacement
        self.data["force_N"]=force

        self.remove_initial_slack()

        self.remove_force_spikes()

        return self.data

    def remove_initial_slack(self):

        force=self.data["force_N"].to_numpy(dtype=float)
        displacement=self.data["displacement_mm"].to_numpy(dtype=float)

        maximum_force=np.max(np.abs(force))

        if maximum_force<=0:
            raise ValueError("No valid tensile force measurements")

        self.slack_threshold_N=max(
            10.0,
            0.001*maximum_force
        )

        start_index=0

        while (
            start_index<len(force)-20 and
            abs(force[start_index])<=self.slack_threshold_N
        ):
            start_index+=1

        self.slack_removed_count=start_index

        if start_index>0:
            self.data=self.data.iloc[start_index:].copy()
            self.data=self.data.reset_index(drop=True)

        displacement=self.data["displacement_mm"].to_numpy(dtype=float)

        displacement=displacement-displacement[0]

        self.data["displacement_mm"]=displacement

        return self.data

    def remove_force_spikes(self,threshold=0.15):

        force=self.data["force_N"].to_numpy(dtype=float).copy()

        displacement=self.data["displacement_mm"].to_numpy(dtype=float).copy()

        original_force=force.copy()
        n=len(force)

        self.corrected_spike_indices=[]

        if n<9:
            return self.data

        local_median=pd.Series(force).rolling(
            window=9,
            center=True,
            min_periods=5
        ).median().to_numpy()

        suspected=[]

        for i in range(4,n-4):

            median=local_median[i]

            if not np.isfinite(median) or abs(median)<1:
                continue

            deviation=abs(force[i]-median)/abs(median)

            if deviation<=threshold:
                continue

            previous=force[i-1]
            following=force[i+1]

            neighbour_difference=abs(previous-following)/abs(median)

            if neighbour_difference>0.05:
                continue

            steps=np.diff(
                displacement[max(0,i-5):min(n,i+6)]
            )

            typical_step=np.median(np.abs(steps))

            if typical_step<=0:
                continue

            step_before=abs(displacement[i]-displacement[i-1])
            step_after=abs(displacement[i+1]-displacement[i])

            if not (
                0.5*typical_step<=step_before<=2*typical_step and
                0.5*typical_step<=step_after<=2*typical_step
            ):
                continue

            suspected.append(i)

        if suspected:

            valid_indices=np.ones(n,dtype=bool)
            valid_indices[suspected]=False

            force[suspected]=np.interp(
                np.array(suspected),
                np.arange(n)[valid_indices],
                original_force[valid_indices]
            )

        self.data["force_N"]=force
        self.corrected_spike_indices=suspected

        return self.data

    def calculate_stress_strain(self):

        if self.data is None or "displacement_mm" not in self.data.columns:
            self.clean_data()

        force=self.data["force_N"].to_numpy(dtype=float)
        displacement=self.data["displacement_mm"].to_numpy(dtype=float)

        stress=force/self.specimen.area

        strain=displacement/self.specimen.gauge_length

        self.data["stress_MPa"]=stress
        self.data["strain"]=strain

        return self.data

    def calculate_youngs_modulus(self,strain_min=0.0005,strain_max=0.0015):

        if self.data is None or "strain" not in self.data.columns:
            self.calculate_stress_strain()

        elastic_data=self.data[
            (self.data["strain"]>=strain_min)&
            (self.data["strain"]<=strain_max)
        ]

        strain=elastic_data["strain"].to_numpy(dtype=float)
        stress=elastic_data["stress_MPa"].to_numpy(dtype=float)

        if len(strain)<10:
            raise ValueError("Insufficient data in elastic fitting region")

        slope,intercept=np.polyfit(strain,stress,1)

        predicted_stress=slope*strain+intercept

        ss_res=np.sum((stress-predicted_stress)**2)
        ss_tot=np.sum((stress-np.mean(stress))**2)

        if ss_tot==0:
            raise ValueError("Cannot calculate elastic fit R2")

        self.elastic_fit_r2=1-ss_res/ss_tot

        if slope<=0:
            raise ValueError("Invalid Young's modulus")

        return slope/1000

    def calculate_yield_strength(self):

        if self.data is None or "strain" not in self.data.columns:
            self.calculate_stress_strain()

        E=self.calculate_youngs_modulus()*1000

        strain=self.data["strain"].to_numpy(dtype=float)
        stress=self.data["stress_MPa"].to_numpy(dtype=float)

        offset_stress=E*(strain-0.002)

        difference=stress-offset_stress

        crossings=np.where(
            (strain[:-1]>=0.002)&
            (difference[:-1]>=0)&
            (difference[1:]<=0)
        )[0]

        if len(crossings)==0:
            raise ValueError("0.2% offset yield point not found")

        i=crossings[0]

        denominator=difference[i+1]-difference[i]

        if denominator==0:
            raise ValueError("Cannot interpolate yield point")

        fraction=-difference[i]/denominator

        yield_strain=strain[i]+fraction*(strain[i+1]-strain[i])

        yield_strength=stress[i]+fraction*(stress[i+1]-stress[i])

        self.yield_strain=yield_strain

        return yield_strength

    def detect_completeness(self):

        if self.data is None or "stress_MPa" not in self.data.columns:
            self.calculate_stress_strain()

        stress=self.data["stress_MPa"].to_numpy(dtype=float)

        n=len(stress)

        self.peak_index=int(np.argmax(stress))

        maximum_stress=stress[self.peak_index]

        if maximum_stress<=0:
            self.complete=False
            self.completion_reason="No positive tensile stress"
            return False

        post_peak_count=n-self.peak_index-1

        if self.peak_index>=int(0.95*n):
            self.complete=False
            self.completion_reason="Peak occurs near the end of the test"
            return False

        if post_peak_count<10:
            self.complete=False
            self.completion_reason="Insufficient post-peak measurements"
            return False

        final_drop=(maximum_stress-stress[-1])/maximum_stress

        if final_drop<0.10:
            self.complete=False
            self.completion_reason="Insufficient post-peak stress reduction"
            return False

        self.complete=True
        self.completion_reason="Post-peak stress reduction detected"

        return True

    def calculate_ultimate_tensile_strength(self):

        if self.data is None or "stress_MPa" not in self.data.columns:
            self.calculate_stress_strain()

        if not self.detect_completeness():
            return np.nan

        return float(self.data["stress_MPa"].max())

    def calculate_elongation_at_fracture(self):

        if self.data is None or "strain" not in self.data.columns:
            self.calculate_stress_strain()

        if not self.detect_completeness():
            return np.nan

        return float(self.data["strain"].iloc[-1])

    def calculate_fracture_strain(self):

        return self.calculate_elongation_at_fracture()


if __name__=="__main__":

    specimens=pd.read_csv("tensile_dataset/data/specimens.csv")

    for _,row in specimens.iterrows():

        test_id=row["test_id"]

        try:

            specimen=Specimen(
                test_id=row["test_id"],
                material=row["material"],
                area=row["area_mm2"],
                gauge_length=row["gauge_length_mm"]
            )

            test=TensileTest(specimen)

            test.load_data()
            test.clean_data()

            data=test.calculate_stress_strain()

            E=test.calculate_youngs_modulus()

            yield_strength=test.calculate_yield_strength()

            uts=test.calculate_ultimate_tensile_strength()

            fracture_strain=test.calculate_elongation_at_fracture()

            print(f"\n{test_id}")
            print(f"Material: {specimen.material}")
            print(f"Measurements: {len(data)}")
            print(f"Initial readings removed: {test.slack_removed_count}")
            print(f"Slack threshold: {test.slack_threshold_N:.2f} N")
            print(f"Corrected force spikes: {len(test.corrected_spike_indices)}")
            print(f"Corrected indices: {test.corrected_spike_indices}")
            print(f"Young's Modulus: {E:.2f} GPa")
            print(f"Elastic fit R2: {test.elastic_fit_r2:.5f}")
            print(f"Yield Strength: {yield_strength:.2f} MPa")
            print(f"Complete: {test.complete}")
            print(f"Completeness reason: {test.completion_reason}")

            if test.complete:
                print(f"UTS: {uts:.2f} MPa")
                print(f"Fracture strain: {fracture_strain:.5f}")
            else:
                print("UTS: Not reported")
                print("Fracture strain: Not reported")

        except (ValueError,FileNotFoundError,IndexError) as error:

            print(f"{test_id}: Analysis failed - {error}")
