### Raw disk clone tool

A free and open-source raw disk clone tool written in Python. It creates a direct sector by sector block copy. It is able to skip bad sectors. No filesystem inspection is involved, so it is filesystem independent. 

Use this tool when you are running on a server OS and do not want to pay for commercial tools. The operation mechanism of this tool is very simple and straightforward. 

It is also helpful in cases where your alternative tool would stop working upon encountering bad sectors. Some commercial disk clone dools cannot handle bad sectors for some reason.

Note: You cannot use this tool to clone the active OS disk since it assumes the source disk is made readonly before cloning starts.

INSPECT THE SOURCE CODE, UNDERSTAND WHAT IT DOES AND VERIFY THAT THE CODE IS CORRECT. THEN USE WITH CARE. I AM NOT RESPONSIBLE IN ANY WAY IF YOU LOSE YOUR DATA. ALL DATA ON DESTINATION DISK WILL BE OVERWRITTEN.


### Usage

python diskclone.py SourceDisk DestinationDisk
<br>
<br>Under Windows:
<br>python diskclone.py "\\.\PhysicalDrive0" "\\.\PhysicalDrive1"
<br>or
<br>Under Linux:
<br>python diskclone.py "/dev/ploop12345" "/dev/ploop67890"


A Python 2 or 3 installation is required. There are package dependencies:
<br> - psutil
<br> - pywin32 (under Windows OS only)


### Roadmap

Bad sector recovery functionality. Sometimes bad sectors can be recovered by attempting to read them repeatedly. The necessary changes to existing code are essentially just a few lines.


### Licence
Version 1.0.1
<br>Copyright: Roland Pihlakas, 2023, roland@simplify.ee
<br>Licence: LGPL 2.1
<br>You can obtain a copy of this free software from https://github.com/levitation-opensource/DiskScan/


### State
Ready to use. Maintained and in active use.


<br>
<br>
<br>
<br>

[![Analytics](https://ga-beacon.appspot.com/UA-351728-28/DiskClone/README.md?pixel)](https://github.com/igrigorik/ga-beacon)    
