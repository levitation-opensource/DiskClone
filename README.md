### Raw disk clone tool

A free and open-source raw disk clone tool written in Python. It creates a direct sector by sector block copy. It is able to skip bad sectors. No filesystem inspection is involved, so it is filesystem independent.

Use this tool when you are running on a server OS and do not want to pay for commercial tools. The operation mechanism of this tool is very simple and straightforward.

It is also helpful in cases where your alternative tool would stop working upon encountering bad sectors. Some commercial disk clone tools cannot handle bad sectors for some reason.

Note: You cannot use this tool to clone the active OS disk since it assumes the source disk is made readonly before cloning starts.

INSPECT THE SOURCE CODE, UNDERSTAND WHAT IT DOES AND VERIFY THAT THE CODE IS CORRECT. THEN USE WITH CARE. I AM NOT RESPONSIBLE IN ANY WAY IF YOU LOSE YOUR DATA. ALL DATA ON DESTINATION DISK WILL BE OVERWRITTEN.

---

### Version 1.0.2 Update

- The script now checks if the second argument (`DestinationDisk`) is a physical disk path (e.g., `\\\\.\\PhysicalDrive1`, `/dev/sdb`) or a regular file path.
- You can now clone a disk to a disk image file by specifying a file path as the destination.

---

### Usage

```sh
python diskclone.py SourceDisk DestinationDisk
```

**Under Windows:**

- Clone to another disk:
  ```
  python diskclone.py "\\\\.\\PhysicalDrive0" "\\\\.\\PhysicalDrive1"
  ```
- Clone to an image file:
  ```
  python diskclone.py "\\\\.\\PhysicalDrive0" "backup.img"
  ```

**Under Linux:**

- Clone to another disk:
  ```
  python diskclone.py "/dev/sda" "/dev/sdb"
  ```
- Clone to an image file:
  ```
  python diskclone.py "/dev/sda" "backup.img"
  ```

A Python 2 or 3 installation is required. There are package dependencies:
 - psutil
 - pywin32 (under Windows OS only)

---

### Roadmap

Bad sector recovery functionality. Sometimes bad sectors can be recovered by attempting to read them repeatedly. The necessary changes to existing code are essentially just a few lines.

---

### Licence
Version 1.0.2  
Copyright: Roland Pihlakas, 2023, roland@simplify.ee & DrcLab, 2025, hanaloginstruments@gmail.com  
Licence: LGPL 2.1  
You can obtain a copy of this free software from https://github.com/levitation-opensource/DiskScan/

---

### State
Ready to use. Maintained and in active use.
