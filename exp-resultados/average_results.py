import pandas as pd

ROOT = "d:/OneDrive - Facultad de Ingeniería/Documents/Academics/fing-crowdcounting/exp-resultados/"
ROOT = "/home/renzo/fing/fing-crowdcounting/exp-resultados/"

shbs = [pd.read_csv(f'{ROOT}SHB1.csv'), pd.read_csv(f'{ROOT}SHB2.csv')]

shb = pd.concat(shbs).groupby(level=0).mean()

shb.to_csv(f"{ROOT}SHB.csv", float_format='%.4f')

qnrfs = [pd.read_csv(f'{ROOT}UCF-QNRF1.csv'), pd.read_csv(f'{ROOT}UCF-QNRF2.csv')]

qnrf = pd.concat(qnrfs).groupby(level=0).mean()

qnrf.to_csv(f"{ROOT}UCF-QNRF.csv", float_format='%.4f')
