function val = callSoftMax(points,eval_point)
%{ 
calls softmax model python script
%}
if isnan(eval_point)
    val = zeros(9,1);
    return
end
[a,b] = size(points);
points_str = '';
for i=1:a
    for j=1:b
        points_str = append(points_str,' ',string(points(i,j)));
    end
end
% add evaluation point
points_str = append(points_str,' ',string(eval_point(1)),' ',string(eval_point(2)));
commandStr = append('python3 ',pwd,'\softMaxSketchCall.py',points_str);
% call script
[status,cmdout] = system(commandStr);
% extract values
% format = "{'East': %d, 'NorthEast': %d, 'North': %d, 'NorthWest': %d, 'West': %d, 'SouthWest': %d, 'South': %d, 'SouthEast': %d, 'Inside': %d}"; 
cmdout = char(extractBetween(cmdout,"{","}"));
idxs_sep = strfind(cmdout,',');
idxs_frnt = strfind(cmdout,':');
for i=1:length(idxs_frnt)
    if i==length(idxs_frnt)
        val(i) = double(string(cmdout(idxs_frnt(i)+2:end-2)));
    else
        val(i) = double(string(cmdout(idxs_frnt(i)+2:idxs_sep(i)-1)));
    end
end
val = val./vecnorm(val);

end