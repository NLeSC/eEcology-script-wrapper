function GPSvis_database(username, password, db_name, host, KDevice, Colors, starttime, stoptime, AltChoice, SizeChoice, SpeedClasses)
% KDevices is a vector (length n) with the devices that are included in the anaysis
% Colors is a vector (length n) with the colorsthat are choosen from the list
% STimes is a matrix (nx2)with a vector (length n) with timeStamps of StartTime and a vector (length n) of EndTime
% AltChoice is a vector (length n) with for each device 'clampToGround', 'relativeToGround', 'absolute'
% SpeedClasses is a matrix (nx3) with three threshold values for speed
% SizeChoice is a vector (length n) with 'small', 'medium' , 'large'
% This function uses the Matlab2GoogleEarth toolbox 
% SV: Do not clear function arguments
% clear all
close all

% Command to compile:
% mcc -mv -R -nodisplay -I openearth/io/postgresql -I openearth -I openearth/general -I openearth/general/io_fun -I googleearth stefanoe.m distWB.m

% Sometimes required to find postgresql driver
% pg_settings()

conn = pg_connectdb(db_name, 'host', host, 'user', username, 'pass', password, 'database_toolbox', 0);

% SV: Use function argument
% KDevice =[620 800];%[620 629 632 639 766 769 772 775 777 800];

% SV: Command line arguments are strings, use eval to convert them into matlab variable types.
if ischar(KDevice)
  KDevice = eval(KDevice);
end

if ischar(Colors)
  Colors = eval(Colors);
end

% AltChoice is not used so display
display(AltChoice)

if ischar(SizeChoice)
  SizeChoice = eval(SizeChoice);
end
% is not used so display
display(SizeChoice)

if ischar(SpeedClasses)
  SpeedClasses = eval(SpeedClasses);
end
% is not used so display
display(SpeedClasses)

%% add path Matlab2GoogleEarth toolbox
% SV: Added during compilation
% addpath('c:\Program Files\MATLAB\googleearth\')

% image width and height
imgWidthPix = 1900;
imgHeightPix = 1050;
% set the image sizes, resolution and units; also see print option -r100
imgResolution = 100; % 100 dpi
imgWidth = imgWidthPix / imgResolution;
imgHeight = imgHeightPix / imgResolution;
% this line is necessary for rendering without openGL drivers/physical screen
set(0, 'DefaultFigureRenderer', 'zbuffer');

tic
%% read data directly from the database
for k=1:length(KDevice)
    clear Time doy Dist ISpeed TSpeed TotNrAcc
    device = num2str(KDevice(k));
    % SV: Use function argument
    % starttime = '2013-02-01 00:00:00';
    start = strcat('''',starttime,''''); % put the single quotes around it.
    % SV: Use function argument
    % stoptime  = '2013-02-10 00:00:00';
    stop = strcat('''',stoptime,'''');


    %% set db prefs.
    % set database pref. this determines how the results are returned.
    % 'structure' means you can reference the fields by the same names as the
    % database tables use. ( see doc setdbprefs )
    % SV: Openearth database fetch has no setdbprefs
    % setdbprefs('DataReturnFormat','structure');

	% SV: Only use ee_*_limited views, so everyone using scripts wrapper can execute queries
    % sql queries
    sql1 = strcat('select t.device_info_serial, t.date_time, a.date_time, ', ...
               ' date_part(''year''::text, t.date_time) AS year, ',...
               ' date_part(''month''::text, t.date_time) AS month, ',...
               ' date_part(''day''::text, t.date_time) AS day, ',...
               ' date_part(''hour''::text, t.date_time) AS hour, ',...
               ' date_part(''minute''::text, t.date_time) AS minute, ',...
               ' date_part(''second''::text, t.date_time) AS second, ',...
               ' t.longitude, t.latitude, t.altitude, t.temperature, t.gps_fixtime, ',...
               ' t.positiondop, t.satellites_used, t.speed, count(a.index) as n_acc_points,  ',...
               ' (t.altitude - elevation.srtm_getvalue(t."location")) AS AGL ',...
               ' from gps.ee_tracking_speed_limited t' , ...
               ' left join gps.ee_acceleration_limited a' , ...
               ' on (t.device_info_serial = a.device_info_serial AND t.date_time = a.date_time)' , ...
               ' where ( t.date_time >= ', start,  ')',...
               ' AND ( t.date_time <= ', stop,    ')' ,...
               ' AND ( t.device_info_serial=' , device , ')', ...
               ' group by   t.device_info_serial, t.date_time, a.date_time, t.speed, t.longitude, ' , ...
               ' t.latitude, t.altitude, t.temperature, t.gps_fixtime, t.positiondop, t.satellites_used, t.location ' , ...
               ' ORDER BY t.date_time' );
    sql2 = strcat('select e.device_info_serial, e.date_time, ', ...
                   ' date_part(''year''::text, e.date_time) AS year, ',...
                   ' date_part(''month''::text, e.date_time) AS month, ',...
                   ' date_part(''day''::text, e.date_time) AS day, ',...
                   ' date_part(''hour''::text, e.date_time) AS hour, ',...
                   ' date_part(''minute''::text, e.date_time) AS minute, ',...
                   ' date_part(''second''::text, e.date_time) AS second, ',...
                   ' e.vsll, e.vbat, e.ssw, e.temperature  ',...
                   ' from gps.ee_energy_limited e' , ...
                   ' where ( e.date_time >= ', start,  ')',...
                   ' AND ( e.date_time <= ', stop,    ')' ,...
                   ' AND ( e.device_info_serial=' , device , ')', ...  %);
                   ' ORDER BY e.date_time' );

    %% run a query
    % get a 'database cursor'
    % this sents the sql command to the database and returns a
    % 'cursor' that can be used to retreive the data in the table.

    % this fetch command actually transfers the data from database table to matlab
    % SV: Openearth database combines exec and fetch into pg_fetch
    curs1 = pg_fetch(conn, sql1);
    curs2 = pg_fetch(conn, sql2);
    %% get the data from the cursor
    % because previously setdbprefs is set to 'structure' devices
    % is a struct with array fields that have the same name as the
    % database columns.  to get the column device_info_serial from
    % the table as an matlab array type tracks.device_info_serial
    tracks = curs1;
    % SV: Openearth returns columns by position and not by name
    % SV: So map position to names
    ener.('date_time') = pg_datenum({curs2{:,2}});
    ener.('ssw') = [curs2{:,11}];
    ener.('vsll') = [curs2{:,9}];
    ener.('vbat') = [curs2{:,10}];

    %% close the database connection
    % ( unless running more queries )
    % SV: Openearth has no close 
    % close(conn); 
    %% copy data
    ID=[tracks{:,1}]; % .device_info_serial;
    Year=[tracks{:,4}]; % .year;
    Month=[tracks{:,5}]; % .month;
    Day=[tracks{:,6}]; % .day;
    Hour=[tracks{:,8}]; % .hour;
    Minute=[tracks{:,8}]; % .minute;
    Second=[tracks{:,9}]; % .second;
    Long=[tracks{:,10}]; % .longitude;
    Lat=[tracks{:,11}]; % .latitude;
    Alt=[tracks{:,12}]; % .altitude;
    Temperature=[tracks{:,13}]; % .temperature;
    AGL=[tracks{:,19}]; % .agl;
    ISpeed=[tracks{:,17}];
    ISpeed =ISpeed*3.6; % .speed*3.6; %convert speed from m/s to km/hr
    nrAcc=[tracks{:,18}]; % .n_acc_points;
    satellites_used = [tracks{:,16}];
    gps_fixtime = [tracks{:,14}];

    ETime=datenum(ener.date_time)-734868; %datenum('2012-01-01 00:00:00')=734869

    Filename=[num2str(ID(1)) '_'];
    if Day(1) < 10
        Filename=[Filename '0' num2str(Day(1))]; 
    else
        Filename=[Filename num2str(Day(1))]; 
    end
    if Month(1) < 10
        Filename=[Filename '0' num2str(Month(1))]; 
    else
        Filename=[Filename num2str(Month(1))]; 
    end    
    Filename=[Filename num2str(Year(1)) '_']; 
    if Day(end) < 10
        Filename=[Filename '0' num2str(Day(end))]; 
    else
        Filename=[Filename num2str(Day(end))]; 
    end
    if Month(end) < 10
        Filename=[Filename '0' num2str(Month(end))]; 
    else
        Filename=[Filename num2str(Month(end))]; 
    end    
    Filename=[Filename num2str(Year(end))]; 


    dom=[0 31 59 90 120 151 181 212 243 273 304 334]; %doy of first of the month
    domLY=[0 31 60 91 121 152 182 213 244 274 305 335]; % dom for leap year

    for i=1:length(Long)
       if Year(i)/4==floor(Year(i)/4)
         LY=1; %leap year
         doy(i)=domLY(Month(i))+Day(i);
       else
         LY=0;
         doy(i)=dom(Month(i))+Day(i);
       end
       Time(i)=doy(i)+(Hour(i)+(Minute(i)+Second(i)/60)/60)/24; 
       Dist(i) = distWB([Lat(i) Long(i)],[42.719741  11.517136]);
       if i>1
              Period=Time(i)-Time(i-1);
              TSpeed(i)= distWB([Lat(i) Long(i)],[Lat(i-1) Long(i-1)])...
                                                ./Period/24; %[km/h]
               if nrAcc(i)>5
                   TotNrAcc(i)=TotNrAcc(i-1)+1;
               else
                   TotNrAcc(i)=TotNrAcc(i-1);
               end
       else
          TSpeed(i)=NaN;
          TotNrAcc(i)=1;
       end
    end

    %%Make overview figure
         %figure for SSW
        SSW=ener.ssw';
        clear SC
        for u=1:length(ener.ssw)
            SC(u,1:4)=NaN;
            if (SSW(u)==1)|(SSW(u)==3)|(SSW(u)==5)|(SSW(u)==7)|(SSW(u)==9) ...
                    |(SSW(u)==11)|(SSW(u)==13)|(SSW(u)==15) 
                 SC(u,1)=1;
            end
            if (SSW(u)==2)|(SSW(u)==3)|(SSW(u)==6)|(SSW(u)==7)|(SSW(u)==10) ...
                    |(SSW(u)==11)|(SSW(u)==14)|(SSW(u)==15) 
                 SC(u,2)=1;
            end
            if (SSW(u)==4)|(SSW(u)==5)|(SSW(u)==6)|(SSW(u)==7)|(SSW(u)==12) ...
                    |(SSW(u)==13)|(SSW(u)==14)|(SSW(u)==15) 
                 SC(u,3)=1;
            end
            if (SSW(u)==8)|(SSW(u)==9)|(SSW(u)==10)|(SSW(u)==11)|(SSW(u)==12) ...
                    |(SSW(u)==13)|(SSW(u)==14)|(SSW(u)==15) 
                 SC(u,4)=1;
            end
        end
        HisTSpeed=[]; HisAGL=[];HisISpeed=[];
        Times=length(Time);
        for u=2:Times
           if TSpeed(u)>2
             HisTSpeed=[HisTSpeed; TSpeed(u)]; 
           end
           if ISpeed(u)>2
             HisISpeed=[HisISpeed; ISpeed(u)]; 
           end
           if AGL(u)>10
               HisAGL=[HisAGL ; AGL(u)];
           end
        end
    toc
    tic
    % On server there is no display
    % scrsz = get(0,'ScreenSize');
    % figure('Position',[30 scrsz(4)/20 scrsz(3)-50 scrsz(4)/1.2]);
    figure('visible','off');
        subplot(4,4,1)
        plot(Time,Long,'k.'); xlabel(['\fontsize{12}','time doy']); ylabel(['\fontsize{12}','longitude']),TITLE (['\fontsize{12}','sensor :', num2str(ID(1))]); grid on
        subplot(4,4,2)
        plot(Time,Lat,'k.');xlabel(['\fontsize{12}','time doy']); ylabel(['\fontsize{12}','latitude']); grid on
        subplot(4,4,3)
        plot(Time,Alt,'k.');xlabel(['\fontsize{12}','time doy']); ylabel(['\fontsize{12}','altitude [m ASL]']); grid on   
        subplot(4,4,4)
        plot(Long,Lat,'k.');xlabel(['\fontsize{12}','longitude']); ylabel(['\fontsize{12}','latitude']); grid on   
        subplot(4,4,5)
        plot(Time,TSpeed,'r.'); xlabel(['\fontsize{12}','time doy']); ylabel(['\fontsize{12}','Speed[km/h] I=blue,T=red']); grid on
        hold on
        plot(Time,ISpeed,'b.');
        subplot(4,4,6)
        plot(Time,nrAcc,'k.-');xlabel(['\fontsize{12}','time doy']); ylabel(['\fontsize{12}','nr acc. samples'])
        subplot(4,4,7)
        plot(Time,tracks.satellites_used,'k.');xlabel(['\fontsize{12}','time doy']); ylabel(['\fontsize{12}','nr Satellites'])
        subplot(4,4,8)
        plot(Time,tracks.gps_fixtime,'k.');xlabel(['\fontsize{12}','time doy']); ylabel(['\fontsize{12}','TimeToFix'])
        subplot(4,4,9)    
        plot(ETime, ener.vsll, 'k.'); ylabel(['\fontsize{12}','SolVoltage [V]']); ylim([-0.8 3]); grid on; title (['\fontsize{12}','sensor :', num2str(ID(1))]); 
        hold on
        plot(ETime, -0.8+0.1*SC(:,1), 'r.');
        plot(ETime, -0.8+0.3*SC(:,2), 'b.');
        plot(ETime, -0.8+0.5*SC(:,3), 'k.');
        plot(ETime, -0.8+0.7*SC(:,4), 'g.');
        subplot(4,4,10)
        plot(ETime, ener.vbat, 'k.'); ylabel(['\fontsize{12}','BatteryVoltage [V]']); ylim([3.2 4.2]); grid on        
        subplot(4,4,11)
        plot(Time,Temperature,'k.');xlabel(['\fontsize{12}','time doy']); ylabel(['\fontsize{12}','Temperature'])
        subplot(4,4,12)
        plot(Time(2:end),log10((Time(2:end)-Time(1:end-1 ))*24*60),'k.');
        xlabel(['\fontsize{12}','time doy']); ylabel(['\fontsize{12}','Meas Interval log[min]'])
        subplot(4,4,13)
        plot(Time(2:end),log10((Time(2:end)-Time(1:end-1 ))*24*60),'k.');
        xlabel(['\fontsize{12}','dataNr']); ylabel(['\fontsize{12}','interval log[min]'])
        plot(Time, 1:length(Long),'k.');ylabel(['\fontsize{12}','Nr datapoint GPS=black,Acc=red']); xlabel(['\fontsize{12}','time doy']); grid on 
        hold on
        plot(Time, TotNrAcc,'r.');
        Bins=[2.5:5:122.5];
        subplot(4,4,14)
        hist(HisTSpeed,Bins);xlabel(['\fontsize{12}','traject speed km/h']), title(['\fontsize{12}','freq distr'])
        subplot(4,4,15)
        hist(HisISpeed,Bins);xlabel(['\fontsize{12}','point speed km/h']), title(['\fontsize{12}','freq distr'])
        Bins=[1.1:0.1:3.3];
        subplot(4,4,16)
        hist(log10(HisAGL),Bins); xlabel(['\fontsize{12}','log(AGL) [m]']), title(['\fontsize{12}','freq distr'])
        saveas(gcf,['S',Filename, '.fig'])
        set(gcf, 'PaperUnits', 'inches');
        set(gcf, 'PaperPosition', [0 0 imgWidth imgHeight]);
        print ('-dpng', '-r100', ['S', Filename])
    toc


    tic
    %% Make kmz-file
    numTime = datenum(Year,Month,Day,Hour,Minute,Second);
    Ix = find(Year<1900|Year>2015);
    numTime(Ix)=NaN; 
    clear Ix;

    dateTimeFormat = 'yyyy-mm-ddTHH:MM:SSZ';

    % filename for kmz file
    Filename=['S',Filename, 'b.kmz']
    % open the kml file, write the header
    fh = ge_output_start(Filename);
     kmlStr_line=''; % start with empty kml
     kmlStr = '';


    % set the icontype   
    iconStr = ['http://maps.google.com/','mapfiles/kml/pal2/icon26.png'];

    % Set the Colortables (these are some examples that you can use)
    Colortable(:,:,1)=['ffffff50';'fffdd017';'ffc68e17'; 'ff733c00']; %OK geel -donkergeel
    Colortable(:,:,2)=['ffF7E8AA';'ffF9E070';'ffFCB514'; 'ffA37F14']; %OK geel -geelgroen
    Colortable(:,:,3)=['ffffa550';'ffeb4100';'ffff0000'; 'ff7d0000']; %OK oranje rood
    Colortable(:,:,4)=['ff5a5aff';'ff0000ff';'ff0000af'; 'ff00004b']; %OK fel blauw
    Colortable(:,:,5)=['ffbeffff';'ff00ffff';'ff00b9b9'; 'ff007373']; %OK licht blauw
    Colortable(:,:,6)=['ff8cff8c';'ff00ff00';'ff00b900'; 'ff004b00']; % fel groen
    Colortable(:,:,7)=['ffff8cff';'ffff00ff';'ffa500a5'; 'ff4b004b']; % OK paars
    Colortable(:,:,8)=['ffAADD96';'ff60C659';'ff339E35'; 'ff3A7728']; %OK groen
    Colortable(:,:,9)=['ffFFD3AA';'ffF9BA82';'ffF28411'; 'ffBF5B00']; %OK 
    Colortable(:,:,10)=['ffC6C699';'ffAAAD75';'ff6B702B'; 'ff424716']; %OK 
    Colortable(:,:,11)=['ffE5BFC6';'ffD39EAF';'ffA05175'; 'ff7F284F']; %OK  roze-paars
    Colortable(:,:,12)=['ffdadada';'ffc3c3c3';'ff999999'; 'ff3c3c3c']; % van wit naar donkergrijs
    Colortable(:,:,13)=['ffC6B5C4';'ffA893AD';'ff664975'; 'ff472B59']; %OK blauwpaars
    Colortable(:,:,14)=['ffC1D1BF';'ff7FA08C';'ff5B8772'; 'ff21543F']; %OK grijsgroen
    Colortable(:,:,15)=['ff000000';'ff000000';'7d000000'; '10000000']; %black

	% SV: Colors variable contains indices of ColorTable
    colortable1 = Colortable(:,:,Colors(k));

    %This is the line that connects the points
    kmlStr_line = [kmlStr_line,ge_plot(Long, Lat,...
                            'lineColor', colortable1(1,:),...
                            'lineWidth',1)];
    ge_output_string(fh, kmlStr_line);

    % FOR-loop to add every datapoint to the kml-file
    for i=2:length(Long)-1

        % set time stamp
        tNumPrev = datenum(numTime(i-1));
        tNumNow = datenum(numTime(i));
        tNumNext = datenum(numTime(i+1));
        if isnan(tNumPrev)&&~isnan(tNumNow)
            tStart = datestr(tNumNow+datenum([0,0,0,-1,0,0]),dateTimeFormat);
        elseif ~isnan(tNumPrev)&&~isnan(tNumNow)
            tStart = datestr(mean([tNumPrev;tNumNow]),dateTimeFormat);
        else
            clear tNumPrev
            clear tNumNow
            clear tNumNext
            clear tStart
            clear tStop
            continue
        end

        if isnan(tNumNext)&&~isnan(tNumNow)
            tStop = datestr(tNumNow+datenum([0,0,0,+1,0,0]),dateTimeFormat);
        elseif ~isnan(tNumNext)&&~isnan(tNumNow)
            tStop = datestr(mean([tNumNext;tNumNow]),dateTimeFormat);
        else
            clear tNumPrev
            clear tNumNow
            clear tNumNext
            clear tStart
            clear tStop
            continue
        end

        % if available use CSpeedGPS (instanteneous)for colors,
        % else CSpeed (trajectory)
        % choose the speedclasses as you like
        %if isnan(CSpeedGPS(i))
        if isempty(ISpeed)
            SpeedClass=4;
            if TSpeed(i)<20
                SpeedClass=3;
                if TSpeed(i)<10
                    SpeedClass=2;
                    if TSpeed(i)<5
                        SpeedClass=1;
                    end;
                end;
            end;
        else
            SpeedClass=4;
            if ISpeed(i)<20
                SpeedClass=3;
                if ISpeed(i)<10
                    SpeedClass=2;
                    if ISpeed(i)<5
                        SpeedClass=1;
                    end;
                end;
            end;
        end


        if  ~isnan(Alt(i))
            colortable=colortable1;
            kmlStr = [kmlStr,ge_point(Long(i),...
                Lat(i),...
                Alt(i),...
                'iconURL',iconStr,...
                'altitudeMode','absolute',...
                'extrude',1,...
                'name','',...
                'iconColor',colortable(SpeedClass,:),...
                'iconScale',0.3+log10(max(1,Alt(i)))/10,...
                'pointDataCell',{'UTM time',datestr(tNumNow,0);...
                'sensor ID',num2str(ID(i));...
                'Julian time', num2str(Time(i));...
                'record index',num2str(i);...
                'lat long',[num2str(Long(i))...
                '  ' num2str(Lat(i))];...
                'altitude [m]',num2str(Alt(i));...
                'Dist [km]', num2str(Dist(i));...
                'T-I Speed [km/h]',[num2str(TSpeed(i)) '  ' num2str(ISpeed(i))];},...
                'timeSpanStart',tStart,...
                'timeSpanStop',tStop)];
        else
            colortable=Colortable(:,:,9);
            colortable=colortable1;
            kmlStr = [kmlStr,ge_point(Long(i),...
                Lat(i),...
                10,...
                'iconURL',iconStr,...
                'altitudeMode','relativeToGround',...
                'extrude',1,...
                'name','',...
                'iconColor',colortable(SpeedClass,:),...
                'iconScale',0.3,...
                'pointDataCell',{'UTM time',datestr(tNumNow,0);...
                'sensor ID',num2str(ID(i));...
                'Julian time', num2str(Time(i));...
                'record index',num2str(i);...
                'lat long',[num2str(Long(i))...
                '  ' num2str(Lat(i))];...
                'altitude [m]',num2str(Alt(i));...
                'Dist [km]', num2str(Dist(i));...
                'T-I Speed [km/h]',[num2str(TSpeed(i)) '  ' num2str(ISpeed(i))];},...
                'timeSpanStart',tStart,...
                'timeSpanStop',tStop)];
        end
        ge_output_string(fh, kmlStr);
        kmlStr=[];
    end

    % write the footer, close the file.
    ge_output_finish(fh);
    kmlStr=[];
    fh=[];
end
toc 

