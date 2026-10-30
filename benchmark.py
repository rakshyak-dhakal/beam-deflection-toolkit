
import numpy as np
import time
import beams
import beams_loop

beam={"L":2,"P":200,"E":200e9,"I":8e-6}
x=np.linspace(0,2,1000000)

# NumPy vectorized calculation
start=time.perf_counter()
y_new=beams.ss_center(x,beam)
numpy_time=time.perf_counter()-start

# Original Python loop calculation
start=time.perf_counter()
y_old=np.array([beams_loop.ss_center(float(pos),beam) for pos in x])
loop_time=time.perf_counter()-start

# Compare results
print("Results match:",np.allclose(y_new,y_old))
print("NumPy time:",numpy_time,"seconds")
print("Loop time:",loop_time,"seconds")
print("Speedup:",loop_time/numpy_time,"times")

