import os
from sys import argv


# -------------------------------- prettifier

def prettify_dir(adir: str) -> str:
    """
    prettify folder path.
    
    Input: "..\\A\\B\\C"
    Output: "../A/B/C/"
    """
    if '\\' in adir:
        adir = adir.replace('\\', '/')
    if adir[-1] != '/':
        adir += '/'
    return adir


def prettify_file(afile: str) -> str:
    """
    prettify file path.
    
    Input: "A\\B\\C.txt"
    Output: "A/B/C.txt"
    """
    if '\\' in afile:
        afile = afile.replace('\\', '/')
    return afile


# -------------------------------- basic path locator

def get_launch_path():
    """
    Get the absolute path of the startup module
    
    Input:
        sys.argv[0]
            e.g. 'D:\\workspace\\my_project\\A.py'
    Output:
        'D:/workspace/my_project/A.py'
    """
    path = os.path.abspath(argv[0])
    return prettify_file(path)


def find_project_dir(apath='', recursive_times=0):
    """
    Get the absolute path of the current project's root directory.

    Input:
        The absolute path of the startup file
            example: "D:/workspace/my_project/A/B/C/D.py"
    Output:
        "D:/workspace/my_project/"
    """
    if not apath:
        apath = get_launch_path()
        # On the first search, obtain the absolute path of the startup file
    if recursive_times > 10:
        # Prevention mechanism: When the startup file path is too deep (default depth is 10 levels),
        # this function will throw an error
        raise AttributeError

    d = os.path.dirname(apath)  # d is the abbr of directory
    p = iter(os.listdir(d))  # p is the abbr of paths

    while True:
        sd = p.__next__()  # sd is the abbr of subdirectory
        if sd[0] == '.':

            if sd == '.idea':
                # lk.prt('the project path is {}'.format(d))
                return prettify_dir(d)  # Return the project root directory
            else:
                # might facing '.abc', '.git', ... directory
                continue
        elif sd in ['scheduler', 'cold_start', 'constant']:
            return prettify_dir(d)  # Return the project root directory
        else:
            break

    return find_project_dir(d, recursive_times + 1)  # Recursive search


# --------------------------------

root = find_project_dir(get_launch_path())


def getfile(path):
    return root + path


if __name__ == '__main__':
    res = getfile(r'util')
    print(res)
