function postProcessROSbag(data_dir)
%% Parameters
% topics
capture_topic = '/stopCon';
sketch_topic = '/Sketch';
pull_topic = '/Pull';
pull_answer_topic = '/PullAnswer';
camera_topic = '/Camera_Num';
target_topic = '/Target/car';
drone_topic = '/Drone1/pose';
drone_goal = '/Drone1/Goal';
push_topic = '/Push';
% constants
time_conversion = 1e-9; % conversion from nanoseconds to seconds
sketch_offset = [-167;-780];
sensitivity = 0.5; % probability cuttoff for accuracy
answer_buffer = 1; %[s] surrounding target location data to evaluate
%% Intake Data files
topic_files = dir(data_dir.folder+"\"+data_dir.name+"\*.csv");
bags = struct();
j=1;
for i=1:length(topic_files)
    name = topic_files(i).name;
    name = strrep(name,'_slash_','/');
    name = name(1:end-4);
    if ~contains(name,'rosout')
        bags(j).topic = name;
        bags(j).data = readtable(topic_files(i).folder+"\"+topic_files(i).name);
        j=j+1;
    end
end
n = length(bags);
%% Test Type
% pull, push, or both
pull = false;
push = false;
if contains(topic_files(1).folder,'Both')
    push = true;
    pull = true;
elseif contains(topic_files(1).folder,'Pull')
    pull = true;
elseif contains(topic_files(1).folder,'Push')
    push = true;
else
    error("Error: Improper Directory name. Make sure directory: " + data_dir.name +"contains either 'push', 'pull', or 'both'.")
end
%% Find Corresponding Survey Response
subject_case = false;
if contains(data_dir.name,'Subject')
    subject_case = true;
    subject_number = double(string(extractBetween(data_dir.name,'Subject','_')));
    questionnaire = readtable("Post-Simulation Questionnaire.csv");
    background = readtable("Subject Background Questionnaire.csv");
    subject_data_ID_string = string(questionnaire.SubjectID);
    for i=1:length(subject_data_ID_string)
        subject_data_ID(i) = str2num(subject_data_ID_string(i));
    end
    subject_data_idx = find(subject_data_ID==subject_number);
    subject_data_idx_back = find(background.WhatIsYourSubjectID_==subject_number);
    for i=1:length(subject_data_idx)
        if contains(questionnaire.Task{subject_data_idx(i)},'Pull')
            if contains(questionnaire.Task{subject_data_idx(i)},'Push')
                subject_data_idx_type(i) = 3;
            else
                subject_data_idx_type(i) = 1;
            end
        else
            subject_data_idx_type(i) = 2;
        end
    end
    if pull
        if push
            idx_survey_response = find(subject_data_idx_type==3);
        else
            idx_survey_response = find(subject_data_idx_type==1);
        end
    else
        idx_survey_response = find(subject_data_idx_type==2);
    end
    subject_background = background(subject_data_idx_back,:);
    subject_survey_data = questionnaire(subject_data_idx(idx_survey_response),:);
    trust_questions = table2array(subject_survey_data(:,10:17));
    subject_survey_trust = mean(trust_questions(~isnan(trust_questions)));
    workload_questions = table2array(subject_survey_data(:,4:8));
    subject_survey_workload = mean(workload_questions(~isnan(workload_questions)));
    
end
%questionnaire = readtable("Post-Simulation Questionnaire.csv");
%% Exctract Data
num_responses = 0;
% get start time to zero other times
for i=1:n
    if strcmp(bags(i).topic,drone_goal)
        %target_time = cell2mat(bags(i).data(2:end,1));
        reference_time = bags(i).data.rosbagTimestamp;
        start_time = reference_time(1);
        reference_time = reference_time - start_time;
        reference_time = reference_time.*time_conversion;
    end
end
% get rest of data
for i=1:n
    switch bags(i).topic
        case target_topic
            target_time = bags(i).data.rosbagTimestamp-start_time;
            target_time = target_time.*time_conversion;
            target_location = [bags(i).data.x,bags(i).data.y,bags(i).data.z];
            for j=1:3
                idx_nan = find(isnan(target_location(:,j)));
                target_location(idx_nan,:) = [];
                target_time(idx_nan) = [];
            end
        % isolate condition data and its rosbag time data
        case capture_topic
%             conditions = string(bags(i).data.data);
%             conditions(:,:) = erase(conditions(:,:),'"');
            condition_times = bags(i).data.rosbagTimestamp-start_time;
            condition_times = condition_times.*time_conversion;
            % get time to capture
%             idx_condition = find(conditions=='Detect');
            capture_time = condition_times(1);
        % number of sketches
        case sketch_topic
            sketch_time = bags(i).data{:,1}-start_time;
            sketch_time = sketch_time.*time_conversion;
            num_sketch = length(sketch_time);
            % sketch name
            sketch_name = string(bags(i).data{:,19});
            sketch_name = erase(sketch_name,'"');
            for k=1:num_sketch
                % locations of sketches
                sketch_points = [bags(i).data{k,4},bags(i).data{k,8},bags(i).data{k,12},bags(i).data{k,16};bags(i).data{k,5},bags(i).data{k,9},bags(i).data{k,13},bags(i).data{k,17}];
                % area of sketch
                sketch_area = polyarea(sketch_points(1,:),sketch_points(2,:));
                sketches(k) = sketchCreate(char(sketch_name(k)),sketch_points,sketch_time(k),sketch_area);
            end  
        % subject response time
        case pull_topic
            if pull
                pull_time = bags(i).data{:,1}-start_time;
                pull_time = pull_time.*time_conversion;
                pull_question = erase(string(bags(i).data.question),'"');
                pull_counter = bags(i).data.counter;
            end
        case pull_answer_topic
            if pull
                pull_answer_time = bags(i).data.rosbagTimestamp-start_time;
                pull_answer_time = pull_answer_time.*time_conversion;
                % handle duplicates
                [pull_answer_counter,idx_unique_pull] = unique(bags(i).data.counter);
                pull_answer_response = bags(i).data.response(idx_unique_pull);
                pull_answer_time = pull_answer_time(idx_unique_pull);
            end
        % number of camera views observed
        case camera_topic
            camera_time = bags(i).data.rosbagTimestamp-start_time;
            camera_time = camera_time.*time_conversion;
            camera_number = bags(i).data.data;
            % remove #6 as it is the drone camera
            camera_number_adj = camera_number(find(camera_number~=6));
            num_views = length(camera_number_adj);
            %num_camera_switches = length(camera_number);
        case drone_topic
            drone_time = bags(i).data.rosbagTimestamp-start_time;
            drone_time = drone_time.*time_conversion;
            drone_location = [bags(i).data.x,bags(i).data.y,bags(i).data.z];
            % handle nans
            for j=1:3
                idx_nan = find(isnan(drone_location(:,j)));
                drone_location(idx_nan,:) = [];
                drone_time(idx_nan) = [];
            end
        case push_topic
            push_time = bags(i).data.rosbagTimestamp-start_time;
            push_time = push_time.*time_conversion;
            push_det = string(bags(i).data{:,3});
            push_label = string(bags(i).data{:,4});
            for j=1:length(push_label)
                push_label_direction(j) = getLabelNum(push_label(j));
            end
            push_sketch_name = string(bags(i).data{:,5});
        otherwise
            fprintf("Unused topic: %s\n",bags(i).topic)
            continue
    end
end

%% Response Time
if pull && exist('pull_answer_counter','var')
    % response time for each answered question
    response_time = zeros(length(pull_answer_counter),1);
    for i=1:length(pull_answer_counter)
        response_time(i) = pull_answer_time(i) - pull_time(pull_answer_counter(i)+1);
    end
    
end

%% Sketch Accuracy Pull
all_accuracy_responses_softmax = [];
accuracy_pull_softmax = [];
accuracy_push_softmax = [];
accuracy_pull_compass = [];
accuracy_push_compass = [];
all_accuracy_responses_compass = [];
% if pull, find target location when question is answered
if pull && exist('pull_answer_counter','var')
    % get only answered questions
    for i=1:length(pull_answer_counter)
        pull_question_answered(i) = pull_question(pull_answer_counter(i)+1);
    end
    
    % get sketches for answered question
    for i=1:length(pull_question_answered)
        pull_question_sketch_names(i) = extractAfter(pull_question_answered(i),'of ');
        pull_question_sketch_names(i) = erase(pull_question_sketch_names(i),'"');
    end
    
    % split sentences into words (these variable names are absurd at this
    % point) Handles edge case where sketch name appears multiple times in
    % sentence
    pull_question_answered_sketchnames = split(pull_question_answered,' ');
    % get question direction
    for i=1:length(pull_question_answered)
        pull_question_direction = getLabelNum(pull_question_answered(i));
        for j=1:length(sketch_name)
            if contains(pull_question_answered_sketchnames(1,i,end),sketch_name(j))
                pull_question_sketch = j;
                break
            end
        end
        pulls(i) = pullCreate(pull_question_answered(i),pull_question_answered_sketchnames(1,i,6),pull_question_answered_sketchnames(1,i,4),pull_time(i),pull_question_sketch,pull_question_direction,pull_answer_time(i),response_time(i),pull_answer_response(i),i);
    end
    
    % target location during question answer
    target_during_pull_answer = zeros(length(pull_answer_time),2);
    drone_during_pull_answer = zeros(length(pull_answer_time),2);
    for i=1:length(pull_answer_time)
        dist = abs(target_time-pull_answer_time(i));
        [min_dist,idx_min] = min(dist(:));
        target_during_pull_answer(i,:) = target_location(idx_min,1:2);
        drone_during_pull_answer(i,:) = drone_location(idx_min,1:2);
%         target_near_pull_answer(i,:,:) = target_location(idx_min-answer_buffer:idx_min,1:2);
%         for j=1:length(answer_buffer)
%         end
        pulls(i).Target_Location = target_during_pull_answer(i,:);
    end
    
    
    for i=1:length(pulls)
        % softmax/compass eval
        if strcmp(pulls(i).Sketch_Name,'You')
            % softmax
            [cond_label,cond_near]=youSketchEval(drone_during_pull_answer(i,:),target_during_pull_answer(i,:));
            % compass
            drone = drone_during_pull_answer(i,:);
            box_width = 10;
            points = [drone(1)+box_width,drone(1)+box_width,drone(1)-box_width,drone(1)-box_width;drone(2)-box_width,drone(2)+box_width,drone(2)+box_width,drone(2)-box_width];
            cond_label_compass = compassEval(points,target_during_pull_answer(i,:));
        elseif (strcmp(pulls(i).Label_Name,'Inside') || strcmp(pulls(i).Label_Name,'Near'))
            [cond_label,cond_near] = callSoftMax(sketches(pulls(i).Sketch).Points,target_during_pull_answer(i,:));
            cond_label_compass = nan(8,1);
        else
            [cond_label,cond_near] = callSoftMax(sketches(pulls(i).Sketch).Points,target_during_pull_answer(i,:));
            cond_label_compass = compassEval(sketches(pulls(i).Sketch).Points,target_during_pull_answer(i,:));
        end
        pulls(i).Prob = cond_label;
        pulls(i).NearProb = cond_near;
        pulls(i).CompassProb = cond_label_compass;
        % accuracy softmax and compass
        if strcmp(pulls(i).Label_Name,'Near')
            if pulls(i).Response == 1
                % if yes, prob near
                accuracy_pull_softmax = [accuracy_pull_softmax,pulls(i).NearProb(1)];
            elseif pulls(i).Response == -1
                % if no, prob not near
                accuracy_pull_softmax = [accuracy_pull_softmax,1-pulls(i).NearProb(1)];
            end
        else
            if pulls(i).Response == 1
                accuracy_pull_softmax = [accuracy_pull_softmax,pulls(i).Prob(pulls(i).Label+1)/max(pulls(i).Prob)];
            elseif pulls(i).Response == -1 
                accuracy_pull_softmax = [accuracy_pull_softmax,1-pulls(i).Prob(pulls(i).Label+1)/max(pulls(i).Prob)];
            end
            
            if ~strcmp(pulls(i).Label_Name,'Inside')
                if pulls(i).Response == 1
                    accuracy_pull_compass = [accuracy_pull_compass,pulls(i).CompassProb(pulls(i).Label+1)/max(pulls(i).CompassProb)];
                elseif pulls(i).Response == -1
                    accuracy_pull_compass = [accuracy_pull_compass,1-pulls(i).CompassProb(pulls(i).Label+1)/max(pulls(i).CompassProb)];
                end
            end
        end
    end
    
    
    
    
    
    % get probabilities 
%     for i=1:length(pulls)
%         if strcmp(sketches(pulls(i).Sketch).Name,'you')
%             [cond_label,cond_near]=youSketchEval(drone_during_pull_answer(i,:),target_during_pull_answer(i,:));
%         else
%             [cond_label,cond_near] = callSoftMax(sketches(pulls(i).Sketch).Points,target_during_pull_answer(i,:));
%         end
%         pulls(i).Prob = cond_label;
%         pulls(i).NearProb = cond_near;
%         
%         % evaluate response
%         if pulls(i).Label == 9
%             [~,maxlabel] = max(pulls(i).NearProb);
%             maxlabel = maxlabel-1;
%             if maxlabel == 0
%                 pulls(i).Correct_Softmax = true;
%             else
%                 pulls(i).Correct_Softmax = false;
%             end
%         else
%             pulls(i).CompassProb = compassEval(sketches(pulls(i).Sketch).Points,target_during_pull_answer(i,:));
%             maxval_compass = max(pulls(i).CompassProb);
%             idx_maxCompasslabel = find(pulls(i).CompassProb == maxval_compass)-1;
%             if ismember(pulls(i).Label,idx_maxCompasslabel)
%                 pulls(i).Correct_Compass = true;
%             else
%                 if pulls(i).Label ~= 8
%                     pulls(i).Correct_Compass = false;
%                 else
%                     pulls(i).Correct_Compass = [];
%                 end
%             end
%             accuracy_pull_compass = [accuracy_pull_compass,pulls(i).Correct_Compass];
%             [~,maxlabel] = max(pulls(i).Prob);
%             maxlabel = maxlabel-1;
%             if maxlabel == pulls(i).Label
%                 pulls(i).Correct_Softmax = true;
%             else
%                 pulls(i).Correct_Softmax = false;
%             end
%         end
%         accuracy_pull(i) = pulls(i).Correct_Softmax;
%         % get probability of target location near answer
% %         for j=1:answer_buffer
% %             [val,near_prob] = callSoftMax(sketches(pulls(i).Sketch).Points,target_near_pull_answer(i,j,:));
% %             ps(j) = surroundingCreate(target_near_pull_answer(i,j,:),val,near_prob);
% %         end
% %         pulls(i).Surrounding = ps;
%         % uncomment this to plot sketches
%         %accuracyPlot(pulls(i),sketches(pulls(i).Sketch))
%     end
    all_accuracy_responses_softmax = [all_accuracy_responses_softmax,accuracy_pull_softmax];
    all_accuracy_responses_compass = [all_accuracy_responses_compass,accuracy_pull_compass];
    num_responses = num_responses + length(pulls);
    
   % get unanswered pulls
       % get only answered questions
    j = length(pulls);
    k=1;
    for i=1:length(pull_question)
        if ~ismember(i,pull_answer_counter)
            pulls_unanswered(k) = pullCreate(pull_question(i),nan,nan,pull_time(i),nan,nan,nan,nan,nan,nan);
            k=k+1;
        end
    end
end


%% Sketch Accuracy Push
if push && exist('push_sketch_name','var')
    % get sketch number
    for i=1:length(push_sketch_name)
        for j=1:length(sketch_name)
            if contains(push_sketch_name(i),sketch_name(j))
                push_sketch = j;
                break
            else
                push_sketch = -1;
            end
        end
        pushes(i) = pushCreate(push_det(i),push_label(i),push_sketch_name(i),push_label_direction(i),push_sketch,push_time(i),i); 
    end
    
    target_during_push_answer = zeros(length(push_time),2);
    drone_during_pull_answer = zeros(length(push_time),2);
    for i=1:length(push_time)
        dist = abs(target_time-push_time(i));
        [min_dist,idx_min] = min(dist(:));
        target_during_push_answer(i,:) = target_location(idx_min,1:2);
        drone_during_pull_answer(i,:) = drone_location(idx_min,1:2);
%         target_near_push_answer(i,:,:) = target_location(idx_min-answer_buffer:idx_min,1:2);
%         for j=1:length(answer_buffer)
%         end
        pushes(i).Target_Location = target_during_push_answer(i,:);
    end
    
    for i=1:length(pushes)
        % softmax/compass eval
        if strcmp(pushes(i).Sketch_Name,'You')
            % softmax
            [cond_label,cond_near]=youSketchEval(drone_during_pull_answer(i,:),target_during_push_answer(i,:));
            % compass
            drone = drone_during_pull_answer(i,:);
            box_width = 10;
            points = [drone(1)+box_width,drone(1)+box_width,drone(1)-box_width,drone(1)-box_width;drone(2)-box_width,drone(2)+box_width,drone(2)+box_width,drone(2)-box_width];
            cond_label_compass = compassEval(points,target_during_push_answer(i,:));
        elseif (strcmp(pushes(i).Label_Name,'Inside') || strcmp(pushes(i).Label_Name,'Near'))
            [cond_label,cond_near] = callSoftMax(sketches(pushes(i).Sketch).Points,target_during_push_answer(i,:));
            cond_label_compass = nan(8,1);
        else
            [cond_label,cond_near] = callSoftMax(sketches(pushes(i).Sketch).Points,target_during_push_answer(i,:));
            cond_label_compass = compassEval(sketches(pushes(i).Sketch).Points,target_during_push_answer(i,:));
        end
        pushes(i).Prob = cond_label;
        pushes(i).NearProb = cond_near;
        pushes(i).CompassProb = cond_label_compass;
        % accuracy softmax and compass
        if strcmp(pushes(i).Label_Name,'Near')
            if contains(pushes(i).Determiner,'not')
                accuracy_push_softmax = [accuracy_push_softmax,1-pushes(i).NearProb(1)];
            else
                accuracy_push_softmax = [accuracy_push_softmax,pushes(i).NearProb(1)];
            end
        else
            if contains(pushes(i).Determiner,'not')
                accuracy_push_softmax = [accuracy_push_softmax,1-pushes(i).Prob(pushes(i).Label+1)/max(pushes(i).Prob)];
            else
                accuracy_push_softmax = [accuracy_push_softmax,pushes(i).Prob(pushes(i).Label+1)/max(pushes(i).Prob)];
            end            
            if ~strcmp(pushes(i).Label_Name,'Inside')
                if contains(pushes(i).Determiner,'not')
                    accuracy_push_compass = [accuracy_push_compass,1-pushes(i).CompassProb(pushes(i).Label+1)/max(pushes(i).CompassProb)];
                else
                    accuracy_push_compass = [accuracy_push_compass,pushes(i).CompassProb(pushes(i).Label+1)/max(pushes(i).CompassProb)];
                end                   
            end
        end

        
%         % compass eval
%         if pushes(i).Label == 9
%             [~,maxlabel] = max(pushes(i).NearProb);
%             maxlabel = maxlabel-1;
%             if maxlabel == 0
%                 pushes(i).Correct_Softmax = true;
%             else
%                 pushes(i).Correct_Softmax = false;
%             end
%         else
%             if strcmp(pushes(i).Sketch_Name,'You')
%                 drone = drone_during_pull_answer(i,:);
%                 box_width = 10;
%                 points = [drone(1)+box_width,drone(1)+box_width,drone(1)-box_width,drone(1)-box_width;drone(2)-box_width,drone(2)+box_width,drone(2)+box_width,drone(2)-box_width];
%                 pushes(i).CompassProb = compassEval(points,target_during_push_answer(i,:));
%             else
%                 pushes(i).CompassProb = compassEval(sketches(pushes(i).Sketch).Points,target_during_push_answer(i,:));
%             end
%             maxval_compass = max(pushes(i).CompassProb);
%             idx_maxCompasslabel = find(pushes(i).CompassProb == maxval_compass)-1;
%             if ismember(pushes(i).Label,idx_maxCompasslabel)
%                 pushes(i).Correct_Compass = true;
%             else
%                 if pushes(i).Label ~= 8
%                     pushes(i).Correct_Compass = false;
%                 else
%                     pushes(i).Correct_Compass = [];
%                 end
%             end
%             accuracy_push_compass = [accuracy_push_compass,pushes(i).Correct_Compass];
%             [~,maxlabel] = max(pushes(i).Prob);
%             maxlabel = maxlabel-1;
%             if maxlabel == pushes(i).Label
%                 pushes(i).Correct_Softmax = true;
%             else
%                 pushes(i).Correct_Softmax = false;
%             end
%         end
%         accuracy_push(i) = pushes(i).Correct_Softmax;
        
        
        % get probability of target location near answer
%         for j=1:answer_buffer
%             [val,near_prob] = callSoftMax(sketches(pushes(i).Sketch).Points,target_near_push_answer(i,j,:));
%             push_surr(j) = surroundingCreate(target_near_push_answer(i,j,:),val,near_prob);
%         end
%         pushes(i).Surrounding = push_surr;
    end    
    all_accuracy_responses_softmax = [all_accuracy_responses_softmax,accuracy_push_softmax];
    all_accuracy_responses_compass = [all_accuracy_responses_compass,accuracy_push_compass];
    num_responses = num_responses+length(pushes);
end

if ~exist('capture_time','var')
    capture_time = nan;
end
%% Total accuracy rating
total_accuracy_softmax = mean(all_accuracy_responses_softmax(~isnan(all_accuracy_responses_softmax)));
total_accuracy_compass = mean(all_accuracy_responses_compass(~isnan(all_accuracy_responses_compass)));
%% Output .mat data file
out_dir_str = "post-process-output"+date;
if ~exist(out_dir_str, 'dir')
    mkdir(out_dir_str)
end
if exist(out_dir_str+"\"+data_dir.name+".mat",'file')
    file_name = out_dir_str+"\"+data_dir.name+string(randi(10000));
else  
    file_name = out_dir_str+"\"+data_dir.name;
end
% save .mat only if human subject data
if subject_case
    if exist('pull_answer_counter','var') && exist('push_sketch_name','var')
        save(file_name,'pulls','pulls_unanswered','pushes','sketches','num_views','target_location','target_time','drone_location','drone_time','capture_time','subject_survey_data','subject_background','subject_survey_trust','total_accuracy_softmax','total_accuracy_compass','subject_survey_workload')
    elseif pull && exist('pull_answer_counter','var')
        save(file_name,'pulls','pulls_unanswered','sketches','num_views','target_location','target_time','drone_location','drone_time','capture_time','subject_survey_data','subject_background','subject_survey_trust','total_accuracy_softmax','total_accuracy_compass','subject_survey_workload')
    elseif push && exist('push_sketch_name','var')
        save(file_name,'pushes','sketches','num_views','target_location','target_time','drone_location','drone_time','capture_time','subject_survey_data','subject_background','subject_survey_trust','total_accuracy_softmax','total_accuracy_compass','subject_survey_workload')
    end
end
end



%% Utility

% sketch struct
function ske = sketchCreate(name,points,time,area)
    ske.Name = name;
    ske.Points = points;
    ske.Time = time;
    ske.Area = area;
end

% pull struct
function p = pullCreate(question,sketch_name,label_name,asktime,sketch,label,answertime,responsetime,response,number)
    p.Question = question;
    p.Sketch_Name = sketch_name;
    p.Label_Name = label_name;
    p.AskTime = asktime;
    p.Sketch = sketch;
    p.Label = label;
    p.AnswerTime = answertime;
    p.ResponseTime = responsetime;
    p.Response = response;
    p.Number = number;
end

% pull surrounding data
function ps = surroundingCreate(target_loc,prob,near_prob)
    ps.Target_Location = target_loc;
    ps.Prob = prob;
    ps.NearProb = near_prob;
%     ps.Correct = correct;
end

% pushes
function p = pushCreate(determiner,label_name,sketch_name,label_dir,sketch,time,number) 
    p.Determiner = determiner;
    p.Label_Name = label_name;
    p.Sketch_Name = sketch_name;
    p.Label = label_dir;
    p.Sketch = sketch;
    p.Time = time;
    p.Number = number;
end

% labels
function l = getLabelNum(label)
if contains(label,'East')
    l = 0;
elseif contains(label,'NorthEast')
    l = 1;
elseif contains(label,'North')
    l = 2;  
elseif contains(label,'NorthWest')
    l = 3;
elseif contains(label,'West')
    l = 4;
elseif contains(label,'SouthWest')
    l = 5;
elseif contains(label,'South')
    l = 6;
elseif contains(label,'SouthEast')
    l = 7;
elseif contains(label,'Inside')
    l = 8;
elseif contains(label,'Near')
    l = 9;
end
end



%% Accuracy Plotting
function accuracyPlot(p,s)
    figure;
    hold on
    grid on
    pgon = polyshape(s.Points(1,:),s.Points(2,:));
    plot(pgon)
    scatter(p.Target_Location(1),p.Target_Location(2),'*')
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