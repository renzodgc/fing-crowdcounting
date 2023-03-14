import glob
import pandas as pd

# ROOT = "d:/OneDrive - Facultad de Ingeniería/Documents/Academics/fing-crowdcounting/exp-resultados/"
ROOT = "/home/renzo/fing/fing-crowdcounting/exp-resultados/"

print(glob.glob(f"{ROOT}*.csv"))
csvs = [(path, pd.read_csv(path)) for path in glob.glob(f"{ROOT}*.csv")]

for path, data in csvs:
    import pdb; pdb.set_trace()
    data["RMSE"] = data["MSE"]**(1/2)
    data.to_csv(path, float_format='%.4f')
