#!/usr/bin/env python
# coding: utf-8

# # File Preprocessing

# MiBand에서 추출한 데이터를 Excel을 통해 모두 csv, UTF-8로 저장할 것
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import chardet #check file encoding

# Laplace Mechanism
from scipy.stats import laplace
from scipy.stats import gamma
from sympy import Symbol, exp, sqrt, pi, Integral
import math

# Paillier Homomorphic Encryption
import phe
from phe import paillier

# MongoDB
import pymongo
from pymongo import MongoClient

# Log 남기기
from datetime import datetime
import time


time_range = [10,11,12,13,14,15,16,17,18,19,20]
data_dir = '/home/hp/jupyter/ljh/eHealthPython/data/'
slot_size = len(time_range)*6

# 디렉토리 내의 csv 파일(걸음수 데이터)을 모두 가져와 리스트에 담는다
def get_file_list(dirname):
    f_list = []
    for (path, dir, files) in os.walk(dirname):
        for filename in files:
            ext = os.path.splitext(filename)[-1]
            if ext == '.csv' or ext =='.xls':
                f_list.append(os.path.join(path, filename))
    return f_list
file_list = get_file_list(data_dir)


# 파일의 인코딩 확인
def find_encoding(file):
    r_file = open(file, 'rb').read()
    result = chardet.detect(r_file)
    charenc = result['encoding']
    return charenc


# 라플라스 메커니즘으로 노이즈 추가
def lap_mechanism(original_data=[], loc=0, scale=0):
    def laprnd(loc,scale):
        s = laplace.rvs(loc, scale, None)
        return s
    
    N = 79
    sensitivity, epsilon = 7000, 1.0
    slot_size = len(original_data)
    noisy_data = list(map(lambda i: i + laprnd(0, (sensitivity/N)/(epsilon/slot_size)), original_data))
    return list(np.around(np.array(noisy_data)))


# 라플라스 메커니즘의 infinite divisibility(무한 분할성)을 활용한 감마 분포의 실수 차를 노이즈로 추가
# test = 1 : 기본 감마 노이즈 생성
# test = 2 : 그룹별 사용자 나눠서 평균 도출 실험
def lap_mechanism_gamma(original_data=[], loc=0, scale=0, people_num=0, epsil=0, test=0):
    def gammarnd(shpae, scale):
        def two_gammarnd_diff1():
            r = gamma.rvs(eshape, eloc, escale, size=2)

        rnd_diff_list=[]

        for i in range(len(original_data)):
            r = gamma.rvs(shape, 0, scale, 2)
            rnd_diff_list.append(r[0]-r[1])
        return rnd_diff_list

#     slot_size = np.count_nonzero(~np.isnan(original_data))    #number of salient point
    
    N = people_num
    slot_size = 66    #number of time period
    sensitivity, epsilon = 7000, epsil
    if test is 1:
        shape,scale = 1/N, (sensitivity/N)/(epsilon/slot_size)
    elif test is 2:
        group = 6
        shape,scale = 1/N, (sensitivity/(N/group))/(epsilon/(slot_size/group))
    
    gamma_noise_list = gammarnd(shape, scale)
    noisy_data = np.array(original_data) + np.array(gamma_noise_list)
    return noisy_data


# Paillier - Homomorphic Encryption Scheme
# encrypt with public_key & decrypt with private_key
class Paillier:
    def __init__(self):
        self.pub_key = 0
        self.priv_key = 0
    
    def setKey(self, pub_key, priv_key):
        self.pub_key, self.priv_key = paillier.generate_paillier_keypair(n_length=2048)
        
    def enc(self, data_lst=[]):
        encrypted_data_lst = []
        for data in data_lst:
            encrypted_data_lst.append(self.pub_key.encrypt(data))
        return encrypted_data_lst
    
    def func_chk(self, data_lst=[]):
        print('original data sum :',np.around(sum(data_lst)), 'encrypted data sum :', np.around(self.priv_key.decrypt(sum(self.enc(data_lst)))))
        print('original data average :', np.around(sum(data_lst)/len(data_lst)), 'encrypted data average :', np.around(self.priv_key.decrypt(sum(self.enc(data_lst))/len(self.enc(data_lst)))))


def histogram_generate(df):
    all_day_histogram_original_dict = dict()
    all_day_histogram_noisy_dict = dict()
    hours=[10,11,12,13,14,15,16,17,18,19,20]

    for date in dates:
        hour_data = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        for row in df.itertuples(index=False, name='Pandas'):
            if getattr(row, 'Date')==date:
                hour_data[getattr(row, 'Hour')-10] += getattr(row, 'Steps')
    #     print(np.around(np.array(hour_data)/6))
        all_day_histogram_original_dict[date] = list(np.around(np.array(hour_data)/6))

    for date in dates:
        original_data = all_day_histogram_original_dict[date]
        noisy_data = lap_mechanism(all_day_histogram_original_dict[date])
        all_day_histogram_noisy_dict[date] = noisy_data
#         print(date)
#         print(original_data)
#         print(noisy_data)
    graph_compare_with_noisy_data(all_day_histogram_original_dict[dates[0]], lap_mechanism(all_day_histogram_original_dict[dates[0]]), 0)
    
    return all_day_histogram_original_dict, all_day_histogram_noisy_dict


def sp_generate(arr):
    diff = np.diff(arr)
    diff_list = [1 if i>0 else(-1 if i<0  else 0) for i in diff]
    
    stack = []
    idx_list = []
    res_list = []

    for i in range(len(diff_list)):
        if i==0:
            stack.append(diff_list[i])
            idx_list.append(i)
        if diff_list[i] not in stack:
            stack.pop()
            stack.append(diff_list[i])
            idx_list.append(i)
        if i == len(diff_list)-1:
            idx_list.append(i+1)

    idx_list = np.array(idx_list)
    for i in idx_list:
        res_list.append(arr[i])
    arr_copy = arr.copy()

    for i in range(len(arr_copy)):
        if i not in idx_list:
            arr_copy[i] = np.nan

#     print('salient point 갯수 :', len(idx_list))
#     print('원본 데이터 갯수 :', len(arr))
#     print('salient point ->', arr_copy)
    return arr_copy


# 원본과 노이즈 추가된 데이터의 그래프 비교
def graph_compare_with_noisy_data(original_data, noisy_data, flag):
    plt.rcParams["figure.figsize"] = (10,4)
    plt.rcParams['lines.linewidth'] = 2
#     plt.rcParams['lines.color'] = 'r'
    plt.rcParams['axes.grid'] = True 
    if flag==0:
        time_range=[10,11,12,13,14,15,16,17,18,19,20]
        plt.plot(time_range, original_data, time_range, noisy_data, 'r-')
    elif flag==1:
        time_range= list(np.arange(66))
        plt.scatter(np.arange(len(noisy_data)), noisy_data)
        plt.plot(time_range, original_data)
    plt.xticks(time_range, rotation=70)
    plt.ylim(-500,max(noisy_data)+500)
    
    plt.show()
    
    
def get_abs_diff(ori, noi):
    o = np.array(ori)
    n = np.array(noi)
    diff = abs(o-n)
    
    return diff
    
    
def graph_compare_with_privacy_conditions(original_data, people_num, test):
    plt.rcParams["figure.figsize"] = (10,4)
    plt.rcParams['lines.linewidth'] = 2
    plt.rcParams['axes.grid'] = True
    time_range= list(np.arange(66))
    
    e1 = lap_mechanism_gamma(original_data, 0, 0, people_num, 0.1, test)
    e2 = lap_mechanism_gamma(original_data, 0, 0, people_num, 0.5, test)
    e3 = lap_mechanism_gamma(original_data, 0, 0, people_num, 1.0, test)
    
    plt.plot(time_range, original_data, 'y-',
            time_range, e1, 'r-',
            time_range, e2, 'g-',
            time_range, e3, 'b-')
#     d1 = abs(sum(original_data) - sum(e1))
#     d2 = abs(sum(original_data) - sum(e2))
#     d3 = abs(sum(original_data) - sum(e3))

    d1 = sum(get_abs_diff(original_data, e1))/slot_size
    d2 = sum(get_abs_diff(original_data, e2))/slot_size
    d3 = sum(get_abs_diff(original_data, e3))/slot_size
    
    print('epsilon 0.1 :', d1)
    print('epsilon 0.5 :', d2)
    print('epsilon 1.0 :', d3)
    
    plt.xticks(time_range, rotation=70)
    plt.ylim(-500, 8000)
    plt.show()
    
    return d1, d2, d3
  
    
def graph_compare_3(original_data, people_num, test):
    plt.rcParams["figure.figsize"] = (12, 4)
    plt.rcParams['lines.linewidth'] = 2
    plt.rcParams['axes.grid'] = True
    time_range= list(np.arange(66))
    
    e1 = lap_mechanism_gamma(original_data, 0, 0, people_num, 0.1, test)
    e2 = lap_mechanism_gamma(original_data, 0, 0, people_num, 0.5, test)
    e3 = lap_mechanism_gamma(original_data, 0, 0, people_num, 1.0, test)
    
    plt.figure(1)
    plt.plot(time_range, original_data, 'b-',
            time_range, e1, 'r-')
    plt.xticks(time_range, rotation=70)
    plt.ylim(-500, 8000)
    
    plt.figure(2)
    plt.plot(time_range, original_data, 'b-',
            time_range, e2, 'r-')
    plt.xticks(time_range, rotation=70)
    plt.ylim(-500, 8000)
    
    plt.figure(3)
    plt.plot(time_range, original_data, 'b-',
            time_range, e3, 'r-')
    plt.xticks(time_range, rotation=70)
    plt.ylim(-500, 8000)
    
    plt.show()
    
#     d1 = abs(sum(original_data) - sum(e1))
#     d2 = abs(sum(original_data) - sum(e2))
#     d3 = abs(sum(original_data) - sum(e3))

    d1 = sum(get_abs_diff(original_data, e1))/slot_size
    d2 = sum(get_abs_diff(original_data, e2))/slot_size
    d3 = sum(get_abs_diff(original_data, e3))/slot_size

    print('epsilon 0.1 :', d1)
    print('epsilon 0.5 :', d2)
    print('epsilon 1.0 :', d3)
    
    return d1, d2, d3
    

# 실험 결과를 txt 파일에 쓰기
def write_result_to_txt(msg, file_name=''):
    file_dir = '/home/hp/jupyter/ljh/eHealthPython/result/'
    file_dir += file_name
    with open(file_dir, "at") as f:
        now = datetime.now()
        tmp = '%s-%s-%s %s:%s:%s' %(now.year, now.month, now.day, now.hour+9, now.minute, now.second)
#         tmp = '%04d-%02d-%02d %02d:%02d:%02d' % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)
        tmp += '\t'
        tmp += str(msg)
        f.write(tmp)
        f.write('\n')