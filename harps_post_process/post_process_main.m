%% Post Process ROS bag Data Version 2
%{
Description: Converts raw csv data into a quantitative form for statistical
analysis. For use with HARPS ROS bags in csv form.

Input: Directory with test subject rosbag data

Output: .mat of ROS bag data, as well as time to capture target, number of
sketches drawn, subject response time, number of camera views observed, etc

Authors: Hunter Ray, Trevor Slack

Date Modified: 6/9/2021
%}
clear all; close all; clc;
tic
%% Find Data
files = dir(pwd);
dirFlags = [files.isdir];
% Extract only those that are directories.
subject_directories = files(dirFlags);


%% Read in all .csv files from specified directory
first = true;
f = waitbar(0,'Please wait...');
for i=1:length(subject_directories)
    if ~(strcmp(subject_directories(i).name,'.')) && ~(strcmp(subject_directories(i).name,'..'))
        waitbar((i-1)/length(subject_directories),f,"Analyzing "+subject_directories(i).name);
        if contains(subject_directories(i).name,'Subject')
            postProcessROSbag(subject_directories(i));
        end
    end  
end
toc
waitbar(1,f,'Finished!');
pause(1)
close(f)

