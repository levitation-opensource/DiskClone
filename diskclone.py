# -*- coding: utf-8 -*-

#
# Author: Roland Pihlakas, 2023
#
# roland@simplify.ee
#
# Version 1.0.1
# 
# Roland Pihlakas licenses this file to you under the GNU Lesser General Public License, ver 2.1.
# See the LICENSE file for more information.
#

import os
import sys
import time
import struct


# first argument is the python script name
if len(sys.argv) >= 3:

  print("")
  print("Starting...")

  # NB! for finding out drive order numbers used in the physical disk name, do NOT rely on AIDA64, instead use the drive order from Windows Disk Management or diskpart
  src_disk_name = sys.argv[1]
  dest_disk_name = sys.argv[2]

else:   #/ if len(sys.argv) >= 3:

  print('')
  print('')
  print('Description:')
  print('')
  print('Raw disk clone tool')
  print('')
  print('A free and open-source raw disk clone tool written in Python. It creates a direct sector by sector block copy. It is able to skip bad sectors. No filesystem inspection is involved, so it is filesystem independent.')
  print('')
  print('Use this tool when you are running on a server OS and do not want to pay for commercial tools. The operation mechanism of this tool is very simple and straightforward.')
  print('')
  print('It is also helpful in cases where your alternative tool would stop working upon encountering bad sectors. Some commercial disk clone tools cannot handle bad sectors for some reason.')
  print('')
  print('Note: You cannot use this tool to clone the active OS disk since it assumes the source disk is made readonly before cloning starts.')
  print('')
  print('INSPECT THE SOURCE CODE, UNDERSTAND WHAT IT DOES AND VERIFY THAT THE CODE IS CORRECT. THEN USE WITH CARE. I AM NOT RESPONSIBLE IN ANY WAY IF YOU LOSE YOUR DATA. ALL DATA ON DESTINATION DISK WILL BE OVERWRITTEN.')
  print('')
  print('')
  print('Usage:')
  print('')
  print('python diskclone.py SourceDisk DestinationDisk')
  print('')
  print('Under Windows:')
  print(r'python diskclone.py "\\.\PhysicalDrive0" "\\.\PhysicalDrive1"')
  print('or')
  print('Under Linux:')
  print(r'python diskclone.py "/dev/ploop12345" "/dev/ploop67890"')
  print('')
  print('')
  print('A Python 2 or 3 installation is required. There are package dependencies:')
  print(' - psutil')
  print(' - pywin32 (under Windows OS only)')
  print('')
  print('')
  print('Version 1.0.1')
  print('Copyright: Roland Pihlakas, 2023, roland@simplify.ee')
  print('Licence: LGPL 2.1')
  print('You can obtain a copy of this free software from https://github.com/levitation-opensource/DiskClone/')
  print('')
  print('')

  sys.exit()

#/ if len(sys.argv) >= 3:



if os.name == "nt":
  try:
    import win32api
  except Exception as msg:
    print(str(msg))
    print("run pip install pywin32")
    pass
    
    
def get_idle_time():
  try:
    return (win32api.GetTickCount() - win32api.GetLastInputInfo()) / 1000
  except:
    return sys.maxsize
    

try:
  import psutil

  if hasattr(psutil, "Process"):
    pid = os.getpid()

    p = psutil.Process(pid)
    
    # set to lowest  priority, this is windows only,  on Unix  use  ps.nice(19)
    # On UNIX this is a number which usually goes from -20 to 20. The higher the nice value, the lower the priority of the process.
    # https://psutil.readthedocs.io/en/latest/#psutil.Process.nice
    # p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS if os.name == "nt" else 10)  # TODO: config
    p.nice(psutil.IDLE_PRIORITY_CLASS if os.name == "nt" else 20)  # TODO: config
    # p.nice(psutil.IDLE_PRIORITY_CLASS)

    # On Windows only *ioclass* is used and it can be set to 2
    # (normal), 1 (low) or 0 (very low).
    p.ionice(0 if os.name == "nt" else psutil.IOPRIO_CLASS_IDLE)
    # p.ionice(2 if os.name == "nt" else psutil.IOPRIO_CLASS_BE)  # BE = best effort = normal
    
    print("Priorities set...")
    
  #/ if psutil.Process:
except Exception as msg:
  print(str(msg))
  print("run pip install psutil")
  pass


if os.name == "nt":
  try:  # psutil fails to set IO priority under Windows for some reason
    import win32process
  
    # NB! Sometimes SetPiorityClass is not enough to set IO priority
    # NB! SetThreadPriority must be called before SetPriorityClass else SetThreadPriority will throw
  
    # 0x00010000: THREAD_MODE_BACKGROUND_BEGIN
    # Begin background processing mode. The system lowers the resource scheduling priorities of the thread so that it can perform background work without significantly affecting activity in the foreground.
    # This value can be specified only if hThread is a handle to the current thread. The function fails if the thread is already in background processing mode.
    # Windows Server 2003:  This value is not supported
    # win32process.SetThreadPriority(-2, 0x00010000)  # NB! -2: win32api.GetCurrentThread()
   
    # 0x00100000: PROCESS_MODE_BACKGROUND_BEGIN
    # Begin background processing mode. The system lowers the resource scheduling priorities of the process (and its threads) so that it can perform background work without significantly affecting activity in the foreground.
    # This value can be specified only if hProcess is a handle to the current process. The function fails if the process is already in background processing mode.
    # Windows Server 2003 and Windows XP:  This value is not supported.
    # https://docs.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-setpriorityclass
    win32process.SetPriorityClass(-1, 0x00100000)   # NB! -1: win32api.GetCurrentProcess()
 
  except Exception as msg:
    print(str(msg))
    print("run pip install pywin32")
    pass


print("")
print("")
print("WARNING!!! ALL DATA ON DISK {} WILL BE OVERWRITTEN.".format(dest_disk_name))
print("TYPE 'YES' AND PRESS ENTER TO CONTINUE, OR PRESS CTRL+C TO CANCEL:")
confirmation = input()
if confirmation != "YES":
  quit()

print("")
print("")
print("RUN THE FOLLOWING COMMANDS IN A SEPARATE COMMAND CONSOLE TO MAKE THE SOURCE DISK READONLY AND TO CLEAN THE DESTINATION DISK:")
if os.name == "nt":
  print("sync")
  print("diskpart")
  print("select disk {}".format(src_disk_name[-1:]))
  print("attribute disk set readonly")
  print("select disk {}".format(dest_disk_name[-1:]))
  print("clean")
  print("exit")
else:
  print("sync")
  print("sudo hdparm -F -r1 {}".format(src_disk_name))
  print("sudo wipefs -a {}".format(dest_disk_name))
print("")
print("PRESS ENTER TO CONTINUE:")
dummy = input()
print("")


if os.name == "nt":

  try:
    import win32file
    import winioctlcon
  
    # https://stackoverflow.com/questions/9901792/wmi-win32-diskdrive-to-get-total-sector-on-the-physical-disk-drive
    src_f = win32file.CreateFile(src_disk_name, win32file.GENERIC_READ, win32file.FILE_SHARE_READ | win32file.FILE_SHARE_WRITE, None, win32file.OPEN_EXISTING, win32file.FILE_ATTRIBUTE_NORMAL, 0)
    src_size = win32file.DeviceIoControl(src_f, winioctlcon.IOCTL_DISK_GET_LENGTH_INFO, None, 512, None)  #returns bytes
    src_precise_capacity = struct.unpack('q', src_size)[0]  #convert 64 bit int from bytes to int -> first element of returned tuple
    src_f.close()
 
    dest_f = win32file.CreateFile(dest_disk_name, win32file.GENERIC_READ, win32file.FILE_SHARE_READ | win32file.FILE_SHARE_WRITE, None, win32file.OPEN_EXISTING, win32file.FILE_ATTRIBUTE_NORMAL, 0)
    dest_size = win32file.DeviceIoControl(dest_f, winioctlcon.IOCTL_DISK_GET_LENGTH_INFO, None, 512, None)  #returns bytes
    dest_precise_capacity = struct.unpack('q', dest_size)[0]  #convert 64 bit int from bytes to int -> first element of returned tuple
    dest_f.close()

  except Exception as msg:
    print(str(msg))
    print("run pip install pywin32")
 
    # NB! Cannot use WMI result here since it is a bit smaller than actual disk size
 
    quit()
    
    # use AIDA64 to get precise capacity: 
    # Storage -> ATA -> select Disk -> LBA Sectors * Physical / Logical Sector Size (assume 512 if missing)
    # NB! do not use this since it is rounded: Storage -> ATA -> select Disk -> Unformatted Capacity
    # NB! similarly, do not use Windows provided capacity
    # NB! for finding out drive order numbers, do NOT rely on AIDA64, instead use the drive order from Windows Disk Management 
    src_precise_capacity = 976703805 * 512  # 500072348160  
    dest_precise_capacity = 976703805 * 512  # 500072348160  
    pass

else:   #/ if os.name == "nt":

  # alternative would be to call "lsblk -b -d -o NAME,SIZE" command

  with open(src_disk_name, 'rb', buffering=0) as src_f:
    # src_f.seek(offset=0, whence=0)
    # Many Python built-in functions accept no keyword arguments
    src_f.seek(0, 2)   # whence=2 means seek to end
    src_precise_capacity = src_f.tell()

  with open(dest_disk_name, 'rb', buffering=0) as dest_f:
    # dest_f.seek(offset=0, whence=0)
    # Many Python built-in functions accept no keyword arguments
    dest_f.seek(0, 2)   # whence=2 means seek to end
    dest_precise_capacity = dest_f.tell()

#/ if os.name == "nt":
      

if src_precise_capacity > dest_precise_capacity:
  print("src_precise_capacity > dest_precise_capacity: {} > {}".format(src_precise_capacity, dest_precise_capacity))
  quit()


# https://superuser.com/questions/839502/windows-equivalent-for-dd
with open(src_disk_name, 'rb', buffering=0) as src_f:
  with open(dest_disk_name, 'r+b', buffering=0) as dest_f:

    print("Source disk precise capacity: " + str(src_precise_capacity))
    src_capacity = src_precise_capacity 
    dest_capacity = dest_precise_capacity 

    step = 256 * 1024
  
    idle_step = 4 * 1024 * 1024
    idle_time = 60  # seconds

    print("step: " + str(step))
    print("idle_step: " + str(idle_step))
    print("idle_time: " + str(idle_time))

    mb = 1024 * 1024

    start_offset = 0    # You may want to modify this start offset in special cases. Then the disk clone tool will read the sectors startin from start_offset first. Later the disk clone tool will loop over to the very beginning of the disk and read the initially skipped beginning part of the disk, until start_offset.

    # f.seek(offset=start_offset, whence=0)   # whence=0 means absolute file positioning
    # Many Python built-in functions accept no keyword arguments
    src_f.seek(start_offset, 0)   # whence=0 means absolute file positioning
    dest_f.seek(start_offset, 0)   # whence=0 means absolute file positioning

    i = 0
    prev_i = 0
    total_bytes_read = 0
    while True:

      if abs(i - prev_i) >= mb:   # NB! handle cases when offset was changed in 512 byte increments
        print('{} MB cloned, offset {}, percent {:.3f}%'.format(int(total_bytes_read / mb), start_offset + i, total_bytes_read / src_capacity * 100))
        prev_i = i
      
      # pause cloning while on battery power
      try:  
        while psutil.sensors_battery() and not psutil.sensors_battery().power_plugged:   # NB! psutil.sensors_battery() may be None if there is no battery
          time.sleep(1)
      except Exception:
        pass


      try:

        # Loop over to drive beginning in case the cloning was started from a nonzero offset. When using default start_offset=0 this code branch here will not activate.
        if start_offset + i >= src_capacity:
          start_offset = 0
          i = 0
          # f.seek(offset=0, whence=0)
          # Many Python built-in functions accept no keyword arguments
          src_f.seek(0, 0)   # whence=0 means absolute file positioning
          dest_f.seek(0, 0)   # whence=0 means absolute file positioning
        

        current_step = idle_step if get_idle_time() >= idle_time else step

        next_rounded_offset = int((start_offset + i + current_step) / step) * step
        current_step = next_rounded_offset - (start_offset + i)   # NB! after stepping bad sectors try to adjust offset so that it again aligns with the step
      
        len_until_disk_end = src_capacity - (start_offset + i)
        current_step = min(current_step, len_until_disk_end)  # NB! do not try to read past disk end

        # print(str(current_step))

        data = src_f.read(current_step)      
        dest_f.write(data)

        i += current_step
        total_bytes_read += current_step

      except Exception as msg:
              
        # NB! If a bad sector is encountered, try to read in 512 byte step increments. If a read fails in an iteration during this loop of 512-byte increments, then seek past the failing sector. The rationale is that maybe the read error from above code occurred in some later sector than the first 512 bytes. Just skipping the first 512 bytes and then reading full current_step bytes would not be correct and would not work.

        for _ in range(0, current_step, 512): # read the amount of current_step bytes in 512 byte increments
          try:
            data = src_f.read(512)      
            dest_f.write(data)

            i += 512
            total_bytes_read += 512

          except Exception as msg:

            print("Error cloning disk at offset " + str(start_offset + i) + " : " + str(msg))

            i += 512
            total_bytes_read += 512
            # f.seek(offset=512, whence=1)   # skip the bad sector   # whence=1 means seek relative to the current position
            # Many Python built-in functions accept no keyword arguments
            src_f.seek(512, 1)   # skip the bad sector   # whence=1 means seek relative to the current position
            dest_f.seek(512, 1)   # skip the bad sector   # whence=1 means seek relative to the current position


      if total_bytes_read >= src_capacity:
        break

      # Yield to OS in case there are other processes that need CPU. If the system load is low, then OS will return to this script almost immediately.
      time.sleep(0)

    #/ while True:
  #/ with open(dest_disk_name,'rb') as dest_f:
#/ with open(src_disk_name,'rb') as src_f:

print("")
print("Done.")
print("")

print("RUN THE FOLLOWING COMMANDS IN A SEPARATE COMMAND CONSOLE TO MAKE SOURCE DISK WRITABLE AGAIN:")
if os.name == "nt":
  print("diskpart")
  print("select disk {}".format(src_disk_name[-1:]))
  print("attribute disk clear readonly")
  print("exit")
else:
  print("sudo hdparm -r0 {}".format(src_disk_name))
print("")
print("Press enter to continue:")
dummy = input()
print("")

