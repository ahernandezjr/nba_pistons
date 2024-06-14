import os, sys

import numpy as np
import pandas as pd
from tqdm import tqdm

import torch
import torch.nn as nn
from torch.autograd import Variable
from torch.utils.data import DataLoader

from sklearn.preprocessing import StandardScaler, MinMaxScaler 

import matplotlib.pyplot as plt

from .torch import NBAPlayerDataset

from ..utils.config import settings
from ..utils.logger import get_logger


# Create logger
logger = get_logger(__name__)


# Set configs from settings
DATA_DIR = settings.DATA_DIR
DATA_FILE_NAME = settings.DATA_FILE_NAME
DATA_FILE_5YEAR_NAME = settings.DATA_FILE_5YEAR_NAME
DATA_FILE_5YEAR_TENSOR_NAME = settings.DATA_FILE_5YEAR_TENSOR_NAME
DATA_FILE_5YEAR_JSON_NAME = settings.DATA_FILE_5YEAR_JSON_NAME


# set device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load the dataset from the tensor file
df = pd.read_csv(DATA_FILE_5YEAR_TENSOR_NAME)

# Load the dictionary with proper numeric types
df_dict = pd.read_json(DATA_FILE_5YEAR_JSON_NAME, typ='series').to_dict()

# Instantiate the dataset
nba_dataset = NBAPlayerDataset(df)

# Create a DataLoader
data_loader = DataLoader(nba_dataset, batch_size=32, shuffle=False)


# Perform analytics on the dataset

# Get shape of the dataset
def get_input_shape(index=0):
    X, y = nba_dataset[index]
    print(f"X: {X.shape}, y: {y.shape}")

    return X, y


# Get the mean and standard deviation of the dataset
def get_mean_std():
    X = np.array([nba_dataset[i][0] for i in range(len(nba_dataset))])
    y = np.array([nba_dataset[i][1] for i in range(len(nba_dataset))])

    X_mean, X_std = np.mean(X), np.std(X)
    y_mean, y_std = np.mean(y), np.std(y)

    return X_mean, X_std, y_mean, y_std


# Get the min and max values of the dataset
def get_min_max():
    X = np.array([nba_dataset[i][0] for i in range(len(nba_dataset))])
    y = np.array([nba_dataset[i][1] for i in range(len(nba_dataset))])

    X_min, X_max = np.min(X), np.max(X)
    y_min, y_max = np.min(y), np.max(y)

    return X_min, X_max, y_min, y_max


# Get the number of features in the dataset
def get_num_features():
    X, y = nba_dataset[0]
    num_features = X.shape[1]

    return num_features


# Get the number of samples in the dataset
def get_num_samples():
    num_samples = len(nba_dataset)

    return num_samples


# Create graphs
def create_graphs():
    # Get the number of samples
    num_samples = get_num_samples()

    # Get the number of features
    num_features = get_num_features()

    # Get the mean and standard deviation
    X_mean, X_std, y_mean, y_std = get_mean_std()

    # Get the min and max values
    X_min, X_max, y_min, y_max = get_min_max()

    # Create a figure
    fig, axs = plt.subplots(2, 2, figsize=(10, 10))

    # Plot the number of samples
    axs[0, 0].bar(['Number of Samples'], [num_samples])
    axs[0, 0].set_title('Number of Samples')
    axs[0, 0].text(0, num_samples, f'{num_samples:.3g}', ha='center', va='bottom')
    

    # Plot the number of features
    axs[0, 1].bar(['Number of Features'], [num_features])
    axs[0, 1].set_title('Number of Features')
    axs[0, 1].text(0, num_features, f'{num_features:.3g}', ha='center', va='bottom')

    # Plot the mean and standard deviation
    axs[1, 0].bar(['X Mean', 'X Std', 'y Mean', 'y Std'], [X_mean, X_std, y_mean, y_std])
    axs[1, 0].set_title('Mean and Standard Deviation')
    axs[1, 0].text(0, X_mean, f'{X_mean:.3g}', ha='center', va='bottom')
    axs[1, 0].text(1, X_std, f'{X_std:.3g}', ha='center', va='bottom')
    axs[1, 0].text(2, y_mean, f'{y_mean:.3g}', ha='center', va='bottom')
    axs[1, 0].text(3, y_std, f'{y_std:.3g}', ha='center', va='bottom')

    # Plot the min and max values
    axs[1, 1].bar(['X Min', 'X Max', 'y Min', 'y Max'], [X_min, X_max, y_min, y_max])
    axs[1, 1].set_title('Min and Max Values')
    axs[1, 1].text(0, X_min, f'{X_min:.3g}', ha='center', va='bottom')
    axs[1, 1].text(1, X_max, f'{X_max:.3g}', ha='center', va='bottom')
    axs[1, 1].text(2, y_min, f'{y_min:.3g}', ha='center', va='bottom')
    axs[1, 1].text(3, y_max, f'{y_max:.3g}', ha='center', va='bottom')

    # Show the plots
    plt.show()

    # Save plots to GRAPHS_DIR
    fig.savefig(os.path.join(settings.GRAPHS_DIR, 'analytics.png'))