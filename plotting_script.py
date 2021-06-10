#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun  3 14:04:05 2021

@author: macproizzy

Description
-----------------------
This script contains the functions necessary to produce the visualizations we have so far for 
TDT data. Eventually this can be tweaked to work with NWB Files. 

What we have: 
    Plot of the trialized z-scored mean response
    Spectrogram grid plot 
"""

#%%
import matplotlib.pyplot as plt
import numpy as np 
import tdt
import os
import warnings 
warnings.simplefilter("ignore")


#%%

def plot_all(data_directory, chs, stimulus_onset = .25, baseline_start = .05, baseline_stop = .15):
    tdt_data = tdt.read_block(data_directory)
    fs = tdt_data['streams']['Wave']['fs']
    baseline_start = fs*baseline_start
    baseline_stop = fs*baseline_stop
    all_data = tdt.epoc_filter(tdt_data, 'mark').streams.Wave['filtered']
    animal_block = tdt_data.info.blockname
    
    
    plot_zscores(all_data, chs, baseline_start, baseline_stop, fs, animal_block)
    #establishes all of the necessary variables 
    #plots the mean z-scored response and the 

def all_data_one_channel(data_for_trial_list, channel, tmax = 6000):
    
    """
    Takes in the data as it comes from the tdt file and returns an array that contains all of the data 
    for one channel
    
    Inputs: 
        data for trial list(list)
            list with data with an array for each trial that contains subarrays for each channel
        channel(int)
             channel you want data for 
    Returns: 
            array with dimensions (60, tmax) that contains the data for one channel"""
    
    data_for_channel = []
    channel = channel - 1 #subtract 1 because the array is 0 indexed but the channels are not 
    for trial in range(len(data_for_trial_list)):
        one_trial = data_for_trial_list[trial][channel]
        data_for_channel.append(one_trial[:tmax])
       
    return np.array(data_for_channel)

### gets the data from the time period before the stimulus in order to calculate baseline statistics
def stimulus_onset_one_channel(data_for_trial_list, channel, onset_start, onset_stop):
    
    """
    Takes in the data for trials as a list and returns only the data during the onset period for all trials
    
    Inputs: 
        data for trial list(list)
            list with data with an array for each trial that contains subarrays for each channel
        channel(int)
             channel you want data for 
        onset_start (int)
            starting period of the stimulus onset
        onset_stop
            right before stimulus occurs 
            
    Returns: 
            array with the data during the onset period for all trials
            
            """
    
    onset_for_channel = []
    channel = channel - 1 #subtract 1 because the array is 0 indexed but the channels are not 
    onset_start = int(onset_start)
    onset_stop = int(onset_stop)
    
    for trial in range(len(data_for_trial_list)):
        one_trial = data_for_trial_list[trial][channel]
        onset_for_channel.append(one_trial[onset_start:onset_stop])
        
    return np.array(onset_for_channel)

###returns the data for one channel z-scored from baseline
def zscore_from_baseline(data_for_trial_list, channel, onset_start, onset_stop):
    """
    Returns the data zscored from baseline 
    
    Inputs:
        data for trial list(list)
            list with data with an array for each trial that contains subarrays for each channel
        channel(int)
             channel you want data for 
        onset_start (int)
            starting period of the stimulus onset
        onset_stop
            right before stimulus occurs 
    """
    onset_data = stimulus_onset_one_channel(data_for_trial_list, channel, onset_start, onset_stop)
    average_onset = np.average(onset_data)
    standard_dev = np.std(onset_data)
    all_data_for_channel = all_data_one_channel(data_for_trial_list, channel) #returns data for one channel for all trials
    zscored = (all_data_for_channel - average_onset)/(standard_dev) 
    return zscored

#get average zscore
def get_average_zscore(data_for_trial_list, channel, onset_start, onset_stop, tmax = 6000):
    
        """
        Returns average data zscored from baseline 
    
        Inputs:
            data for trial list(list)
                list with data with an array for each trial that contains subarrays for each channel
            channel(int)
                channel you want data for 
            onset_start (int)
                starting period of the stimulus onset
            onset_stop
                right before stimulus occurs 
        """
        all_data = all_data_one_channel(data_for_trial_list, channel)
        data_for_channel = zscore_from_baseline(data_for_trial_list, channel, onset_start, onset_stop)
        different_format = np.transpose(data_for_channel) #array shape(6000, 60)
        mean_trial = np.mean(different_format, axis = 1)
        return mean_trial

#plot, might change when vanessa uploads her version
def plot_zscores(data_for_trial_list, chs, onset_start, onset_stop, fs, animal_block,
                 tmax = 6000, height = 8, width = 16): 
    """
    Plots the data for an ecog grid, update when vanessa
    """
    for channel in np.arange(len(chs)):
        if channel >= height*width:
            return
        plt.subplot(height, width, channel + 1)
        
        correct_channel = chs[channel]
        data_for_channel_zscored = zscore_from_baseline(data_for_trial_list, correct_channel, onset_start, onset_stop)
        average_for_channel = get_average_zscore(data_for_trial_list, correct_channel, onset_start, onset_stop)
        
        plt.plot(average_for_channel, color = 'k', linewidth= 2, zorder = 9)
        plt.title('Channel ' + str(correct_channel), fontsize= 5)
        plt.vlines(.25*fs, ymin = min(data_for_channel_zscored.flatten()), ymax = max(data_for_channel_zscored.flatten()), color = 'darksalmon', zorder = 10)
        for i in np.arange(len(data_for_channel_zscored)):
            plt.plot(data_for_channel_zscored[i], color = (.85,.85,.85), linewidth = 0.5)
        
        plt.xlim(2000, 6000)
        plt.xticks(fontsize=10)
        plt.yticks(fontsize=10)
        
    plt.suptitle('{} Z-Scores Across Channels'.format(animal_block), fontsize=60, y=1)

#%%
data_directory = "/Users/macproizzy/Desktop/Raw_signal/RVG02_B01/"
chs = [
       81, 83, 85, 87, 89, 91, 93, 95, 97, 105, 98, 106, 114, 122, 113, 121,
       82, 84, 86, 88, 90, 92, 94, 96, 99, 107, 100, 108, 116, 124, 115, 123,
       66, 68, 70, 72, 74, 76, 78, 80, 101, 109, 102, 110, 118, 126, 117, 125,
       65, 67, 69, 71, 73, 75, 77, 79, 103, 111, 104, 112, 120, 128, 119, 127,
       63, 61, 59, 57, 55, 53, 51, 49, 25, 17, 26, 18, 10, 2, 9, 1,
       64, 62, 60, 58, 56, 54, 52, 50, 27, 19, 28, 20, 12, 4, 11, 3,
       48, 46, 44, 42, 40, 38, 36, 34, 29, 21, 30, 22, 14, 6, 13, 5,
       47, 45, 43, 41, 39, 37, 35, 33, 31, 23, 32, 24, 16, 8, 15, 7
       ]

plot_all(data_directory, chs)









