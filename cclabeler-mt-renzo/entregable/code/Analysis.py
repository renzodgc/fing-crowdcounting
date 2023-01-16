# -*- coding: utf-8 -*-
"""
Created on Sat Nov  3 14:50:14 2018

@author: lenovo
"""

# Python Imports

import cv2
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import h5py
import glob
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import keras
import tensorflow as tf

from pathlib import Path
from PIL import Image
from sklearn.metrics import mean_absolute_error
from matplotlib import cm as c
from keras.models import model_from_json

import warnings
warnings.filterwarnings("ignore")

# model_A_weights (Trained with ShanghaiTech A: Shanghai crowd pictures from the Internet)
MODELS_PATHS = [("A", "weights/model_A_weights.h5"), ("B", "weights/model_B_weights.h5")]
DATASET_PATH = "../cclabeler-mt-renzo/data"
MODEL_JSON = "models/Model.json"

RESULTS_PATH = "results"
VISUALIZATION_PATH = f"{RESULTS_PATH}/visualization"

# Images are too high res and are processed in blocks
BLOCKS_IMAGES = ["cm02", "bm01", "bm02", "cm01"]

def load_model(model):
    # Function to load and return neural network model 
    json_file = open(MODEL_JSON, 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    loaded_model = model_from_json(loaded_model_json)
    loaded_model.load_weights(model)
    return loaded_model

def create_img(path):
    # Function to load,normalize and return image 
    im = Image.open(path).convert('RGB')
    
    im = np.array(im)
    
    im = im/255.0
    
    im[:,:,0]=(im[:,:,0]-0.485)/0.229
    im[:,:,1]=(im[:,:,1]-0.456)/0.224
    im[:,:,2]=(im[:,:,2]-0.406)/0.225

    im = np.expand_dims(im, axis  = 0)
    return im

def predict(path, model):
    # Function to load image,predict heat map, generate count and return (image , heat map, count)
    image = create_img(path)
    if any(s in path for s in BLOCKS_IMAGES):
        if image.shape[1] % 2 != 0:
            image = np.resize(image, (1, image.shape[1] + 1, image.shape[2], 3))
        # Images are too high res. Split
        vsplits = np.vsplit(image[0], 2)
        vstacks = []
        for vertical_section in vsplits:
            hsplits = np.hsplit(vertical_section, 4)
            hstacks = []
            for horizonal_section in hsplits:
                hstacks.append(model.predict(np.expand_dims(horizonal_section, 0))[0])
            vstacks.append(np.hstack(hstacks))
        pred_hmap = np.expand_dims(np.vstack(vstacks), 0)
    else:
        pred_hmap = model.predict(image)
    pred_count = np.sum(pred_hmap)
    return image, pred_hmap, pred_count

def run_test(test_image_path, test_gt_path, model, model_index):
    image, pred_hmap, pred_count = predict(test_image_path, model)
    gt_file = h5py.File(test_gt_path , 'r')
    gt_hmap = np.asarray(gt_file['density'])
    gt_count = np.sum(gt_hmap)
    process_test_results(image, pred_hmap, pred_count, gt_hmap, gt_count, test_image_path, model_index)
    return image, pred_hmap, pred_count, gt_hmap, gt_count

def process_test_results(img, pred_hmap, pred_count, gt_hmap, gt_count, image_path, model_index):
    print(f"{os.path.basename(image_path)} - Predict Count: {pred_count} out of {gt_count} annotated")
    image_name, image_ext = os.path.splitext(os.path.basename(image_path))
    original_image = cv2.imread(image_path)
    pred_hmap = pred_hmap.reshape(pred_hmap.shape[1], pred_hmap.shape[2])
    pred_image = cv2.resize(pred_hmap, dsize=(img.shape[2], img.shape[1]), interpolation=cv2.INTER_CUBIC)

    cv2.imwrite(os.path.join(VISUALIZATION_PATH, model_index, f"{image_name}-img{image_ext}"), original_image)
    fig = plt.imshow(pred_image, cmap = c.jet)
    plt.axis('off')
    fig.axes.get_xaxis().set_visible(False)
    fig.axes.get_yaxis().set_visible(False)
    plt.savefig(os.path.join(VISUALIZATION_PATH, model_index, f"{image_name}-img-pred{image_ext}"), bbox_inches='tight', pad_inches = 0)
    plt.close()
    fig = plt.imshow(gt_hmap, cmap = c.jet)
    plt.axis('off')
    fig.axes.get_xaxis().set_visible(False)
    fig.axes.get_yaxis().set_visible(False)
    plt.savefig(os.path.join(VISUALIZATION_PATH, model_index, f"{image_name}-img-gt{image_ext}"), bbox_inches='tight', pad_inches = 0)
    plt.close()

def test_dataset(index, model_path):
    print()
    print(f"--- Starting model {index} ---")
    print()
    model = load_model(model_path)
    img_paths = glob.glob(os.path.join(DATASET_PATH, "images", '*.jpg'))

    name = []
    y_true = []
    y_pred = []

    Path(os.path.join(VISUALIZATION_PATH, index)).mkdir(parents=True, exist_ok=True)

    print([os.path.basename(i) for i in img_paths])
    for image_path in img_paths:
        print(os.path.basename(image_path))
        gt_path = image_path.replace('.jpg','.h5').replace('images','h5')
        img, pred_hmap, pred_count, gt_hmap, gt_count = run_test(image_path, gt_path, model, index)
        name.append(os.path.basename(image_path))
        y_pred.append(pred_count)
        y_true.append(gt_count)
        if any([s in image_path for s in BLOCKS_IMAGES]):
            keras.backend.clear_session()
            model = load_model(model_path)

    data = pd.DataFrame({'name': name, 'y_pred': y_pred, 'y_true': y_true})
    data.to_csv(f'{RESULTS_PATH}/test_{index}.csv', sep=',')
    ans = mean_absolute_error(np.array(y_true), np.array(y_pred))
    print(f"--- Model {index} finished. Total MAE : {ans} ---")
    print()
    print()

if __name__ == "__main__":
    for index, model_path in MODELS_PATHS:
        test_dataset(index, model_path)
        keras.backend.clear_session()
