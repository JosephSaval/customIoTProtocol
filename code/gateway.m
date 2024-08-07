%Authors: Joseph W Saval & Ryan Easter with code taken from Prof. Foster
%Purpose: Transfer data between a micro:bit gateway & an MQTT broker.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% UI CONFIG/INIT
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

app = uifigure;
app.Position = [500, 500, 400, 100];
app.Resize = 'off';

% Request Letter Display Node 1 Button
bX = uibutton(app);
bX.Position = [10,40,100,50];
bX.Text = 'Node 1 Disp';
bX.Tag = 'lDisp1';  % hidden value that can store useful data tied to an object
bX.FontSize = 20;

% Request Letter Display Node 2 Button
bY = uibutton(app);
bY.Position = [120,40,100,50];
bY.Text = 'Node 2 Disp';
bY.Tag = 'lDisp2';  % hidden value that can store useful data tied to an object
bY.FontSize = 20;

% Request Letter Display Node 3 Button
bZ = uibutton(app);
bZ.Position = [230,40,100,50];
bZ.Text = 'Node 3 Disp';
bZ.Tag = 'lDisp13';  % hidden value that can store useful data tied to an object
bZ.FontSize = 20;

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% COM PORT CONFIG/INIT
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%Need to check device manager for this value.
comport = "COM3";

clear sp; % deletes old serial port item from the workspace to make it easier to rerun the script
sp = serialport(comport, 115200);
flush(sp); % clear any old data
configureTerminator(sp,"CR/LF");
setappdata(app,'sp',sp); %Create global variable sp under the app object

% After the serial port object is created, you can click on it in the
% Workspace window, and MATLAB will show a configuration screen. This is a
% good way to see all the fields that can be modified.
sp.DataBits=8;
sp.FlowControl = 'none';
sp.StopBits = 1.0;

% Calback to readport - triggers when a '\r\n' is read (I think)
configureCallback(sp, "terminator", @(src,event)readport(src, event,app));

%Callbacks to transfer MQTT requests - SHOULD BE REPLACED WITH CALLBACKS
%FOR MQTT DATA READ
bX.ButtonPushedFcn = {@sendL1,sp};
bY.ButtonPushedFcn = {@sendL2,sp}; 
bZ.ButtonPushedFcn = {@sendL3,sp};

% Read messages from micro:bit gateway on the COM Port
function readport( port,~,app)
    fprintf('Got %d bytes\n', port.BytesAvailable);
    data = char(readline(port));
    fprintf('Receiving: %s\n', data);
    
    %Detect C type message (Accelerometer Data)
    if data(1) == 'C'
        sendC(data);
    end
    %Detect N type Message (Node connect message)
    if data(1) == 'N'
        sendN(data);
    end
    %Detect A type Message (Ack for letter display messages) 
    if data(1) == 'A'
        sendA(data)
    end
end

% Sends C data (accelerometer data) read from the COM port over MQTT
function sendC(data)
    value = sscanf(data, '%c:%d:%d:%d:%d');
    
    %Node ID is value(2), X is value(3), etc.
    fprintf("Node: %d, X: %d, Y: %d, Z: %d\n", value(2), value(3), value(4), value(5))

    %TRANSFER ACCELEROMETER DATA TO CLOUD HERE

end

%Notifies the cloud that a node has been connected
function sendN(data)
    value = sscanf(data, '%c:%d');
    fprintf("Node %d Connected!\n", value(2))
end

%Notifies the cloud that a node has successfully recieved & displayed a
%requested letter
function sendA(data)
    value = sscanf(data, '%c:%d:%c');

    fprintf("Letter '%c' Displayed on Node %d!\n", value(3), value(2))
end

%Sends a char to node1
function sendL1(s,e,sp)
    msg = sprintf('L%d%c',1,'C');
    fprintf("Sending: %s\n", msg);
    sp.write(msg,'string');
end

%Sends a char to node1
function sendL2(s,e,sp)
    msg = sprintf('L%d%c',2,'C');
    fprintf("Sending: %s\n", msg);
    sp.write(msg,'string');
end

%Sends a char to node1
function sendL3(s,e,sp)
    msg = sprintf('L%d%c',3,'C');
    fprintf("Sending: %s\n", msg);
    sp.write(msg,'string');
end