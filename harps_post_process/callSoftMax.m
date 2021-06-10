function [val,near_prob] = callSoftMax(points,eval_point)
%{ 
calls softmax model python script
%}
if isnan(eval_point)
    val = zeros(9,1);
    return
end
points = reorderPoints(points);
[a,b] = size(points);
points_str = '';
for i=1:a
    for j=1:b
        points_str = append(points_str,' ',string(points(i,j)));
    end
end
% add evaluation point
points_str = append(points_str,' ',string(eval_point(1)),' ',string(eval_point(2)));
commandStr = append('python ',pwd,'\softMaxSketchCall.py',points_str);
% call script
[status,cmdout] = system(commandStr);
% extract values
% format = "{'East': %d, 'NorthEast': %d, 'North': %d, 'NorthWest': %d, 'West': %d, 'SouthWest': %d, 'South': %d, 'SouthEast': %d, 'Inside': %d}"; 
%if contains(extractBetween(cmdout,'[',']'),'↵')
try
    near_prob_str = split(erase(string(cell2mat(extractBetween(cmdout,'[',']'))),'↵'));
    for i=1:6
        near_prob(i) = str2num(near_prob_str(i));
    end
catch
    %disp('near prob failed to evaluate')
    near_prob = NaN(6,1);
end

% else
%     near_prob = zeros(6,1);
% end
cmdout = char(extractBetween(cmdout,"{","}"));
idxs_sep = strfind(cmdout,',');
idxs_frnt = strfind(cmdout,':');
for i=1:length(idxs_frnt)
    if i==length(idxs_frnt)
        val(i) = double(string(cmdout(idxs_frnt(i)+2:end)));
    else
        val(i) = double(string(cmdout(idxs_frnt(i)+2:idxs_sep(i)-1)));
    end
end
%val = val./vecnorm(val);
%val = val./max(val);
% [m,idx_m] = max(near_prob);
% if idx_m == 1
%     near = 'Yes';
% else
%     near = 'No';
% end

% in giveNearProb the order of 'inside' label is reversed so 
% flip it here to follow the cardinal directions order 
tmp = near_prob(end);
tmp2 = near_prob(1);
near_prob(1) = tmp;
near_prob(end) = tmp2;

end

%% Reorder points
% points need to be fed into softmax starting east most and then
% counterclockwise
function p_new = reorderPoints(points)
    x = points(1,:);
    y = points(2,:);
    xCenter = mean(x);
    yCenter = mean(y);
    angles = atan2d((y-yCenter),(x-xCenter));
    angles_rezeroed = angles+min(abs(angles));
    wraped_angles = wrapTo360(angles_rezeroed);
    [sortedAngles, sortedIndexes] = sort(wraped_angles);
    x_s = x(sortedIndexes);  % Reorder x and y with the new sort order.
    y_s = y(sortedIndexes);
    p_new = [x_s;y_s];
end
