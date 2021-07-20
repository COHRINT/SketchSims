function val = compassEval(points,eval_point)
%% Compass Evaluation
% evaluates points using compass directions from a ENWS grid
polyin = polyshape(points(1,:),points(2,:));
[xcen,ycen] = centroid(polyin);
angle = atan2(eval_point(2)-ycen,eval_point(1)-xcen);
angle_wrap = wrapTo2Pi(angle);
angle_deg = rad2deg(angle_wrap);
v = zeros(1,8);
a = 0;
j=0;
for i=1:8
   if a<angle_deg && angle_deg<=(a+90)
       v(i) = 1;
       j=j+1;
   end
   a = a+45;
end


v = v./j;
for i=1:8
    if i==1
        val(i) = v(end);
    else
        val(i) = v(i-1);
    end
end
end