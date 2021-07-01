%The script plots the current user's sketches and the previous target
%history
run = 'Curious_Push_3_';
if isnan(capture_time)
    capture_time = 900;
end
scale = length(drone_location)/capture_time;
time1 = 1;
time2 = 537;
theend = 1;
index2 = round(time2*scale);
figure
hold on
grid off
img = imread('/Users/RayH/Documents/School/Research/HARPS/COHRINTCode/overhead_mini_fit.png');
imagesc(0,0,flipud(img))
% imagesc(0,0,img)
for s= 1:size(sketches,2)
    if theend
        s_x = sketches(s).Points(1,:);
        s_y = sketches(s).Points(2,:);
%         s_y = -(s_y+s_y*0.1) + 1000;
        pgon = polyshape(s_x,s_y);
        [x,y] = centroid(pgon);
        plot(pgon)
        text(x,y,sketches(s).Name,'FontSize',14)
    elseif sketches(s).Time <= time2
   
        s_x = sketches(s).Points(1,:);
        s_y = sketches(s).Points(2,:);
%         s_x = s_x+s_x*0.1;
%         s_y = -(s_y+s_y*0.1) + 1000;
        pgon = polyshape(s_x,s_y);
        [x,y] = centroid(pgon);

        plot(pgon)
        text(x,y,sketches(s).Name,'FontSize',14)
    else
        continue
    end

end

%End
if theend
    scatter(target_location(time1:end,1),target_location(time1:end,2),'.r')
    scatter(target_location(end,1),target_location(end,2),1000,'xr')
    scatter(target_location(time1,1),target_location(time1,2),1000,'.r')
%     text(target_location(time1,1)+20,target_location(time1,2)+20,'Target Start')
    % sketch_offset = [0;0];
    scatter(drone_location(time1:end,1),drone_location(time1:end,2),'.b')
    scatter(drone_location(time1,1),drone_location(time1,2),1000,'.b')
    scatter(drone_location(end,1),drone_location(end,2),1000,'xb')
%     text(drone_location(time1,1)+20,drone_location(time1,2)+10,'Drone Start')
    time2 = 'capture';
else
    scatter(target_location(time1:index2,1),target_location(time1:index2,2),'.r')
    scatter(target_location(time1,1),target_location(time1,2),1000,'.r')
    scatter(target_location(index2,1),target_location(index2,2),1000,'xr')
%     text(target_location(time1,1)+20,target_location(time1,2)+20,'Target Start')
    % sketch_offset = [0;0];
    scatter(drone_location(time1:index2,1),drone_location(time1:index2,2),'.b')
    scatter(drone_location(time1,1),drone_location(time1,2),1000,'.b')
    scatter(drone_location(index2,1),drone_location(index2,2),1000,'xb')
%     text(drone_location(time1,1)+20,drone_location(time1,2)+10,'Drone Start')
end
% legend(s.Name,"Target")
% legend([],[],'Target Location','Drone Location')

%[X,Y] = centroid(pgon);
% text(750,-750,textstr)
% title_str = p.Question + "; Answer: " + an;
% title(title_str)
 xlim([0,1000])
 ylim([0,1000])
%   saveas(gcf,"/Users/RayH/Documents/School/Research/HARPS/COHRINTCode/Interaction_Examples/"+run+string(time2)+"s.png")