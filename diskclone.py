# -*- coding: utf-8 -*-

#
# Author: Roland Pihlakas, 2023
#
# roland@simplify.ee
#
# Version 1.0.2 - Fixed U+00A0 error and added image file output
#
# Roland Pihlakas licenses this file to you under the GNU Lesser General Public License, ver 2.1.
# See the LICENSE file for more information.
#

import os
import sys
import time
import struct
import re # Added for path pattern matching


# first argument is the python script name
if len(sys.argv) >= 3:

    print("")
    print("Starting...")

    # NB! for finding out drive order numbers used in the physical disk name, do NOT rely on AIDA64, instead use the drive order from Windows Disk Management or diskpart
    src_disk_name = sys.argv[1]
    dest_disk_name = sys.argv[2]

    # Check if the destination is a physical disk or a file
    is_dest_physical_disk = False
    if os.name == "nt":
        # Windows physical disk names typically start with \\.\PhysicalDrive
        if re.match(r"^\\\\\.\\PhysicalDrive\d+$", dest_disk_name, re.IGNORECASE):
            is_dest_physical_disk = True
    else:
        # Linux/Unix physical disk names are typically /dev/sdX, /dev/hdX, /dev/nvme0nX, /dev/ploopX
        # This is a simpler check, you might need a more robust one for all Linux variants
        if re.match(r"^/dev/(sd[a-z]|hd[a-z]|nvme\d+n\d+|ploop\d+)", dest_disk_name):
            is_dest_physical_disk = True

    print(f"Destination '{dest_disk_name}' treated as {'physical disk' if is_dest_physical_disk else 'image file'}.")

else:    #/ if len(sys.argv) >= 3:

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
    print('INSPECT THE SOURCE CODE, UNDERSTAND WHAT IT DOES AND VERIFY THAT THE CODE IS CORRECT. THEN USE WITH CARE. I AM NOT RESPONSIBLE IN ANY WAY IF YOU LOSE YOUR DATA. ALL DATA ON DESTINATION DISK OR IMAGE WILL BE OVERWRITTEN.')
    print('')
    print('')
    print('Usage:')
    print('')
    print('python diskclone.py SourceDisk Destination')
    print('')
    print('Under Windows (cloning to another disk):')
    print(r'python diskclone.py "\\.\PhysicalDrive0" "\\.\PhysicalDrive1"')
    print('Under Windows (saving to an image file):')
    print(r'python diskclone.py "\\.\PhysicalDrive0" "C:\disk_image.img"')
    print('or')
    print('Under Linux (cloning to another disk):')
    print(r'python diskclone.py "/dev/ploop12345" "/dev/ploop67890"')
    print('Under Linux (saving to an image file):')
    print(r'python diskclone.py "/dev/sdb" "/mnt/backup/disk.img"')
    print('')
    print('')
    print('A Python 2 or 3 installation is required. There are package dependencies:')
    print(' - psutil')
    print(' - pywin32 (under Windows OS only)')
    print(' - re (standard library, for path matching)')
    print('')
    print('')
    print('Version 1.0.2')
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

        # 0x00100000: PROCESS_MODE_BACKGROUND_BEGIN
        win32process.SetPriorityClass(-1, 0x00100000)    # NB! -1: win32api.GetCurrentProcess()

    except Exception as msg:
        print(str(msg))
        print("run pip install pywin32")
        pass


print("")
print("")
# Adjusted warning based on destination type
if is_dest_physical_disk:
    print("WARNING!!! ALL DATA ON DISK {} WILL BE OVERWRITTEN.".format(dest_disk_name))
else:
    print("WARNING!!! THE IMAGE FILE {} WILL BE OVERWRITTEN.".format(dest_disk_name))
print("TYPE 'YES' AND PRESS ENTER TO CONTINUE, OR PRESS CTRL+C TO CANCEL:")
confirmation = input()
if confirmation != "YES":
    quit()

print("")
print("")
print("RUN THE FOLLOWING COMMANDS IN A SEPARATE COMMAND CONSOLE TO MAKE THE SOURCE DISK READONLY:")
if os.name == "nt":
    print("sync")
    print("diskpart")
    print("select disk {}".format(src_disk_name[-1:]))
    print("attribute disk set readonly")
    print("exit")
    if is_dest_physical_disk:
        print("AND TO CLEAN THE DESTINATION DISK:")
        print("diskpart")
        print("select disk {}".format(dest_disk_name[-1:]))
        print("clean")
        print("exit")
    else:
        print("NOTE: Image file destination requires no 'clean' command.")
else:
    print("sync")
    print("sudo hdparm -F -r1 {}".format(src_disk_name))
    if is_dest_physical_disk:
        print("AND TO CLEAN THE DESTINATION DISK:")
        print("sudo wipefs -a {}".format(dest_disk_name))
    else:
        print("NOTE: Image file destination requires no 'wipefs' command.")
print("")
print("PRESS ENTER TO CONTINUE:")
dummy = input()
print("")


# --- Disk Capacity Determination (Source) ---
if os.name == "nt":
    try:
        import win32file
        import winioctlcon

        # Get Source Disk Capacity
        src_f = win32file.CreateFile(src_disk_name, win32file.GENERIC_READ, win32file.FILE_SHARE_READ | win32file.FILE_SHARE_WRITE, None, win32file.OPEN_EXISTING, win32file.FILE_ATTRIBUTE_NORMAL, 0)
        src_size = win32file.DeviceIoControl(src_f, winioctlcon.IOCTL_DISK_GET_LENGTH_INFO, None, 512, None)  #returns bytes
        src_precise_capacity = struct.unpack('q', src_size)[0]  #convert 64 bit int from bytes to int -> first element of returned tuple
        src_f.close()

    except Exception as msg:
        print(str(msg))
        print("run pip install pywin32 or ensure source disk path is correct")
        quit()
else:    #/ if os.name == "nt":
    # Get Source Disk Capacity
    with open(src_disk_name, 'rb', buffering=0) as src_f:
        src_f.seek(0, 2)    # whence=2 means seek to end
        src_precise_capacity = src_f.tell()

#/ if os.name == "nt":


# --- Disk Capacity Determination (Destination) ---
if is_dest_physical_disk:
    if os.name == "nt":
        try:
            dest_f = win32file.CreateFile(dest_disk_name, win32file.GENERIC_READ, win32file.FILE_SHARE_READ | win32file.FILE_SHARE_WRITE, None, win32file.OPEN_EXISTING, win32file.FILE_ATTRIBUTE_NORMAL, 0)
            dest_size = win32file.DeviceIoControl(dest_f, winioctlcon.IOCTL_DISK_GET_LENGTH_INFO, None, 512, None)  #returns bytes
            dest_precise_capacity = struct.unpack('q', dest_size)[0]  #convert 64 bit int from bytes to int -> first element of returned tuple
            dest_f.close()
        except Exception as msg:
            print(str(msg))
            print("run pip install pywin32 or ensure destination disk path is correct")
            quit()
    else:
        with open(dest_disk_name, 'rb', buffering=0) as dest_f:
            dest_f.seek(0, 2)    # whence=2 means seek to end
            dest_precise_capacity = dest_f.tell()
else:
    # If destination is an image file, the required capacity is the source capacity.
    dest_precise_capacity = src_precise_capacity

# --- Capacity Check ---
if src_precise_capacity > dest_precise_capacity:
    print("src_precise_capacity > dest_precise_capacity: {} > {}".format(src_precise_capacity, dest_precise_capacity))
    if not is_dest_physical_disk:
        # If it's a file, we set the file size below, so we don't quit, but warn.
        print("The target image file size will be set to the source disk size.")
    else:
        # If it's a disk, we must quit because the destination is too small.
        quit()


# Determine file open mode for destination
if is_dest_physical_disk:
    dest_open_mode = 'r+b'
else:
    # 'w+b' will create the file or truncate it if it exists
    dest_open_mode = 'w+b'

with open(src_disk_name, 'rb', buffering=0) as src_f:
    with open(dest_disk_name, dest_open_mode, buffering=0) as dest_f:

        # If we are writing to an image file, ensure the file is the size of the source disk
        if not is_dest_physical_disk:
            print(f"Setting image file size to {src_precise_capacity} bytes...")
            # Use os.ftruncate to set the file size, ensuring it's the full disk size
            dest_f.truncate(src_precise_capacity)
            dest_precise_capacity = src_precise_capacity # Re-set dest capacity to source capacity for logic below

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

        # f.seek(offset=start_offset, whence=0)    # whence=0 means absolute file positioning
        # Many Python built-in functions accept no keyword arguments
        src_f.seek(start_offset, 0)    # whence=0 means absolute file positioning
        dest_f.seek(start_offset, 0)    # whence=0 means absolute file positioning

        i = 0
        prev_i = 0
        total_bytes_read = 0
        while True:

            if abs(i - prev_i) >= mb:    # NB! handle cases when offset was changed in 512 byte increments
                print('{} MB cloned, offset {}, percent {:.3f}%'.format(int(total_bytes_read / mb), start_offset + i, total_bytes_read / src_capacity * 100))
                prev_i = i

            # pause cloning while on battery power
            try:
                while psutil.sensors_battery() and not psutil.sensors_battery().power_plugged:    # NB! psutil.sensors_battery() may be None if there is no battery
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
                    src_f.seek(0, 0)    # whence=0 means absolute file positioning
                    dest_f.seek(0, 0)    # whence=0 means absolute file positioning


                current_step = idle_step if get_idle_time() >= idle_time else step

                next_rounded_offset = int((start_offset + i + current_step) / step) * step
                current_step = next_rounded_offset - (start_offset + i)    # NB! after stepping bad sectors try to adjust offset so that it again aligns with the step

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
                        # f.seek(offset=512, whence=1)    # skip the bad sector    # whence=1 means seek relative to the current position
                        # Many Python built-in functions accept no keyword arguments
                        src_f.seek(512, 1)    # skip the bad sector    # whence=1 means seek relative to the current position
                        dest_f.seek(512, 1)    # skip the bad sector    # whence=1 means seek relative to the current position


            if total_bytes_read >= src_capacity:
                break

            # Yield to OS in case there are other processes that need CPU. If the system load is low, then OS will return to this script almost immediately.
            time.sleep(0)

        #/ while True:
    #/ with open(dest_disk_name,'r+b' or 'w+b') as dest_f:
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
