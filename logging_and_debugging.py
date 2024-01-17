import os, sys

LOG_REL_FILE_PATH = ""

def resource_path(relative_path):
    """
    Get absolute path to resource, works for dev and for PyInstaller
    """
    
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # this is the case used for dev (run .py)
        base_path = os.path.abspath(".")

    # returning the full path
    return os.path.join(base_path, relative_path)

def check_make_log_path(log_rel_file_path:str)->str:
    """
    Receives a relative path for the log file (log_rel_file_path)
    and generates the full absolute lof file path+filename
    """

    # given the relative path, resource_path() returns the absolute path whenever if pyinstaller or dev
    # Example: 
    # "%TEMP%\relative_path" for pyinstaller
    # "%CWD%\relative_path" for dev
    log_path = resource_path(os.path.realpath(log_rel_file_path))

    # if the "log-dir" exists, then ok. Else, create it.
    if (os.path.isdir(log_path)):
        pass
    else:
        os.mkdir(log_path)
    
    # return the str with the log path
    return log_path

def get_log_filename(current_py_file:str, log_rel_file_path:str=LOG_REL_FILE_PATH):
    """
    Create the path+filename string used to make the log file.
    """

    log_path = check_make_log_path(log_rel_file_path)
    log_basename = os.path.basename(current_py_file.replace('.py','.log'))

    return os.path.join(log_path, log_basename)

def remove_old_log_lines(log_file:str, max_lines:int=5000):
    
    """
    When the log file number of lines exceeds "max_lines", 
    we cut off the 1000 older lines from it, so it does not grow indefinitely.
    This gives room for at least 50 complete logs to be stored in the log-file.
    """

    # check if the log-file exists
    if (os.path.exists(log_file)):
        # count the number of lines on the log file
        line_count = 0
        with open(log_file) as f:
            for line in f:
                line_count = line_count+1

        # if the number of lines of the log file exceeds "max_lines"
        if (line_count > max_lines):
            temp_log_file = log_file.replace('.log','_temp.log')
            # read the log file and create a temp log file
            with open(log_file) as f, open(temp_log_file, "w") as out_temp:
                line_index = 0
                # read all lines from the current log file
                for line in f:
                    line_index = line_index+1
                    # write a copy of the lines on the temp log file only if line > 1000
                    if (line_index > 1000):
                        out_temp.write(line)
            # replace current log with temp log file (with lines reduced by 1000)
            os.replace(temp_log_file, log_file)