# mt4_geo_report.py
# Execution step of the Script

##### Manual Mode #####

1. Download the MT4 Server log to .\MT4_Server_Log\47.88.153.124\
2. Open a powershell prompt
3. Execute below command
cd 'J:\GITISS\Application and Infrastructure Support\Team Folder\py_tools';
.\PortablePython-3.7.4\App\Python\python.exe .\mt4_geo_report.py

OR

cd 'J:\GITISS\Application and Infrastructure Support\Team Folder\py_tools';
.\PortablePython-3.7.4\App\Python\python.exe .\mt4_geo_report.py <YYYYMMDD>


4. Input the YYYYMMDD / YYYYMM for the date 
5. Collect the report in .\report dir


##### Auto Mode #####

1. Download the MT4 Server log to .\MT4_Server_Log\47.88.153.124\
2. Setup a schedule job with below commands
cd 'J:\GITISS\Application and Infrastructure Support\Team Folder\py_tools';
.\PortablePython-3.7.4\App\Python\python.exe .\mt4_geo_report.py auto

3. Input the YYYYMMDD / YYYYMM for the date 
4. Collect the report in .\report dir
