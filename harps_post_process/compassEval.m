function val = compassEval(points,eval_point)
%% Compass Evaluation
% evaluates points using compass directions from a ENWS grid
polyin = polyshape(points(1,:),points(2,:));
[xcen,ycen] = centroid(polyin);
angle = atan2(eval_point(2)-ycen,eval_point(1)-xcen);
angle_wrap = wrapTo2Pi(angle);
C = 0:7;
idx = 1+mod(round(8*mod(angle_wrap,2*pi)/(2*pi)),8);
val = C(idx);
end