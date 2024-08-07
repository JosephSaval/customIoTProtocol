%Final Project - Cloud Layer 
% Author: Ryan Easter
% Purpose:
 

clear myMQTT % closes an existing connection - MATLAB crashes if trying to open a second identical MQTT connection.

% code to connect to an MQTT broker
myMQTT = mqttclient('tcp://broker.hivemq.com');

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% UI CONFIG/INIT
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

app = uifigure;
app.Position = [0, 0, 1200, 700];
app.Resize = 'off';

%Accelerometer Graph Node 1
n1Disp = uiaxes(app);
n1Disp.Position = [600,310,590,300];
n1Disp.Title.String = "Node 1 Accelerometer Readings";
ylabel(n1Disp, 'Measurement')
xlabel(n1Disp, 'Reading Number')
setappdata(n1Disp,'n1_vals',[])
setappdata(n1Disp, 'n1_vals_count_max', 0);
setappdata(n1Disp, 'n1_vals_count_min', 0);
setappdata(app,'n1Graph',n1Disp);

%Accelerometer Graph Node 2
n2Disp = uiaxes(app);
n2Disp.Position = [10,10,590,300];
n2Disp.Title.String = "Node 2 Accelerometer Readings";
ylabel(n2Disp, 'Measurement')
xlabel(n2Disp, 'Reading Number')
setappdata(n2Disp,'n2_vals',[])
setappdata(n2Disp, 'n2_vals_count_max', 0);
setappdata(n2Disp, 'n2_vals_count_min', 0);
setappdata(app,'n2Graph',n2Disp);

%Accelerometer Graph Node 3
n3Disp = uiaxes(app);
n3Disp.Position = [600,10,590,300];
n3Disp.Title.String = "Node 3 Accelerometer Readings";
ylabel(n3Disp, 'Measurement')
xlabel(n3Disp, 'Reading Number')
setappdata(n3Disp,'n3_vals',[])
setappdata(n3Disp, 'n3_vals_count_max', 0);
setappdata(n3Disp, 'n3_vals_count_min', 0);
setappdata(app,'n3Graph',n3Disp);

% Request Letter Display Node 1 Button
bX = uibutton(app);
bX.Position = [10,500,100,50];
bX.Text = 'Node 1 Disp';
bX.Tag = 'lDisp1';  % hidden value that can store useful data tied to an object
bX.FontSize = 20;

% Request Letter Display Node 2 Button
bY = uibutton(app);
bY.Position = [120,500,100,50];
bY.Text = 'Node 2 Disp';
bY.Tag = 'lDisp2';  % hidden value that can store useful data tied to an object
bY.FontSize = 20;

% Request Letter Display Node 3 Button
bZ = uibutton(app);
bZ.Position = [230,500,100,50];
bZ.Text = 'Node 3 Disp';
bZ.Tag = 'lDisp13';  % hidden value that can store useful data tied to an object
bZ.FontSize = 20;

% Channel Subscriptions
mySubN1 = subscribe(myMQTT,'SAVAEASTN1','Callback',@myMQTT_Callback);
mySubN2 = subscribe(myMQTT,'SAVAEASTN2','Callback',@myMQTT_Callback);
mySubN3 = subscribe(myMQTT,'SAVAEASTN3','Callback',@myMQTT_Callback);
mySubACK = subscribe(myMQTT,'SAVAEASTack','Callback',@myMQTT_Callback);
mySubLR = subscribe(myMQTT,'SAVAEASTLetterReq','Callback',@myMQTT_Callback);

% This function is automatically called by MATLAB until you close MATLAB,
% unsubscribe, or the connection times out.
%Callback for Node 1 Channel
function myMQTT_Callback(topic, msg)
    
   %Node 1
    if strcmp(topic,'SAVAEASTN1' )
        value = sscanf(msg, '%c:%d:%d:%d:%d');
        graph_n1(app,value(3), value(4), value(5))
        fprintf("Node: %d, X: %d, Y: %d, Z: %d\n", value(2), value(3), value(4), value(5))
    end

    %Node 2
     if strcmp(topic,'SAVAEASTN2' )
        value = sscanf(msg, '%c:%d:%d:%d:%d');
        graph_n2(app,value(3), value(4), value(5))
       fprintf("Node: %d, X: %d, Y: %d, Z: %d\n", value(2), value(3), value(4), value(5))
     end

     %Node 3
      if strcmp(topic,'SAVAEASTN3' )
       value = sscanf(msg, '%c:%d:%d:%d:%d');
        graph_n3(app,value(3), value(4), value(5))
       fprintf("Node: %d, X: %d, Y: %d, Z: %d\n", value(2), value(3), value(4), value(5))
      end

      %ACK
       if strcmp(topic,'SAVAEASTackC' )
        value = sscanf(data, '%c:%d');
        fprintf("Node %d Connected!\n", value(2))
       end

       %Letter Request
        if strcmp(topic,'SAVAEASTLetterReq' )
        value = sscanf(data, '%c:%d:%c');
        write(myMQTT, 'SAVAEASTLetterSend', 'H');
        fprintf("Letter 'H' Displayed on Node %d!\n", value(3), value(2))
        end
end


%Node 1 Accelerometer Graph
function graph_n1(app, dataValx, dataValy, dataValz)
    MAXPOINTS = uint32(20);

    % Get copies of the global data
    myplot = getappdata(app, 'n1Graph');

    n1_vals = getappdata(myplot,'n1_vals');
    n1_vals_count_min = getappdata(myplot,'n1_vals_count_min');
    n1_vals_count_max = getappdata(myplot,'n1_vals_count_max'); %starts at 0, so it shouldn't be affected

    % read value from user
    new_n1x = dataValx;
    new_n1y = dataValy;
    new_n1z = dataValz;

    if (isnumeric(new_n1x))   % If that data isn't valid
        n1_vals_count_max = n1_vals_count_max + 1;
        if (size(n1_vals,2) >= MAXPOINTS) % already have 20 readings, shift window
            n1_vals = [n1_vals(2:MAXPOINTS), new_n1];  
            n1_vals_count_min = n1_vals_count_max-19;
            n1span = MAXPOINTS;
        else  % still accumulating first 20 readings, just append
            n1_vals = [n1_vals, new_n1];
            n1_vals_count_min = 1;
            n1span = n1_vals_count_max;
        end
 
        % new point added, get a handle to the plot and update
        
        plot(myplot, new_n1x);
        hold on
        plot(myplot, new_n1y); %This last part should work and plot all 3 values while keeping the myplot (x) the same (keeping the window the same)
        hold on
        plot(myplot, new_n1z);
        hold off
        n1ticks(myplot,1:n1span)
        if (n1span > 1)
            n1lim(myplot,[1 uint32(n1span)])
        end
        n1ticklabels(myplot,string(n1_vals_count_min:n1_vals_count_max))    

        % Save updated data
        setappdata(myplot, 'n1_vals', n1_vals);                    
        setappdata(myplot, 'n1_vals_count_max', n1_vals_count_max);
        setappdata(myplot, 'n1_vals_count_min', n1_vals_count_min);
    end
end