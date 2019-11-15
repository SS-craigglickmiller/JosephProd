""" Manage files in directories """

import os, time

def ArchiveFiles(path, age):
    count = MeetsRequirements(path, age, 'Archive')
    return count

def DeleteFiles(path, age):
    count = MeetsRequirements(path, age, 'Delete')
    return count

def MeetsRequirements(path, age, action):
    critical_time = time.time() - age*86400
    count = 0
    for filename in os.listdir(path):
        if os.path.isfile(os.path.join(path,filename)):
            if os.path.getmtime(os.path.join(path, filename)) < critical_time:
                if action == 'Archive':
                    #print('Archive ', filename)
                    os.rename(os.path.join(path, filename), os.path.join(path + '/Archive', filename))
                if action == 'Delete':
                    #print('Delete ', filename)
                    os.remove(os.path.join(path, filename))
                count+=1
    return count

def ArchiveSingle(path, filename):
    if not os.path.isfile(os.path.join(path, filename)):
        return 'Not a file'
    else:
        val = os.rename(os.path.join(path, filename), 
                    os.path.join(path+'/Archive', filename))
        return val
