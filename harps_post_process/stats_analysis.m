 clear all; close all; clc;
%Current /Users/RayH/Documents/School/Research/HARPS/COHRINTCode/post-process-output25-Apr-2021
%% Get directory
% direct = input("Enter Bag Directory: ",'s');
direct = "/Users/RayH/Documents/School/Research/HARPS/COHRINTCode/post-process-output18-Jun-2021";
robot_direct = '/Users/RayH/Documents/School/Research/HARPS/COHRINTCode/robot-post-process-output16-Jun-2021';
plot_things = 1;
%% Read in all .csv files from specified directory
%Subject Data
files = dir(direct+"/*.mat");
n = length(files);

r_files = dir(robot_direct+"/*.mat");
r_n = length(r_files);

%Matrix pre-allocation
subperformance = zeros(n,1);
camviews = zeros(n,1);
numsketch = zeros(n,1);
acc_compass = zeros(n,4);
acc_softmax = zeros(n,4);
user_trust = zeros(n,1);
subject_capture_rate = zeros(36,8);
subject_accuracy_c = zeros(36,3);
subject_accuracy_s = zeros(36,3);
subject_trust = zeros(36,3);
subject_availability = zeros(36,3);
availability = [];

both_perf = [];
push_perf = [];
pull_perf = [];

both_trust = [];
push_trust = [];
pull_trust = [];

both_work = [];
push_work = [];
pull_work = [];

%Workload
both_work1 = 0;
both_work2 = 0;
both_work3 = 0;
pull_work1 = 0;
pull_work2 = 0;
pull_work3 = 0;
push_work1 = 0;
push_work2 = 0;
push_work3 = 0;

%Loop through all robot data
r_performance = zeros(r_n,1);
for r = 1:r_n
   active = r_files(r).name;
   load(robot_direct+"/"+active)
%    if isnan(capture_time)
%        capture_time = 0
%    else 
%        capture_time = 1
%    end
   r_performance(r) = capture_time;
end


%Loop through all subject data
for i = 1:n 
    %Active file
    active = files(i).name;
    load(direct+"/"+active)
    
    %Capture time determination
    if isnan(capture_time) || capture_time>900 %Target not captured
        %Should non capture runs be put in seperate matrix? 
        t = NaN;
        subperformance(i) = t; %Needs to be changed to account for target not captured.
        capture_time = t;
%     elseif capture_time<120
%         subperformance(i) = NaN;
%         capture_time_extra = capture_time;
%         capture_time = NaN;
    else
%         capture_time = 1;
        subperformance(i) = capture_time(1);
    end
    camviews(i) = num_views;
    if num_views/capture_time>1
        st = 1;
    end
    numsketch(i) = length(sketches);
    
    %Catch errors with timing contributing to accuracy problems
    if contains(active,"Pull") || contains(active,"Both")
        if pulls(1).ResponseTime<0 %Negative response time is bad
            acc_compass(i,1) = NaN;
            acc_softmax(i,1) = NaN;
        else
            acc_compass(i,1) = total_accuracy_compass;
            acc_softmax(i,1) = total_accuracy_softmax;
        end
    elseif pushes(1).Time==pushes(end).Time %Same push time is bad
        acc_compass(i,1) = NaN;
        acc_softmax(i,1) = NaN;
    else
        acc_compass(i,1) = total_accuracy_compass;
        acc_softmax(i,1) = total_accuracy_softmax;
    end
    user_trust(i) = subject_survey_trust;
    
    %Sorting by run type
    if contains(active,"Both")
        both_perf = [both_perf,capture_time(1)];
        avail = length(pulls)/(length(pulls_unanswered)+length(pulls));
%         availability = [availability, [capture_time; avail; length(sketches)]];
        both_trust = [both_trust,subject_survey_trust];
        both_work = [both_work,subject_survey_workload];
        acc_softmax(i,2) = length(pushes)+length(pulls);
        acc_compass(i,2) = length(pushes)+length(pulls);
        switch subject_survey_data.Ranking
            case 1
                both_work1 = both_work1+1;
            case 2
                both_work2 = both_work2+1;
            case 3
                both_work3 = both_work3+1;
        end
        
        if isnan(str2double(active(9)))
            subject_availability(str2num(active(8)),2) = avail;
        else
            subject_availability(str2num(active(8:9)),2) = avail;
        end
        %total_nans = sum(isnan(both_perf))
        %subject_survey_data{1,end}
        
    elseif contains(active,"Pull")
        pull_perf = [pull_perf,capture_time(1)];
        avail = length(pulls)/(length(pulls_unanswered)+length(pulls));
        availability = [availability, [capture_time; avail; length(sketches)]];
        pull_trust = [pull_trust,subject_survey_trust];
        pull_work = [pull_work,subject_survey_workload];
        acc_softmax(i,2) = length(pulls);
        acc_compass(i,2) = length(pulls);
        
        if isnan(str2double(active(9)))
            subject_availability(str2num(active(8)),1) = avail;
        else
            subject_availability(str2num(active(8:9)),1) = avail;
        end
        
        switch subject_survey_data.Ranking
            case 1
                pull_work1 = pull_work1+1;
            case 2
                pull_work2 = pull_work2+1;
            case 3
                pull_work3 = pull_work3+1;
        end
        
    elseif contains(active,"Push")
        push_perf = [push_perf,capture_time(1)];
        push_trust = [push_trust,subject_survey_trust];
        push_work = [push_work,subject_survey_workload];
        acc_softmax(i,2) = length(pushes);
        acc_compass(i,2) = length(pushes);
        switch subject_survey_data.Ranking
            case 1
                push_work1 = push_work1+1;
            case 2
                push_work2 = push_work2+1;
            case 3
                push_work3 = push_work3+1;
        end
    else
        error("Rosbag file improperly named")
    end
    
    %Subject Capture Rate
    %Find index number
    if isnan(str2double(active(9)))
        cur = subject_capture_rate(str2double(active(8)),:);
        acc_softmax(i,3) = str2double(active(8));
        acc_compass(i,3) = str2double(active(8));
        switch active(10:13)
            case "Pull"
                c = 1;
            case "Push"
                c = 2;
            case "Both"
                c = 3;
        end
    else
        cur = subject_capture_rate(str2double(active(8:9)),:);
        acc_compass(i,3) = str2double(active(8:9));
        acc_softmax(i,3) = str2double(active(8:9));
        switch active(11:14)
            case "Pull"
                c = 1;
            case "Push"
                c = 2;
            case "Both"
                c = 3;
        end

    end
    %Assign simulation mode type
    acc_softmax(i,4) = c;
    acc_compass(i,4) = c;
    %Find simulation number
    for in= 1:3
       if cur(in)== 0 
            ind = in;
            break
       end
    end
    if isnan(str2double(active(9)))
        subject_capture_rate(str2double(active(8)),ind) = capture_time;
        subject_accuracy_s(str2double(active(8)),ind) = total_accuracy_softmax;
        subject_accuracy_c(str2double(active(8)),ind) = total_accuracy_compass;
        subject_trust(str2double(active(8)),ind) = subject_survey_trust;
    else
        subject_capture_rate(str2double(active(8:9)),ind) = capture_time;
        subject_trust(str2double(active(8:9)),ind) = subject_survey_trust;
        subject_accuracy_s(str2double(active(8:9)),ind) = total_accuracy_softmax;
        subject_accuracy_c(str2double(active(8:9)),ind) = total_accuracy_compass;
    end
     
end

%Subject Capture Rate
for r=1:36
   subject_capture_rate(r,4) = nanmean(subject_capture_rate(r,1:3)); 
   subject_capture_rate(r,5) = std_mean(subject_capture_rate(r,1:3));
   subject_capture_rate(r,6) = nanmean(subject_accuracy_s(r,:));
   subject_capture_rate(r,7) = nanmean(subject_accuracy_c(r,:));
   subject_capture_rate(r,8) = nanmean(subject_trust(r,:));
   subject_availability(r,3) = nanmean(subject_availability(r,1:2));
end

%Sorting capture rate
[val idx]=sort(subject_capture_rate(:,4));
sorted_capture = [subject_capture_rate(idx,1:3) val subject_capture_rate(idx,5)];

%Create table
variable_names = {'Number of Sketches','Camera Views','Performance'};
perf_table = table(numsketch,camviews,subperformance,'VariableNames',variable_names);
%ttest
%% Start statistics
% fitlm(numsketch,subperformance)
% fitlm(perf_table)
%Find means and std of performance data

    %Standards
    axis_size = 16;
    title_size = 19;
    marker_size = 40;
    both_color =   [0 0.13 0.8];
    push_color = [0.14 0.65 0.149];
    robot_color = [0.8 0 0.27];
    pull_color = [1 0.73 0.1];
    
%% Hypothesis 1 - Input type correlates to performance
%Time to capture
    perf_bar_fig = figure;
    names = categorical({'Both','Passive','Active','Robot Only'});
    names = reordercats(names,{'Both','Passive','Active','Robot Only'});
    mean_data = [nanmean(both_perf); nanmean(push_perf);nanmean(pull_perf);nanmean(r_performance)];
    mean_low = [std_mean(both_perf);std_mean(push_perf);std_mean(pull_perf);std_mean(r_performance)];
    mean_high = [std_mean(both_perf);std_mean(push_perf);std_mean(pull_perf);std_mean(r_performance)];
    b = bar(names,mean_data);
    b.FaceColor = 'flat';
    b.CData(1,:) = both_color;
    b.CData(2,:) = push_color;
    b.CData(3,:) = pull_color;
    b.CData(4,:) = robot_color;
    perf_bar_fig.CurrentAxes.FontSize = axis_size;
    perf_bar_fig.CurrentAxes.FontName = 'Trebuchet';
    hold on
    grid on
    er = errorbar(names,mean_data,mean_low,mean_high,'CapSize',70,'LineWidth',2);  
    er.Color = [0 0 0];  
    er.LineStyle = 'none';  
    ylabel("Time to Capture (s)",'FontName','Trebuchet','FontSize',axis_size)
    title("Time to Capture Performance",'FontName','Trebuchet','FontSize',title_size)
    saveas(perf_bar_fig,'/Users/RayH/Documents/School/Research/HARPS/COHRINTCode/Data_Plots/Capture_Perf.png');
    
    %Capture rate
    perf_bar_fig = figure;
    names = categorical({'Both','Passive','Active','Robot Only'});
    names = reordercats(names,{'Both','Passive','Active','Robot Only'});
    ratio_data = [capture_ratio(both_perf);capture_ratio(push_perf);capture_ratio(pull_perf);capture_ratio(r_performance)];
%     ratio_data = [1,0.8,0.7]
    b = bar(names,ratio_data);
    grid on
    b.FaceColor = 'flat';
    b.CData(1,:) = both_color;
    b.CData(2,:) = push_color;
    b.CData(3,:) = pull_color;
    b.CData(4,:) = robot_color;
    perf_bar_fig.CurrentAxes.FontSize = axis_size;
    perf_bar_fig.CurrentAxes.FontName = 'Trebuchet';
    hold on
    ylabel("Capture Ratio",'FontName','Trebuchet','FontSize',axis_size)
    title("Capture Ratio",'FontName','Trebuchet','FontSize',title_size)
    saveas(perf_bar_fig,'/Users/RayH/Documents/School/Research/HARPS/COHRINTCode/Data_Plots/Capture_Ratio.png')
    
    %Subject specific accuracy
            sub_cap_fig = figure;
    hold on
    grid on
    b = bar(1:36,subject_capture_rate(:,4));
    b.FaceColor = 'flat';
        
    for s = 1:length(subject_capture_rate(:,1))
       r = capture_ratio(subject_capture_rate(s,1:3));
       switch r
           case 1
               b.CData(s,:) = push_color;
           case 2/3
               b.CData(s,:) = pull_color;
           case 1/3
               b.CData(s,:) = robot_color;
       end               
    end
    ylabel("Mean Time to Capture (s)",'FontName','Trebuchet','FontSize',axis_size)
    xlabel("Subject Number",'FontName','Trebuchet','FontSize',axis_size)
    title("Capture Time per Subject",'FontName','Trebuchet','FontSize',title_size)
    er = errorbar(1:36,subject_capture_rate(:,4),subject_capture_rate(:,5),subject_capture_rate(:,5),'LineWidth',1);  
    er.Color = [0 0 0];  
    er.LineStyle = 'none';  
    
    sub_cap_fig.CurrentAxes.FontSize = axis_size;
    sub_cap_fig.CurrentAxes.FontName = 'Trebuchet';
    saveas(sub_cap_fig,'/Users/RayH/Documents/School/Research/HARPS/COHRINTCode/Data_Plots/Subject_Performance.png')
    
    
  

%% Sketch Correlation Hypothesis 2- Favorable Frequency of Human Input
%      sketch_rate = numsketch./subperformance;
     sketch_rate = numsketch;
    p_sketch = fitlm(sketch_rate,subperformance);
    sketch_fig = figure;
    scatter(subperformance,sketch_rate,marker_size,'blue','filled')
%     text(500,0.06,['p value= ' num2str(p_sketch.Coefficients.pValue(2)) ', R^2= ' num2str(p_sketch.Rsquared.Adjusted)],'FontSize',12);
    ylabel("Number of Sketches",'FontName','Trebuchet','FontSize',axis_size)
    xlabel("Time to Capture (s)",'FontName','Trebuchet','FontSize',axis_size)
    title("Optimal Sketch Correlation",'FontName','Trebuchet','FontSize',title_size)
    grid on
        sketch_fig.CurrentAxes.FontSize = axis_size;
    sketch_fig.CurrentAxes.FontName = 'Trebuchet';
    saveas(sketch_fig,'/Users/RayH/Documents/School/Research/HARPS/COHRINTCode/Data_Plots/Sketch_Input.png')
    
%% Availability and accuracy Hypothesis 3- Availability and accuracy leads to success
 % Accuracy
    p_soft = fitlm(subperformance,acc_softmax(:,1));
    soft_acc_fig = figure;
    hold on
%     scatter(subperformance,acc_softmax(:,1),acc_softmax(:,2)*2,'blue','filled')
    for s = 1:length(acc_softmax(:,1))
       r = acc_softmax(s,4);
       switch r
           case 2
               scatter(subperformance(s),acc_softmax(s,1),acc_softmax(s,2)*2,push_color,'filled')
           case 1
               scatter(subperformance(s),acc_softmax(s,1),acc_softmax(s,2)*2,pull_color,'filled')
           case 3
               scatter(subperformance(s),acc_softmax(s,1),acc_softmax(s,2)*2,both_color,'filled')
       end               
    end
    text(650,0.25,['p value= ' num2str(p_soft.Coefficients.pValue(2)) ', R^2= ' num2str(p_sketch.Rsquared.Adjusted)],'FontSize',12);
    xlabel("Time to Capture (s)",'FontName','Trebuchet','FontSize',axis_size)
    ylabel("User Accuracy",'FontName','Trebuchet','FontSize',axis_size)
    title("Softmax Accuracy vs. Performance",'FontName','Trebuchet','FontSize',title_size)
    grid on
    soft_acc_fig.CurrentAxes.FontSize = axis_size;
    soft_acc_fig.CurrentAxes.FontName = 'Trebuchet';
    for l=1:length(acc_softmax(:,3))
        text(subperformance(l),acc_softmax(l,1)+0.02,string(acc_softmax(l,3)))
    end
    saveas(gcf,'/Users/RayH/Documents/School/Research/HARPS/COHRINTCode/Data_Plots/SoftmaxAcc_Performance.png')
    
    p_compass = fitlm(subperformance,acc_compass(:,1));
    comp_acc_fig = figure;
    scatter(subperformance,acc_compass(:,1),acc_compass(:,2)*2,'magenta','filled')
    text(650,0.2,['p value= ' num2str(p_compass.Coefficients.pValue(2)) ', R^2= ' num2str(p_sketch.Rsquared.Adjusted)],'FontSize',12);
    xlabel("Time to Capture (s)",'FontName','Trebuchet','FontSize',axis_size)
    ylabel("User Accuracy",'FontName','Trebuchet','FontSize',axis_size)
    title("Compass Accuracy vs. Performance",'FontName','Trebuchet','FontSize',title_size)
    grid on
    comp_acc_fig.CurrentAxes.FontSize = axis_size;
    comp_acc_fig.CurrentAxes.FontName = 'Trebuchet';
    for l=1:length(acc_softmax(:,3))
        text(subperformance(l),acc_compass(l,1)+0.02,string(acc_compass(l,3)))
    end
    saveas(gcf,'/Users/RayH/Documents/School/Research/HARPS/COHRINTCode/Data_Plots/CompassAcc_Performance.png')
    
    %User specific accuracy - Softmax
    p_softmax_user = fitlm(subject_capture_rate(:,4),subject_capture_rate(:,6));
    comp_acc_user_fig = figure;
    hold on
    grid on
    for s = 1:length(subject_capture_rate(:,1))
       r = capture_ratio(subject_capture_rate(s,1:3));
       switch r
           case 1
               scatter(subject_capture_rate(s,4),subject_capture_rate(s,6),marker_size,push_color,'filled')
               text(subject_capture_rate(s,4),subject_capture_rate(s,6)+0.02,string(s))
           case 2/3
               scatter(subject_capture_rate(s,4),subject_capture_rate(s,6),marker_size,pull_color,'filled')
               text(subject_capture_rate(s,4),subject_capture_rate(s,6)+0.02,string(s))
           case 1/3
               scatter(subject_capture_rate(s,4),subject_capture_rate(s,6),marker_size,robot_color,'filled')
               text(subject_capture_rate(s,4),subject_capture_rate(s,6)+0.02,string(s))
       end               
    end
    text(400,0.9,['p value= ' num2str(p_softmax_user.Coefficients.pValue(2)) ', R^2= ' num2str(p_sketch.Rsquared.Adjusted)],'FontSize',12);
    xlabel("Time to Capture (s)",'FontName','Trebuchet','FontSize',axis_size)
    ylabel("User Accuracy",'FontName','Trebuchet','FontSize',axis_size)
    title("Subject Softmax Accuracy and Performance",'FontName','Trebuchet','FontSize',title_size)
    comp_acc_user_fig.CurrentAxes.FontSize = axis_size;
    comp_acc_user_fig.CurrentAxes.FontName = 'Trebuchet';
    saveas(gcf,'/Users/RayH/Documents/School/Research/HARPS/COHRINTCode/Data_Plots/Subject_SoftmaxAcc_Performance.png')
    
    %User specific accuracy - Compass
    p_compass_user = fitlm(subject_capture_rate(s,4),subject_capture_rate(s,7));
    comp_acc_user_fig = figure;
    hold on
    grid on
    for s = 1:length(subject_capture_rate(:,1))
       r = capture_ratio(subject_capture_rate(s,1:3));
       switch r
           case 1
               scatter(subject_capture_rate(s,4),subject_capture_rate(s,7),marker_size,push_color,'filled')
               text(subject_capture_rate(s,4),subject_capture_rate(s,7)+0.02,string(s))
           case 2/3
               scatter(subject_capture_rate(s,4),subject_capture_rate(s,7),marker_size,pull_color,'filled')
               text(subject_capture_rate(s,4),subject_capture_rate(s,7)+0.02,string(s))
           case 1/3
               scatter(subject_capture_rate(s,4),subject_capture_rate(s,7),marker_size,robot_color,'filled')
               text(subject_capture_rate(s,4),subject_capture_rate(s,7)+0.02,string(s))
       end               
    end
    text(500,0.9,['p value= ' num2str(p_compass_user.Coefficients.pValue(2)) ', R^2= ' num2str(p_sketch.Rsquared.Adjusted)],'FontSize',12);
    xlabel("Time to Capture (s)",'FontName','Trebuchet','FontSize',axis_size)
    ylabel("User Accuracy",'FontName','Trebuchet','FontSize',axis_size)
    title("Subject Compass Accuracy and Performance",'FontName','Trebuchet','FontSize',title_size)
    comp_acc_user_fig.CurrentAxes.FontSize = axis_size;
    comp_acc_user_fig.CurrentAxes.FontName = 'Trebuchet';
    saveas(gcf,'/Users/RayH/Documents/School/Research/HARPS/COHRINTCode/Data_Plots/Subject_CompassAcc_Performance.png')
    
    % Availability
    p_available = fitlm(availability(1,:),availability(2,:));
    avilability_fig = figure;
    scatter(availability(1,:),availability(2,:),availability(3,:)*3,'blue','filled')
    text(600,0.25,['p value=' num2str(p_available.Coefficients.pValue(2)) ', R^2 = ' num2str(p_available.Rsquared.Adjusted)],'FontSize',12)
    xlabel("Time to Capture (s)",'FontName','Trebuchet','FontSize',axis_size)
    ylabel("User Availability (Answered/Total Questions)",'FontName','Trebuchet','FontSize',axis_size)
    title("Subject Availability vs. Performance",'FontName','Trebuchet','FontSize',title_size)
    grid on
        avilability_fig.CurrentAxes.FontSize = axis_size;
    avilability_fig.CurrentAxes.FontName = 'Trebuchet';
    saveas(avilability_fig,'/Users/RayH/Documents/School/Research/HARPS/COHRINTCode/Data_Plots/Availability_v_Performance.png')
    
    availability_sketch_fig = figure;
    scatter(subject_capture_rate(:,4),subject_availability(:,3),marker_size,'blue','filled')
    text(600,0.25,['p value=' num2str(p_available.Coefficients.pValue(2)) ', R^2 = ' num2str(p_available.Rsquared.Adjusted)],'FontSize',12)
    xlabel("Time to Capture (s)",'FontName','Trebuchet','FontSize',axis_size)
    ylabel("Subject Availability (Answered/Total Questions)",'FontName','Trebuchet','FontSize',axis_size)
    title("Subject Availability vs. Performance",'FontName','Trebuchet','FontSize',title_size)
    availability_sketch_fig.CurrentAxes.FontSize = axis_size;
    availability_sketch_fig.CurrentAxes.FontName = 'Trebuchet';
    grid on
    
if plot_things
%% Views Correlation Hypothesis 4 - Viewpoints to accuracy?
    cam_time_ratio = camviews./subperformance;
    p_cam = fitlm(cam_time_ratio,subperformance);
    views_fig = figure;
    scatter(subperformance,cam_time_ratio,marker_size,'blue','filled')
    text(500,0.3,['p value=' num2str(p_cam.Coefficients.pValue(2)) ', R^2= ' num2str(p_cam.Rsquared.Adjusted)],'FontSize',12);
    ylabel("Number of Camera Views per Second",'FontName','Trebuchet','FontSize',axis_size)
    xlabel("Time to Capture (s)",'FontName','Trebuchet','FontSize',axis_size)
    title("Views Correlation to Performance",'FontName','Trebuchet','FontSize',title_size)
    views_fig.CurrentAxes.FontSize = axis_size;
    views_fig.CurrentAxes.FontName = 'Trebuchet';
    grid on
    saveas(gcf,'/Users/RayH/Documents/School/Research/HARPS/COHRINTCode/Data_Plots/Views_v_Performance.png')
    
    cam_time_ratio = camviews./subperformance;
    p_cam = fitlm(cam_time_ratio,subperformance);
    views_fig = figure;
    scatter(cam_time_ratio,acc_softmax(:,1),marker_size,'blue','filled')
    text(500,0.3,['p value=' num2str(p_cam.Coefficients.pValue(2)) ', R^2= ' num2str(p_cam.Rsquared.Adjusted)],'FontSize',12);
    ylabel("User Accuracy (Softmax)",'FontName','Trebuchet','FontSize',axis_size)
    xlabel("Camera Views per Second",'FontName','Trebuchet','FontSize',axis_size)
    title("Views Correlation to Performance",'FontName','Trebuchet','FontSize',title_size)
    views_fig.CurrentAxes.FontSize = axis_size;
    views_fig.CurrentAxes.FontName = 'Trebuchet';
    grid on
    saveas(gcf,'/Users/RayH/Documents/School/Research/HARPS/COHRINTCode/Data_Plots/Views_v_Accuracy.png')

%% Workload Hypothesis 5 - Higher workload across incremental scenarios and accuracy
    work_bar_fig = figure;
    names = categorical({'Both','Passive','Active'});
    names = reordercats(names,{'Both','Passive','Active'});
    mean_data = [nanmean(both_work); nanmean(push_work);nanmean(pull_work)];
    mean_low = [std_mean(both_work);std_mean(push_work);std_mean(pull_work)];
    mean_high = [std_mean(both_work);std_mean(push_work);std_mean(pull_work)];
    b = bar(names,mean_data);
    b.FaceColor = 'flat';
    b.CData(1,:) = both_color;
    b.CData(2,:) = push_color;
    b.CData(3,:) = pull_color;
    work_bar_fig.CurrentAxes.FontSize = axis_size;
    work_bar_fig.CurrentAxes.FontName = 'Trebuchet';
    hold on
    grid on
    er = errorbar(names,mean_data,mean_low,mean_high,'CapSize',70,'LineWidth',2);  
    er.Color = [0 0 0];  
    er.LineStyle = 'none';  
    ylabel("User Workload",'FontName','Trebuchet','FontSize',axis_size)
    title("Total User Workload")
    saveas(gcf,'/Users/RayH/Documents/School/Research/HARPS/COHRINTCode/Data_Plots/Workload.png')
    
    work_rank_fig = figure;
    names = categorical({'Both','Passive','Active'});
    names = reordercats(names,{'Both','Passive','Active'});
    mean_data = [both_work1 both_work2 both_work3;push_work1 push_work2 push_work3;pull_work1 pull_work2 pull_work3];
    b = bar(names,mean_data,'stacked');
%     b(:).FaceColor = 'flat';
    b(1).FaceColor = both_color;
     b(2).FaceColor = push_color;
     b(3).FaceColor = pull_color;
    work_rank_fig.CurrentAxes.FontSize = axis_size;
    work_rank_fig.CurrentAxes.FontName = 'Trebuchet';
    hold on
    grid on
    ylabel("Workload Rankings",'FontName','Trebuchet','FontSize',axis_size)
    title("Workload Ranking")
    legend('Rank 1','Rank 2','Rank 3')
    saveas(gcf,'/Users/RayH/Documents/School/Research/HARPS/COHRINTCode/Data_Plots/Workload_Ranking.png')


%% Trust Hypothesis 6 - Higher trust across scenarios and accuracy

    trust_bar_fig = figure;
    names = categorical({'Both','Passive','Active'});
    names = reordercats(names,{'Both','Passive','Active'});
    mean_data = [nanmean(both_trust); nanmean(push_trust);nanmean(pull_trust)];
    mean_low = [std_mean(both_trust);std_mean(push_trust);std_mean(pull_trust)];
    mean_high = [std_mean(both_trust);std_mean(push_trust);std_mean(pull_trust)];
    b = bar(names,mean_data);
    b.FaceColor = 'flat';
    b.CData(1,:) = both_color;
    b.CData(2,:) = push_color;
    b.CData(3,:) = pull_color;
    trust_bar_fig.CurrentAxes.FontSize = axis_size;
    trust_bar_fig.CurrentAxes.FontName = 'Trebuchet';
    hold on
    grid on
    er = errorbar(names,mean_data,mean_low,mean_high,'CapSize',70,'LineWidth',2);  
    er.Color = [0 0 0];  
    er.LineStyle = 'none';  
    ylabel("User Trust",'FontName','Trebuchet','FontSize',axis_size)
    title("Total User Trust")
    saveas(gcf,'/Users/RayH/Documents/School/Research/HARPS/COHRINTCode/Data_Plots/Trust_Compare.png')
    
    %Regression Calc
    p_trust = fitlm(user_trust,subperformance);
    
    trust_perf_fig = figure;
    scatter(subperformance,user_trust,marker_size,'blue','filled')
    text(500,6,['p value= ' num2str(p_trust.Coefficients.pValue(2)) ',  R^2= ' num2str(p_trust.Rsquared.Adjusted)],'FontSize',12);
    xlabel("Time to Capture (s)",'FontName','Trebuchet','FontSize',axis_size)
    ylabel("User Trust",'FontName','Trebuchet','FontSize',axis_size)
    title("Trust vs. Performance",'FontName','Trebuchet','FontSize',title_size)
    trust_perf_fig.CurrentAxes.FontSize = axis_size;
    trust_perf_fig.CurrentAxes.FontName = 'Trebuchet';
    grid on
    saveas(gcf,'/Users/RayH/Documents/School/Research/HARPS/COHRINTCode/Data_Plots/Trust_v_Performance.png')
    
    
    trust_acc_fig = figure;
    scatter(acc_softmax(:,1),user_trust,marker_size,'blue','filled')
    xlabel("User Accuracy",'FontName','Trebuchet','FontSize',axis_size)
    ylabel("User Trust",'FontName','Trebuchet','FontSize',axis_size)
    title("Trust vs. Accuracy",'FontName','Trebuchet','FontSize',title_size)
    trust_acc_fig.CurrentAxes.FontSize = axis_size;
    trust_acc_fig.CurrentAxes.FontName = 'Trebuchet';
    grid on
    saveas(gcf,'/Users/RayH/Documents/School/Research/HARPS/COHRINTCode/Data_Plots/Trust_v_Accuracy.png')
    
    %Mean User trust and accuracy
    trust_acc_subject_fig = figure;
    scatter(subject_capture_rate(:,6),subject_capture_rate(:,8),marker_size,'blue','filled')
    xlabel("User Mean Accuracy",'FontName','Trebuchet','FontSize',axis_size)
    ylabel("User Mean Trust",'FontName','Trebuchet','FontSize',axis_size)
    title("Trust vs. Accuracy",'FontName','Trebuchet','FontSize',title_size)
    trust_acc_subject_fig.CurrentAxes.FontSize = axis_size;
    trust_acc_subject_fig.CurrentAxes.FontName = 'Trebuchet';
    grid on
    saveas(gcf,'/Users/RayH/Documents/School/Research/HARPS/COHRINTCode/Data_Plots/Subject_Trust_v_Accuracy.png')
    

end

%% Regression Analysis

tbl = table(acc_compass(:,1),acc_softmax(:,1),cam_time_ratio,sketch_rate,subperformance);
tbl(1:5,:)
lm = fitlm(tbl)


%% 
function result = std_mean(data)
%Returns the standard error of the mean
    result = nanstd(data)/sqrt((length(data)-sum(isnan(data))));
end

function result = capture_ratio(data)
%Returns the ratio that the target was captured across all simulations
    t_nan = sum(isnan(data));
    if t_nan == 0
        result = 1;
    else
        result = (length(data)-t_nan)/length(data);
    end
end
