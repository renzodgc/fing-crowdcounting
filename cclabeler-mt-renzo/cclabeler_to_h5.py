"""
Based on: https://github.com/DiaoXY/CSRnet/blob/master/Preprocess.py

TODO: What to do with this comment
Created on Sat Nov  3 14:32:23 2018
生成groundh5文件
# Data Preprocessing :
In data preprocessing, the main objective was to convert the ground truth 
provided by the ShanghaiTech dataset into density maps. For a given image the dataset 
provided a sparse matrix consisting of the head annotations in that image. 
This sparse matrix was converted into a 2D density map by passing through a Gaussian Filter.
The sum of all the cells in the density map results in the actual count of people in that 
particular image. Refer the `Preprocess.ipynb` notebook for the same.

# Data preprocessing math explained:
Given a set of head annotations our task is to convert it to a density map.
1) Build a kdtree(a kdtree is a data structure that allows fast computation of K 
Nearest neighbours) of the head annotations.
2) Find the average distances for each head with K(in this case 4) nearest heads in the head
 annotations. Multpiply this value by a    factor, 0.3 as suggested by the author of the paper.
3) Put this value as sigma and convolve using the 2D Gaussian filter. 

@author: lenovo
"""

import glob
import h5py
import json
import numpy as np
import os
import scipy.io as io

from matplotlib import cm as CM
from matplotlib import pyplot as plt
from scipy import spatial
from scipy.ndimage import gaussian_filter
from tqdm import tqdm

BASE_PATH = "data"
IMAGE_PATH = f"{BASE_PATH}/images"
JSON_PATH = f"{BASE_PATH}/jsons"

def gaussian_filter_density(gt):
    """
    Receives a list of coordinates (x,y) and returns a density map
    """
    #Generates a density map using Gaussian filter transformation   
    density = np.zeros(gt.shape, dtype=np.float32)
    
    gt_count = np.count_nonzero(gt)
    
    if gt_count == 0:
        return density
    # Find out the K nearest neighbours using a KDTree
   
    pts = np.array(list(zip(np.nonzero(gt)[1].ravel(), np.nonzero(gt)[0].ravel())))
    leafsize = 2048
    
    # build kdtree
    tree = spatial.KDTree(pts.copy(), leafsize=leafsize)
    
    # query kdtree
    distances, locations = tree.query(pts, k=4)
       
    for i, pt in enumerate(pts): # 枚举，返回序列（索引，数据）
        pt2d = np.zeros(gt.shape, dtype=np.float32)
        pt2d[pt[1],pt[0]] = 1.
        if gt_count > 1:
            sigma = np.sum(distances[i][1:4])*0.1
            # sigma = np.mean(distances[i][1:4])*0.1
        else:
            sigma = np.average(np.array(gt.shape))/2./2. # case: 1 point
        
        # Convolve with the gaussian filter
        kernel_value = gaussian_filter(pt2d, sigma, mode='constant')
        normalized_kernel_value = kernel_value / np.sum(kernel_value)
        density += normalized_kernel_value
    total_sum = np.sum(density)
    if abs(gt_count - total_sum) > 0.01:
        import pdb; pdb.set_trace()
    return density

def convert_annotations(data_format = "json", gt_path = JSON_PATH):
    """
    Loads annotations from a given fromat, applies gaussian filter and converts them to a .h5 file.
    """
    # List of all image paths
    gt_paths = [gt_path for gt_path in glob.glob(os.path.join(gt_path, f"*.{data_format}"))]
    print(gt_paths)
    print(f"Number of annotations: {len(gt_paths)}")

    for gt_path in tqdm(gt_paths):
        if data_format == "mat":
            # Load sparse matrix
            mat = io.loadmat(gt_path)["image_info"]
            gt = mat[0,0][0,0][0]
            # TODO: Only works for ST
            # img = plt.imread(gt_path.replace('.jpg','.mat').replace('images','ground_truth').replace('IMG_','GT_IMG_'))
        elif data_format == "json":
            with open(gt_path, 'r') as json_data:
                gt_raw = json.loads(json_data.read())
            gt = np.array([(p['x'], p['y']) for p in gt_raw["points"]])
            img = plt.imread(gt_path.replace(f".{data_format}",'.jpg').replace('jsons','images'))

        # Create a zero matrix of image size
        k = np.zeros((img.shape[0],img.shape[1]))
        
        #Generate hot encoded matrix of sparse matrix
        for i in range(0,len(gt)):
            if int(gt[i][1])<img.shape[0] and int(gt[i][0])<img.shape[1]:
                k[int(gt[i][1]), int(gt[i][0])]=1
        
        # generate density map
        density_map = gaussian_filter_density(k)

        # File path to save density map
        file_path = gt_path.replace("jsons", "h5").replace(f".{data_format}",'.h5')
        
        with h5py.File(file_path, 'w') as hf:
            hf['density'] = density_map

    print("Finished!")
    print()
    print("Sample Ground Truth:")
    file_path = gt_paths[0].replace(f".{data_format}",'.h5').replace("jsons", "h5")
    print(file_path)
    gt_file = h5py.File(file_path,'r')
    groundtruth = np.asarray(gt_file['density'])
    plt.imshow(groundtruth,cmap=CM.jet) # CM.jet显示蓝-青-黄-红四色
    print("Sum = ", np.sum(groundtruth))

convert_annotations()
