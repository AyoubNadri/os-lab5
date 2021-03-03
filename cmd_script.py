#!/usr/bin/env python3

import os, sys
import shutil
import signal
from datetime import datetime
#add other imports as needed by your script
# The purpose of this script is to give you simple functions for locating an executable program in common locations in the Linux path

# Simple shell
# COMMANDS          ERRORS CHECKED
# 1. info XX         - check file/dir exists
# 2. files
# ... omitted for simplicity
# 8. Default is to run the program


# Here the path is hardcoded, but you can easily optionally get your PATH environ variable
# by using: path = os.environ['PATH'] and then splitting based on ':' such as the_path = path.split(':')
THE_PATH = ["/bin/", "/usr/bin/", "/usr/local/bin/", "./"]

# ========================
#    Run command
#    Run an executable somewhere on the path
#    Any number of arguments
# ========================
def runCmd(fields):
    global PID, THE_PATH

    cmd = fields[0]
    count = 0
    args = []
    while count < len(fields):
        args.append(fields[count])
        count += 1  
    
    execname = add_path(cmd, THE_PATH)

    # run the executable
    if not execname:
        print ("Executable file", cmd, "not found")
        return
    else:
      # execute the command
      print(execname)
#signal handler has to be in the parent
    PID = os.fork()
    # Wait if we're in parent, execute command if in child.
    if PID:
        os.waitpid(PID, 0)
    else:
    # execv executes a new program, replacing the current process; on success, it does not return. 
    # On Linux systems, the new executable is loaded into the current process, and will have the same process id as the caller.
        os.execv(execname, args)

# ========================
#    Constructs the full path used to run the external command
#    Checks to see if the file is executable. Returns False on failure.
# ========================
def add_path(cmd, path):
    if cmd[0] not in ['#!/', '#!.']:
        for d in path:
            execname = d + cmd
            if os.path.isfile(execname) and os.access(execname, os.X_OK):
                return execname
        return False
    else:
        return cmd

# ========================
#    files command
#    List file and directory names
#    No arguments
# ========================
def filesCmd(fields):
    target = os.path.realpath(os.path.expanduser(fields[1]))
    print(target)
    if checkArgs(fields, 1):
        for filename in os.listdir(target):
            if os.path.isdir(os.path.abspath(filename)):
                print("dir:", filename)
            else:
                print("file:", filename)

# ========================
#  info command
#     List file information
#     1 argument: file name
# ========================
def infoCmd(fields):
    arg = 1
    if len(fields) > 1:
        while arg < len(fields):
            name = fields[arg]
            path = os.path.realpath(os.path.expanduser(name))

            print("\npath  | ", path)
            if os.path.islink(name):
                print("type  | link -> " + os.path.basename(os.readlink(name)))
            elif os.path.isfile(name):
                print("type  | file")
            elif os.path.isdir(name):
                print("type  | directory")
            else:
                print("type  | other")
            if not os.path.exists(path):
                print("The path above does not exist.")
                arg = arg + 1
                continue
            print("owner | ", Path(path).owner())   
            if os.path.isfile(name):
                print("bytes | ", os.path.getsize(name))
            print("executable   |", os.access(path, os.X_OK))
            print("last_changed | ", datetime.fromtimestamp(os.path.getctime(path)).strftime('%b %d %Y %H:%M:%S'))

            arg = arg + 1
    else:
        print("Incorrect number of arguments for command:", fields[0])

# ========================
#  delete command
#     Delete file
#     1 argument: file name
# ========================
def del_cmd(fields):
    path = os.path.realpath(os.path.expanduser(fields[1]))
    if checkArgs(fields, 1):
        os.remove(path)
        if not os.path.exists(path):
            print("The file was deleted.")

# ========================
#  copy command
#     Copy and paste file 
#     2 argument: file name, new file name
# ========================
def copy_cmd(fields):
    src = os.path.realpath(os.path.expanduser(fields[1]))
    dst = os.path.realpath(os.path.expanduser(fields[2]))

    if checkArgs(fields, 2):
        if os.path.exists((dst)) & os.path.isfile(dst):
            ans = input("This path already exists. Do you want to overwrite it with your copy? (Y/n)\n")
            while (not ans == "Y") and (not ans == "n"):
                ans = input("This path already exists. Do you want to overwrite it with your copy? (Y/n)\n")

            if ans == "Y":
                result = shutil.copy2(src, dst)
                print("Your file is at ", result + ".")
            else:
                print("Your file wasn't copied.")
        else:
            result = shutil.copy2(src, dst)
            print("Your file is at ", result + ".") 
        
# ========================
#  where command
#     Show current directory
#     0 argument
#=========================
def where_cmd(fields):
    if checkArgs(fields, 0):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        print(dir_path)

# ========================
#  down command
#     Move down to a directory
#     1 argument: directory name
#=========================
def down_cmd(fields):
    if checkArgs(fields, 1):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        dst = dir_path + "/" + fields[1]

        os.chdir(dst)
        print("Directory changed.")

# ========================
#  up command
#     Move up to a directory
#     0 argument
#=========================
def up_cmd(fields, current):
    if checkArgs(fields, 0):
        dst = os.path.dirname(os.path.realpath(current))

        os.chdir(dst)
        print("Directory changed.")
        
        return current

# ----------------------
# Other functions
# ----------------------
def checkArgs(fields, num):
    numArgs = len(fields) - 1
    if numArgs == num:
        return True
    if numArgs > num:
        unexpected = ""
        for arg in fields[num+1:]:
            unexpected = unexpected  + " " + arg
        print("Unexpected argument" + unexpected + " for command:", fields[0])
    else:
        print("Missing argument for command:", fields[0])

    return False

def sigint_handler(signum, frame):
    os.kill(PID, signal.SIGKILL)
    print(" Process:", str(PID) + " was killed.")

# ----------------------------------------------------------------------------------------------------------------------
signal.signal(signal.SIGINT, sigint_handler)

while True:
    try:

        line = input("PShell>")
        fields = line.split()

        if fields[0] == "files":
            filesCmd(fields)
        elif fields[0] == "info":
            infoCmd(fields)
        elif fields[0] == "delete":
            del_cmd(fields)
        elif fields[0] == "copy":
            copy_cmd(fields)
        elif fields[0] == "where":
            where_cmd(fields)
        elif fields[0] == "down":
            down_cmd(fields)
        elif fields[0] == "up":
            current = os.getcwd()
            if not current == "/":
                current = up_cmd(fields, current)
            else:
                print("No higher directory.")
        elif fields[0] == "finish" or fields[0] == "x":
            break
        else:
            runCmd(fields)
    except FileExistsError:
        print("File already exists.")
    except FileNotFoundError:
        print("The path above does not exist.")
    except IndexError:
        print("Incorrect number of arguments for command:", fields[0])
    except IsADirectoryError:
        print("This is a directory.")
    except NotADirectoryError:
        print("This isn't a directory.")


