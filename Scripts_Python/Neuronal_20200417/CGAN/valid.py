import argparse
import os
import numpy as np
from PIL import Image
import torch
from torch.autograd import Variable
import torchvision.transforms as transforms
#import torchvision.transforms as standard_transforms
#from sklearn.preprocessing import minmax_scale,StandardScaler
from skimage import img_as_ubyte
import torch.nn as nn
#from util import is_image_file, load_img, save_img
from skimage.io import imread, imsave
from skimage import io
from glob import glob
#import SimpleITK as sitk
#import nibabel as nib
from math import log10
import h5py
os.environ["CUDA_VISIBLE_DEVICES"] = "0,1"

# Testing settings
parser = argparse.ArgumentParser(description='pix2pix-PyTorch-implementation')
parser.add_argument('--batchSize', type=int, default=4, help='training batch size')
parser.add_argument('--testBatchSize', type=int, default=1, help='testing batch size')
parser.add_argument('--nEpochs', type=int, default=200, help='number of epochs to train for')
parser.add_argument('--input_nc', type=int, default=16, help='input image channels')
parser.add_argument('--output_nc', type=int, default=1, help='output image channels')
parser.add_argument('--ngf', type=int, default=64, help='generator filters in first conv layer')
parser.add_argument('--ndf', type=int, default=64, help='discriminator filters in first conv layer')
parser.add_argument('--lr', type=float, default=0.0002, help='Learning Rate. Default=0.002')
parser.add_argument('--beta1', type=float, default=0.5, help='beta1 for adam. default=0.5')
parser.add_argument('--threads', type=int, default=4, help='number of threads for data loader to use')
parser.add_argument('--seed', type=int, default=123, help='random seed to use. Default=123')
parser.add_argument('--lamb', type=int, default=10, help='weight on L1 term in objective')
parser.add_argument('--dataset', default=True, help='DEEP-TFM-l1loss')
parser.add_argument('--model', type=str, default='checkpoint/DEEP-TFM-l1loss/netG_model_epoch_50.pth.tar', help='model file to use')
parser.add_argument('--cuda', default=True, help='use cuda')
opt = parser.parse_args(args=[])
max_im = 100
max_gt = 741

criterionMSE = nn.MSELoss() 
img_dir = open('train.txt','r')

avg_mse = 0
avg_psnr = 0
h5_dir = '/n/holyscratch01/wadduwage_lab/uom_bme/ForwardModel_matlab/_cnn_synthTrData/03-Jun-2020/cells_tr_data_6sls_03-Jun-2020.h5'

for epochs in range(12,13):
    my_model = '/n/holyscratch01/wadduwage_lab/uom_bme/2020_static/Data_02Apr2020/unetscse/depth_6/checkpoint/DEEP-TFM-lr-0.001/netG_model_epoch_' + str(epochs) + '.pth.tar'
    netG = torch.load(my_model)
    netG.eval()
    p = 0
    for line in img_dir:
        print(line)
        id_ = int(line)
        with h5py.File(h5_dir, 'r') as db:

             modalities = db['input'][id_] 
             GT_ = db['gt'][id_] 
        depth = modalities.shape[2]
        predicted_im = np.zeros((160,160,1))
        if np.min(np.array(GT_))==np.max(np.array(GT_)):
             print('Yes')
        GT = torch.from_numpy(np.divide(GT_,max_gt))
        img = torch.from_numpy(np.divide(modalities,max_im)[None, :, :]).float()
        netG = netG.cuda()
        input = img.cuda()
        out = netG(input)
        print(out.max())
        out = out.cpu()
        out_img = out.data[0]
        out_img = np.squeeze(out_img)

        mymin = np.min(np.array(out_img))
        mymax = np.max(np.array(out_img))
        out_img += abs(mymin)
        out_img = out_img * max_gt

        out_img = np.array(np.squeeze(out_img),dtype=np.uint8)
        GT = img_as_ubyte(np.squeeze(GT))

        predict_path= 'Predicted/epoch_' + str(epochs) +'/'
        if not os.path.exists(predict_path):
            os.makedirs(predict_path)
        imsave(predict_path + '/' + str(line[0:-1]) + '_pred.png',out_img)
        imsave(predict_path + '/' + str(line[0:-1]) + '_gt.png',(GT))
print('mse=',torch.div(avg_mse,p))
print(avg_mse)
print(avg_psnr)
print(p)
img_dir.close()
