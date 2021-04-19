function postProcessROSbag(data_dir)
%% Parameters
% topics
capture_topic = '/Obs';
sketch_topic = '/Sketch';
pull_topic = '/Pull';
pull_answer_topic = '/PullAnswer';
camera_topic = '/Camera_Num';
target_topic = '/Target/car';
drone_topic = '/Drone1/pose';
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
    subject_data_idx = find(questionnaire.SubjectID==subject_number);
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
    subject_survey_data = questionnaire(subject_data_idx(idx_survey_response),:);
end
questionnaire = readtable("Post-Simulation Questionnaire.csv");
%% Exctract Data
% get start time to zero other times
for i=1:n
    if strcmp(bags(i).topic,target_topic)
        %target_time = cell2mat(bags(i).data(2:end,1));
        target_time = bags(i).data.rosbagTimestamp;
        start_time = target_time(1);
        target_time = target_time - start_time;
        target_time = target_time.*time_conversion;
    end
end
% get rest of data
for i=1:n
    switch bags(i).topic
        case target_topic
            target_location = [bags(i).data.x,bags(i).data.y,bags(i).data.z];
            for j=1:3
                idx_nan = find(isnan(target_location(:,j)));
                target_location(idx_nan,:) = [];
                target_time(idx_nan) = [];
            end
        % isolate condition data and its rosbag time data
        case capture_topic
            conditions = string(bags(i).data.data);
            conditions(:,:) = erase(conditions(:,:),'"');
            condition_times = bags(i).data.rosbagTimestamp-start_time;
            condition_times = condition_times.*time_conversion;
            % get time to capture
            idx_condition = find(conditions=='Detect');
            capture_time = condition_times(idx_condition);
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
            num_views = length(unique(camera_number_adj));
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
            push_time = bags(i).data.rosbagTimestamp;
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
    
    % get question direction
    for i=1:length(pull_question_answered)
        pull_question_direction = getLabelNum(pull_question_answered(i));
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
%         target_near_pull_answer(i,:,:) = target_location(idx_min-answer_buffer:idx_min,1:2);
%         for j=1:length(answer_buffer)
%         end
        pulls(i).Target_Location = target_during_pull_answer(i,:);
    end
    
    % get probabilities (Yes/No is confusing terminology, should be
    % correct/incorrect)
    for i=1:length(pulls)
        [cond_label,cond_near] = callSoftMax(sketches(pulls(i).Sketch).Points,target_during_pull_answer(i,:));
        pulls(i).Prob = cond_label;
        pulls(i).NearProb = cond_near;
        % get probability of target location near answer
%         for j=1:answer_buffer
%             [val,near_prob] = callSoftMax(sketches(pulls(i).Sketch).Points,target_near_pull_answer(i,j,:));
%             ps(j) = surroundingCreate(target_near_pull_answer(i,j,:),val,near_prob);
%         end
%         pulls(i).Surrounding = ps;
        % uncomment this to plot sketches
        %accuracyPlot(pulls(i),sketches(pulls(i).Sketch))
    end
end

%% Sketch Accuracy Push
if push && exist('push_sketch_name','var')
    % get sketch number
    for i=1:length(push_sketch_name)
        for j=1:length(sketch_name)
            if contains(push_sketch_name(i),sketch_name(j))
                push_sketch = j;
            end
        end
        pushes(i) = pushCreate(push_det(i),push_label(i),push_sketch_name(i),push_label_direction(i),push_sketch,push_time(i),i); 
    end
    
    target_during_push_answer = zeros(length(push_time),2);
    for i=1:length(push_time)
        dist = abs(target_time-push_time(i));
        [min_dist,idx_min] = min(dist(:));
        target_during_push_answer(i,:) = target_location(idx_min,1:2);
%         target_near_push_answer(i,:,:) = target_location(idx_min-answer_buffer:idx_min,1:2);
%         for j=1:length(answer_buffer)
%         end
        pushes(i).Target_Location = target_during_push_answer(i,:);
    end
    
    for i=1:length(pushes)
        [cond_label,cond_near] = callSoftMax(sketches(pushes(i).Sketch).Points,target_during_push_answer(i,:));
        pushes(i).Prob = cond_label;
        pushes(i).NearProb = cond_near;
        % get probability of target location near answer
%         for j=1:answer_buffer
%             [val,near_prob] = callSoftMax(sketches(pushes(i).Sketch).Points,target_near_push_answer(i,j,:));
%             push_surr(j) = surroundingCreate(target_near_push_answer(i,j,:),val,near_prob);
%         end
%         pushes(i).Surrounding = push_surr;
    end    
    
end
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
    if pull && exist('pull_answer_counter','var')
        save(file_name,'pulls','sketches','num_views','target_location','target_time','drone_location','drone_time','capture_time','subject_survey_data')
    elseif push && exist('push_sketch_name','var')
        save(file_name,'pushes','sketches','num_views','target_location','target_time','drone_location','drone_time','capture_time','subject_survey_data')
    elseif exist('pull_answer_counter','var') && exist('push_sketch_name','var')
        save(file_name,'pulls','pushes','sketches','num_views','target_location','target_time','drone_location','drone_time','capture_time','subject_survey_data')
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