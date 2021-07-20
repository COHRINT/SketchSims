function [cond,near_cond]=youSketchEval(drone,target)
% create box around drone location and call softmax with that box
box_width = 10;
points = [drone(1)+box_width,drone(1)+box_width,drone(1)-box_width,drone(1)-box_width;drone(2)-box_width,drone(2)+box_width,drone(2)+box_width,drone(2)-box_width];

[cond,near_cond]=callSoftMax(points,target);
end