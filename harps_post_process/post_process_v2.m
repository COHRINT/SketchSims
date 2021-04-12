%% Post Process ROS bag Data Version 2
%{
Description: Converts raw csv data into a quantitative form for statistical
analysis. For use with HARPS ROS bags in csv form.

Input: Directory of csv files from a ROS bag

Output: .mat of ROS bag data, as well as time to capture target, number of
sketches drawn, subject response time, number of camera views observed, etc

Authors: Hunter Ray, Trevor Slack

Date Modified: 4/5/2021
%}
clear all; close all; clc;
%% Get directory
direct = input("Enter Bag Directory: ",'s');
%% Topics
capture_topic = '/Obs';
sketch_topic = '/Sketch';
pull_topic = '/Pull';
pull_answer_topic = '/PullAnswer';
camera_topic = '/Camera_Num';
target_topic = '/Target/car';
drone_topic = '/Drone1/pose';
time_conversion = 1e-9; % conversion from nanoseconds to seconds
sketch_offset = [-167;-780];
sensitivity = 0.5; % probability cuttoff for accuracy
answer_buffer = 1; %[s] surrounding target location data to evaluate
%% Read in all .csv files from specified directory
files = dir(direct+"\*.csv");
n = length(files);
bags = struct();
for i=1:n
    name = files(i).name;
    name = strrep(name,'_slash_','/');
    name = name(1:end-4);
    bags(i).topic = name;
    bags(i).data = readcell(files(i).folder+"\"+files(i).name);
end
%% Check what type of test
% pull, push, or both
pull = false;
push = false;
both = false;
if contains(files(1).folder,'both')
    both = true;
elseif contains(files(1).folder,'pull')
    pull = true;
elseif contains(files(1).folder,'push')
    push = true;
else
    error("Error: Improper Directory name. Make sure directory name contains either 'push', 'pull', or 'both'.")
end
%% Exctract Data
% get start time to zero other times
for i=1:n
    if strcmp(bags(i).topic,target_topic)
        target_time = cell2mat(bags(i).data(2:end,1));
        start_time = target_time(1);
        target_time = target_time - start_time;
        target_time = target_time.*time_conversion;
    end
end
% get rest of data
for i=1:n
    switch bags(i).topic
        case target_topic
            %target_time = cell2mat(bags(i).data(2:end,1));
            target_location = zeros(length(bags(i).data(2:end,1)),3);
            for j=2:length(target_location)+1
                target_location(j-1,:) = [cell2mat(bags(i).data(j,10)),cell2mat(bags(i).data(j,11)),cell2mat(bags(i).data(j,12))];
            end
            for j=1:3
                idx_nan = find(isnan(target_location(:,j)));
                target_location(idx_nan,:) = [];
                target_time(idx_nan) = [];
            end
%             tmp1 = target_location(~isnan(target_location(:,1)));
%             tmp2 = target_location(~isnan(target_location(:,2)));
%             tmp3 = target_location(~isnan(target_location(:,3)));
%             target_location = [tmp1,tmp2,tmp3];
            %start_time = target_time(1);
        % isolate condition data and its rosbag time data
        case capture_topic
            conditions = string(bags(i).data(2:end,2));
            conditions(:,:) = erase(conditions(:,:),'"');
            condition_times = cell2mat(bags(i).data(2:end,1))-start_time;
            condition_times = condition_times.*time_conversion;
            % get time to capture
            idx_condition = find(conditions=='Capture',1);
            capture_time = condition_times(idx_condition);
        % number of sketches
        case sketch_topic
            num_sketch = length(bags(i).data(2:end,1));
            sketch_time = cell2mat(bags(i).data(2:end,1))-start_time;
            sketch_time = sketch_time.*time_conversion;
            % sketch name
            sketch_name = string(bags(i).data(2:end,15));
            sketch_name = erase(sketch_name,'"');
            for k=1:num_sketch
                % locations of sketches
                for j=3:3:12
                    p = bags(i).data(k+1,:);
                    sketch_points = cell2mat([p(3),p(6),p(9),p(12);p(4),p(7),p(10),p(13)])+sketch_offset;
                end
                % area of sketch
                sketch_area = polyarea(sketch_points(1,:),sketch_points(2,:));
                sketches(k) = sketchCreate(char(sketch_name(k)),sketch_points,sketch_time(k),sketch_area);
            end  
        % subject response time
        case pull_topic
            if pull || both
                pull_time = cell2mat(bags(i).data(2:end,1))-start_time;
                pull_time = pull_time.*time_conversion;
                pull_question = string(bags(i).data(2:end,2));
                pull_counter = cell2mat(bags(i).data(2:end,3));
            end
        case pull_answer_topic
            if pull || both
                pull_answer_time = cell2mat(bags(i).data(2:end,1))-start_time;
                pull_answer_time = pull_answer_time.*time_conversion;
                pull_answer_response = cell2mat(bags(i).data(2:end,2));
                pull_answer_counter = cell2mat(bags(i).data(2:end,3));
            end
        % number of camera views observed
        case camera_topic
            camera_time = cell2mat(bags(i).data(2:end,1))-start_time;
            camera_time = camera_time.*time_conversion;
            camera_number = cell2mat(bags(i).data(2:end,2));
            % remove #6 as it is the drone camera
            camera_number_adj = camera_number(find(camera_number~=6));
            num_views = length(unique(camera_number_adj));
            %num_camera_switches = length(camera_number);
        case drone_topic
            drone_time = cell2mat(bags(i).data(2:end,1))-start_time;
            drone_time = drone_time.*time_conversion;
            drone_location = zeros(length(bags(i).data(2:end,1)),3);
            for j=2:length(drone_location)+1
                drone_location(j-1,:) = [cell2mat(bags(i).data(j,10)),cell2mat(bags(i).data(j,11)),cell2mat(bags(i).data(j,12))];
            end
        otherwise
            fprintf("Unused topic: %s\n",bags(i).topic)
            continue
    end
end

%% Response Time
if pull || both
    % response time for each answered question
    response_time = zeros(length(pull_answer_counter),1);
    for i=1:length(pull_answer_counter)
        response_time(i) = pull_answer_time(i) - pull_time(pull_answer_counter(i)+1);
    end
    
end

%% Sketch Accuracy

% if pull, find target location when question is answered
if pull || both
    % get only answered questions
    for i=1:length(pull_answer_counter)
        pull_question_answered(i) = pull_question(pull_answer_counter(i)+1);
    end
    
    % get sketches for answered question
    for i=1:length(pull_question_answered)
        pull_question_sketch_names(i) = extractAfter(pull_question_answered(i),'of ');
        pull_question_sketch_names(i) = erase(pull_question_sketch_names(i),'"');
    end
    
    % get question direction
    for i=1:length(pull_question_answered)
        if contains(pull_question_answered(i),'East')
            pull_question_direction = 0;
        elseif contains(pull_question_answered(i),'NorthEast')
            pull_question_direction = 1;
        elseif contains(pull_question_answered(i),'North')
            pull_question_direction = 2;  
        elseif contains(pull_question_answered(i),'NorthWest')
            pull_question_direction = 3;
        elseif contains(pull_question_answered(i),'West')
            pull_question_direction = 4;
        elseif contains(pull_question_answered(i),'SouthWest')
            pull_question_direction = 5;
        elseif contains(pull_question_answered(i),'South')
            pull_question_direction = 6;
        elseif contains(pull_question_answered(i),'SouthEast')
            pull_question_direction = 7;
        elseif contains(pull_question_answered(i),'Inside')
            pull_question_direction = 8;
        elseif contains(pull_question_answered(i),'Near')
            pull_question_direction = 9;
        end
        for j=1:length(sketch_name)
            if contains(pull_question_answered(i),sketch_name(j))
                pull_question_sketch = j;
            end
        end
        pulls(i) = pullCreate(pull_question_answered(i),pull_time(i),pull_question_sketch,pull_question_direction,pull_answer_time(i),response_time(i),pull_answer_response(i),i);
    end
    
    % target location during question answer
    target_during_pull_answer = zeros(length(pull_answer_time),2);
    for i=1:length(pull_answer_time)
        dist = abs(target_time-pull_answer_time(i));
        [min_dist,idx_min] = min(dist(:));
        target_during_pull_answer(i,:) = target_location(idx_min,1:2);
        target_near_pull_answer(i,:,:) = target_location(idx_min-answer_buffer:idx_min,1:2);
        for j=1:length(answer_buffer)
        end
        pulls(i).Target_Location = target_during_pull_answer(i,:);
    end
    
    % get probabilities (Yes/No is confusing terminology, should be
    % correct/incorrect)
    for i=1:length(pulls)
        tic
        [cond_label,cond_near] = callSoftMax(sketches(pulls(i).Sketch).Points,target_during_pull_answer(i,:));
        toc
        pulls(i).Prob = cond_label;
        pulls(i).NearProb = cond_near;
%         if pulls(i).Label < 9
%             if cond_label(pulls(i).Label+1) >= sensitivity
%                 if pulls(i).Response == 0
%                     pulls(i).Correct = 'Correct';
%                 else
%                     pulls(i).Correct = 'Incorrect';
%                 end
%             else
%                 if pulls(i).Response == 1
%                     pulls(i).Correct = 'Correct';
%                 else
%                     pulls(i).Correct = 'Incorrect';
%                 end
%             end
%         else
%             if strcmp(near_label,'Yes')
%                 if pulls(i).Response == 0
%                     pulls(i).Correct = 'Correct';
%                 else
%                     pulls(i).Correct = 'Incorrect';
%                 end
%             else
%                 if pulls(i).Response == 1
%                     pulls(i).Correct = 'Correct';
%                 else
%                     pulls(i).Correct = 'Incorrect';
%                 end
%             end 
%         end
        % get probability of target location near answer
        for j=1:answer_buffer
            [val,near_prob] = callSoftMax(sketches(pulls(i).Sketch).Points,target_near_pull_answer(i,j,:));
%             if pulls(i).Label < 9
%                 if val(pulls(i).Label+1) >= sensitivity
%                     if pulls(i).Response == 0
%                         corr = 'Correct';
%                     else
%                         corr = 'Incorrect';
%                     end
%                 else
%                     if pulls(i).Response == 1
%                         corr = 'Correct';
%                     else
%                         corr = 'Incorrect';
%                     end
%                 end
%             else
%                 if strcmp(near,'Yes')
%                     if pulls(i).Response == 0
%                         corr = 'Correct';
%                     else
%                         corr = 'Incorrect';
%                     end
%                 else
%                     if pulls(i).Response == 1
%                         corr = 'Correct';
%                     else
%                         corr = 'Incorrect';
%                     end
%                 end
%             end
            ps(j) = surroundingPullCreate(target_near_pull_answer(i,j,:),val,near_prob);
        end
        pulls(i).Surrounding = ps;
        % uncomment this to plot sketches
        accuracyPlot(pulls(i),sketches(pulls(i).Sketch))
    end
end
%% Output .mat data file
% get name of directory
direct_rev = reverse(direct);
tmp = extractAfter(direct_rev,'\');
tmp2 = erase(direct_rev,tmp);
direct_name = erase(reverse(tmp2),'\');
% save .mat
% if pull
%     save(direct_name,'pulls','sketches','num_views','target_location','drone_location')
% elseif push
%     save(direct_name,'pushes','sketches','num_views','target_location','drone_location')
% else
%     save(direct_name,'pulls','pushes','sketches','num_views','target_location','drone_location')
% end
%% Plotting
% figure(1)
% hold on
% leg_string = sketch_name;
% for i=1:num_sketch
%     pgon = polyshape(s(i).Points(1,:),s(i).Points(2,:));
%     plot(pgon)
% end
% leg_string = [leg_string;'Drone Location';'Target Location'];
% % plot drone and target position
% scatter(drone_location(:,1),drone_location(:,2),'.')
% scatter(target_location(:,1),target_location(:,2),'.')
% legend(leg_string)
% grid on
% xlim([-1000 1000])
% ylim([-1000 1000])
% title("Sketches")



%% Utility
% sketch struct
function ske = sketchCreate(name,points,time,area)
    ske.Name = name;
    ske.Points = points;
    ske.Time = time;
    ske.Area = area;
end
% pull struct
function p = pullCreate(question,asktime,sketch,label,answertime,responsetime,response,number)
    p.Question = question;
    p.AskTime = asktime;
    p.Sketch = sketch;
    p.Label = label;
    p.AnswerTime = answertime;
    p.ResponseTime = responsetime;
    p.Response = response;
    p.Number = number;
end
% pull surrounding data
function ps = surroundingPullCreate(target_loc,prob,near_prob)
    ps.Target_Location = target_loc;
    ps.Prob = prob;
    ps.NearProb = near_prob;
%     ps.Correct = correct;
end
% pushes
% function pu = pushCreate()
%% Accuracy Plotting
function accuracyPlot(p,s)
    figure;
    hold on
    grid on
    pgon = polyshape(s.Points(1,:),s.Points(2,:));
    plot(pgon)
    scatter(p.Target_Location(1),p.Target_Location(2),'*')
%     leg_string = [leg_string,string(p.Correct)];
%     for i=1:length(p.Surrounding)
%         scatter(p.Surrounding(i).Target_Location(1),p.Surrounding(i).Target_Location(2))
% %         leg_string = [leg_string,string(p.Surrounding(i).Correct)];
%     end
    legend(s.Name,"Target")
    if p.Response == 0
        an = 'Yes';
    else
        an = 'No';
    end
    
    if p.Label==9
        prob_str = string(round(p.NearProb,3)*100);
        textstr = ["","","","","","Inside: "]'+prob_str;
    else
        prob_str = string(round(p.Prob,3)*100);
        textstr = ["East: ","NorthEast: ","North: ","NorthWest: ","West: ","SouthWest: ","South: ","SouthEast: ","Inside: "]+prob_str;
    end
    %[X,Y] = centroid(pgon);
    text(750,-750,textstr)
    title_str = p.Question + "; Answer: " + an;
    title(title_str)
    xlim([-8,1000])
    ylim([-1000,8])
    saveas(gcf,string(p.Number)+".png")
end

