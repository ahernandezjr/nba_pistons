'''
MUCH OF THIS CODE IS NOT ORIGINAL CODE
USED FOR REFERENCING PURPOSES
SOURCE: 'https://charlieoneill.medium.com/predicting-the-price-of-bitcoin-with-multivariate-pytorch-lstms-695bc294130'
'''

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

from ..data_process.dataset_torch import NBAPlayerDataset

from ..utils.config import settings
from ..utils.logger import getLogger


# Create logger
logger = getLogger(__name__)


# Set configs from settings
DATA_DIR = settings.DATA_DIR
DATA_FILE_NAME = settings.DATA_FILE_NAME
DATA_FILE_5YEAR_NAME = settings.DATA_FILE_5YEAR_NAME
DATA_FILE_5YEAR_JSON_NAME = settings.DATA_FILE_5YEAR_JSON_NAME


class LSTM(nn.Module):
    def __init__(self, num_classes, input_size, hidden_size, num_layers):
        super().__init__()
        self.num_classes = num_classes # output size
        self.num_layers = num_layers # number of recurrent layers in the lstm
        self.input_size = input_size # input size
        self.hidden_size = hidden_size # neurons in each lstm layer
        # LSTM model
        self.lstm = nn.LSTM(input_size=input_size, hidden_size=hidden_size,
                            num_layers=num_layers, batch_first=True, dropout=0.2) # lstm
        self.fc_1 =  nn.Linear(hidden_size, 128) # fully connected 
        self.fc_2 = nn.Linear(128, num_classes) # fully connected last layer
        self.relu = nn.ReLU()
        
    def forward(self,x):
        # hidden state
        h_0 = Variable(torch.zeros(self.num_layers, x.size(0), self.hidden_size))
        # cell state
        c_0 = Variable(torch.zeros(self.num_layers, x.size(0), self.hidden_size))
        # propagate input through LSTM
        output, (hn, cn) = self.lstm(x, (h_0, c_0)) # (input, hidden, and internal state)
        hn = hn.view(-1, self.hidden_size) # reshaping the data for Dense layer next
        out = self.relu(hn)
        out = self.fc_1(out) # first dense
        out = self.relu(out) # relu
        out = self.fc_2(out) # final output
        return out


def training_loop(epochs, lstm, optimizer, loss_fn, dataloader):
    for epoch in tqdm(range(epochs)):
        for i, (inputs, targets) in enumerate(dataloader):
            lstm.train()
            outputs = lstm.forward(inputs) # forward pass
            optimizer.zero_grad() # calculate the gradient, manually setting to 0
            # obtain the loss function
            loss = loss_fn(outputs, targets)
            loss.backward() # calculates the loss of the loss function
            optimizer.step() # improve from loss, i.e backprop
            # test loss
            lstm.eval()
    

# def test_loop(lstm, optimizer, loss_fn, test_loader):

def run_lstm(epochs=1000):
    '''
    Run the LSTM model.
    '''
    # Load the dictionary with proper numeric types
    df_dict = pd.read_json(DATA_FILE_5YEAR_JSON_NAME, typ='series').to_dict()

    # Instantiate the dataset
    nba_dataset = NBAPlayerDataset(df_dict)

    # Create a training DataLoader and test DataLoader
    train_loader = DataLoader(nba_dataset, batch_size=32, shuffle=True)
    test_loader  = DataLoader(nba_dataset, batch_size=32, shuffle=False)

    

    # # Check the first item in the DataLoader
    # for i, (inputs, targets) in enumerate(dataloader):
    #     print(inputs)
    #     print(targets)
    #     break

    # Define hyperparameters
    learning_rate = 0.001 # 0.001 lr

    input_size = 39 # number of features
    hidden_size = 39 # number of features in hidden state
    num_layers = 5 # number of stacked lstm layers

    num_classes = 39 # number of output classes 

    # Create the LSTM model
    model = LSTM(num_classes=num_classes, 
                 input_size=input_size, 
                 hidden_size=hidden_size, 
                 num_layers=num_layers)

    # Define the loss function and the optimizer
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

    # Training loop
    training_loop(n_epochs=epochs,
                lstm=model,
                optimizer=optimizer,
                loss_fn=criterion,
                dataloader=dataloader)


   

    # # Training loop
    # for epoch in tqdm(range(epochs)):
    #     for i, (inputs, targets) in enumerate(dataloader):
    #         # DO NOT Flatten 2d targets to 1d
    #         # targets = targets.view(-1)

    #         # Convert inputs and targets to tensors
    #         print(targets.shape)
    #         inputs = torch.tensor(inputs).float()
    #         targets = torch.tensor(targets).float()

    #         # Forward pass
    #         outputs = model(inputs)
    #         loss = criterion(outputs, targets)

    #         # Backward and optimize
    #         optimizer.zero_grad()
    #         loss.backward()
    #         optimizer.step()

    #     if (epoch+1) % 100 == 0:
    #         print(f'Epoch {epoch+1}/{epochs}, Loss: {loss.item()}')


# TO DO: Implement to predict every year for first 5 years
def arima():
    '''
    Run the ARIMA model.
    '''
    pass


# def split_sequences(input_sequences, output_sequence, n_steps_in, n_steps_out):
#     '''
#     Split a multivariate sequence past, future samples (X and y)
    
#     Args:
#         input_sequences (np.array): The input sequences.
#         output_sequence (np.array): The output sequences. 
#         n_steps_in (int): The number of steps in.
#         n_steps_out (int): The number of steps out.
        
#     Returns:
#         np.array: The input sequences.
#         np.array: The output sequences.
#     '''
#     X, y = list(), list() # instantiate X and y
#     for i in range(len(input_sequences)):
#         # find the end of the input, output sequence
#         end_ix = i + n_steps_in
#         out_end_ix = end_ix + n_steps_out - 1
#         # check if we are beyond the dataset
#         if out_end_ix > len(input_sequences): break
#         # gather input and output of the pattern
#         seq_x, seq_y = input_sequences[i:end_ix], output_sequence[end_ix-1:out_end_ix, -1]
#         X.append(seq_x), y.append(seq_y)
#     return np.array(X), np.array(y)


# # Create NBA dataset
# nba_dataset = NBAPlayerDataset(DATA_FILE_5YEAR_NAME, DATA_FILE_5YEAR_JSON_NAME)

# # Create a training loop for pytorch NBA dataset
# df = pd.read_csv(os.path.join(DATA_DIR, DATA_FILE_NAME))
# X, y = df.drop(columns=['Close']), df.Close.values

# scaler_X = StandardScaler()
# scaler_y = MinMaxScaler()

# X_trans = scaler_X.fit_transform(X)
# y_trans = scaler_y.fit_transform(y.reshape(-1, 1))

# # Assuming split_sequences is a function that you have defined elsewhere
# X_ss, y_mm = split_sequences(X_trans, y_trans, 100, 50)

# total_samples = len(X)
# train_test_cutoff = round(0.90 * total_samples)

# input_size = 4 # number of features
# hidden_size = 2 # number of features in hidden state
# num_layers = 1 # number of stacked lstm layers

# n_epochs = 1000 # 1000 epochs
# learning_rate = 0.001 # 0.001 lr

# df_X_ss = scaler_X.transform(df.drop(columns=['Close'])) # old transformers
# df_y_mm = scaler_y.transform(df.Close.values.reshape(-1, 1)) # old transformers


# def training_loop(n_epochs, lstm, optimiser, loss_fn, X_train, y_train,
#                   X_test, y_test):
#     for epoch in range(n_epochs):
#         lstm.train()
#         outputs = lstm.forward(X_train) # forward pass
#         optimiser.zero_grad() # calculate the gradient, manually setting to 0
#         # obtain the loss function
#         loss = loss_fn(outputs, y_train)
#         loss.backward() # calculates the loss of the loss function
#         optimiser.step() # improve from loss, i.e backprop
#         # test loss
#         lstm.eval()
#         test_preds = lstm(X_test)
#         test_loss = loss_fn(test_preds, y_test)
#         if epoch % 100 == 0:
#             print("Epoch: %d, train loss: %1.5f, test loss: %1.5f" % (epoch, 
#                                                                       loss.item(), 
#                                                                       test_loss.item())) 
            


# import warnings
# warnings.filterwarnings('ignore')

# n_epochs = 1000 # 1000 epochs
# learning_rate = 0.001 # 0.001 lr

# input_size = 4 # number of features
# hidden_size = 2 # number of features in hidden state
# num_layers = 1 # number of stacked lstm layers

# num_classes = 50 # number of output classes 

# lstm = LSTM(num_classes, 
#               input_size, 
#               hidden_size, 
#               num_layers)



# training_loop(n_epochs=n_epochs,
#               lstm=lstm,
#               optimiser=optimiser,
#               loss_fn=loss_fn,
#               X_train=X_train_tensors_final,
#               y_train=y_train_tensors,
#               X_test=X_test_tensors_final,
#               y_test=y_test_tensors)




# df_X_ss = ss.transform(df.drop(columns=['Close'])) # old transformers
# df_y_mm = mm.transform(df.Close.values.reshape(-1, 1)) # old transformers
# # split the sequence
# df_X_ss, df_y_mm = split_sequences(df_X_ss, df_y_mm, 100, 50)
# # converting to tensors
# df_X_ss = Variable(torch.Tensor(df_X_ss))
# df_y_mm = Variable(torch.Tensor(df_y_mm))
# # reshaping the dataset
# df_X_ss = torch.reshape(df_X_ss, (df_X_ss.shape[0], 100, df_X_ss.shape[2]))

# train_predict = lstm(df_X_ss) # forward pass
# data_predict = train_predict.data.numpy() # numpy conversion
# dataY_plot = df_y_mm.data.numpy()

# data_predict = mm.inverse_transform(data_predict) # reverse transformation
# dataY_plot = mm.inverse_transform(dataY_plot)
# true, preds = [], []
# for i in range(len(dataY_plot)):
#     true.append(dataY_plot[i][0])
# for i in range(len(data_predict)):
#     preds.append(data_predict[i][0])
# plt.figure(figsize=(10,6)) #plotting
# plt.axvline(x=train_test_cutoff, c='r', linestyle='--') # size of the training set

# plt.plot(true, label='Actual Data') # actual plot
# plt.plot(preds, label='Predicted Data') # predicted plot
# plt.title('Time-Series Prediction')
# plt.legend()
# plt.savefig("whole_plot.png", dpi=300)
# plt.show() 