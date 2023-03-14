
import glob
import json
import numpy as np
import matplotlib.pyplot as plt
import os
import math
import pandas as pd
import statistics

DATASET_PATH = "mt_datos/ground_truth/*/*.json"
MT_UMBRELLA = ["aj01", "aj02", "aj03", "aj04", "bj01", "bj02"]
MT_LOW = ["aj06", "aj08", "aj09", "aj10", "aj11", "aj12", "aj13", "aj14", "aj15", "aj16", "aj17", "am01", "am04"]
MT_MID = ["aj05", "aj07", "am02", "am03", "am05", "am06", "am07", "bj03", "bj04", "bj05", "bj06", "bj07", "bj08", "bj09", "bj10", "bj11", "bj12", "bm01", "bm02", "bm04", "bm07", "bm08", "bm09", "bm10", "bm12", "bm13"]
MT_AERIAL = ["bm03", "bm05", "bm06", "bm11", "cm01", "cm02", "cm03", "cm04", "cm05", "cm06", "cm07", "cm08"]

def read_annotations():
    annotations = {}
    for annotation_file in glob.glob(DATASET_PATH):
        with open(annotation_file) as f:
            data = json.load(f)
        if data['human_num'] != len(data['points']):
            print("Error: ", f)
            exit(1)
        annotation_img = os.path.basename(annotation_file).replace(".json", "")
        annotator = os.path.basename(os.path.dirname(annotation_file))
        if annotation_img not in annotations:
            annotations[annotation_img] = {}
        annotations[annotation_img][annotator] = data['human_num']
    annotations_umbrella = {k: v for k, v in annotations.items() if k in MT_UMBRELLA}
    annotations_low = {k: v for k, v in annotations.items() if k in MT_LOW}
    annotations_mid = {k: v for k, v in annotations.items() if k in MT_MID}
    annotations_aerial = {k: v for k, v in annotations.items() if k in MT_AERIAL}
    return annotations_umbrella, annotations_low, annotations_mid, annotations_aerial, annotations

def visualize_annotations(annotations, title):
    error = {}
    print()
    print("Visualizing:", title)
    print('\t'.join(['    '] + [str(i) for i in range(1, 13)] + ["Mean (std)"]))
    for img in sorted(annotations.keys()):
        print(img, end=' & ')
        vls = []
        for ann in sorted(annotations[img].keys(), key=int):
            vls.append(annotations[img][ann])
        mean = sum(vls)/len(vls)
        std = statistics.pstdev(vls)
        for c, v in enumerate(vls, start=1): 
            if abs(v-mean) > std:
                print("\\textbf{"+str(v)+"}", end=' & ') 
            else:    
                print(v, end=' & ') 
        print(f"%.1f (%.1f, %.1f" % (mean, std, 100*std/mean) + "%) \\\\")
    print_general_statistics(annotations, title)

def box_plot(annotations, title):
    annotations_matrix = np.array([[c for c in ann.values()] for img, ann in annotations.items()])
    print(annotations_matrix)
    plt.suptitle(title)
    plt.boxplot(np.transpose(annotations_matrix), showmeans=True, meanline=True)
    plt.xticks(list(range(1, len(annotations)+1)), [k for k in annotations.keys()])
    plt.show()

def print_general_statistics(annotations, title):
    print()
    total_annotations = []
    for img, ann in annotations.items():
        for annot, c in ann.items():
            total_annotations.append(c)
    print(f"{title} mean: %.2f" % statistics.mean(total_annotations))

def process_metrics(subset, title):
    with open("mt_datos/results_models_metrics.json") as f:
        data = json.load(f)
    df = pd.DataFrame()
    final_metrics = {"Model": [], "MAE": [], "MSE": [], "RMSE": [], "GAME4": [], "GAME16": [], "PSNR": [], "SSIM": []}
    for model, weight_data in data.items():
        for weights, img_data in weight_data.items():
            mae, mse, game4, game16, psnr, ssim = [], [], [], [], [], []
            for img_name, metrics in img_data.items():
                if img_name.replace(".jpg", "") in subset:
                    mae.append(metrics["MAE"]); mse.append(metrics["MSE"])
                    game4.append(metrics["GAME4"]); game16.append(metrics["GAME16"])
                    psnr.append(metrics["PSNR"]); ssim.append(metrics["SSIM"])
            avg_mse = statistics.mean(mse)
            final_metrics["Model"].append(f"{model}-{weights}")
            final_metrics["MAE"].append(round(statistics.mean(mae), 4))
            final_metrics["MSE"].append(round(avg_mse, 4))
            final_metrics["RMSE"].append(round(math.sqrt(avg_mse), 4))
            final_metrics["GAME4"].append(round(statistics.mean(game4), 4))
            final_metrics["GAME16"].append(round(statistics.mean(game16), 4))
            final_metrics["PSNR"].append(round(statistics.mean(psnr), 4))
            final_metrics["SSIM"].append(round(statistics.mean(ssim), 4))
    df = pd.DataFrame.from_dict(final_metrics)
    df.to_csv(f"mt_datos/metrics/{title}.csv")

def main():
    annotations_umbrella, annotations_low, annotations_mid, annotations_aerial, annotations_all = read_annotations()
    visualize_annotations(annotations_umbrella, "Paraguas"); visualize_annotations(annotations_low, "Densidad Baja")
    visualize_annotations(annotations_mid, "Densidad Media"); visualize_annotations(annotations_aerial, "Aérea")
    # box_plot(annotations_umbrella, "Paraguas"); box_plot(annotations_low, "Densidad baja")
    # box_plot(annotations_mid, "Densidad Media"); box_plot(annotations_aerial, "Aérea")
    print_general_statistics(annotations_all, "General")
    process_metrics(MT_UMBRELLA, "metrics_umbrella"); process_metrics(MT_LOW, "metrics_low")
    process_metrics(MT_MID, "metrics_mid"); process_metrics(MT_AERIAL, "metrics_aerial")

if __name__ == '__main__':
    main()
