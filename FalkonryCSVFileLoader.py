from falkonryclient import client as Falkonry
from falkonryclient import schemas as Schemas
import sys, io, os
import glob, shutil
import argparse
import time
import json
import datetime

#
# Treat this as a constant
#
WAIT_TIME_LIMIT = 1800
SIZE_LIMIT = 50 * 1024 * 1024


#
# Log method
#
def info(msg):
    ts = str(datetime.datetime.now())
    print("INFO:" + ts + " : " + msg, flush=True)


#
# Error log method
#
def err_msg(msg):
    ts = str(datetime.datetime.now())
    print("ERROR:" + ts + " : " + msg, flush=True)


#
# Method to upload a chunk consisting of multiple files
#
def upload_chunk(chunk, ds_id, falkonry):
    start_time = int(time.time())
    pause = 5  # In seconds
    processed = 0
    error_count = 0
    error_limit = 3
    status = False
    try:
        opts = {'streaming': False, 'hasMoreData': False}
        #
        # Retry until the API call is successful or error_limit is reached
        #
        while processed == 0:
            res = falkonry.add_input_data(ds_id, 'csv', opts, chunk)
            while True:
                tr = falkonry.get_status(res['__$id'])
                status = tr['status']
                info("Status:" + status)
                if status == 'SUCCESS':
                    processed = 1
                    status = True
                    info("Completed loading chunk")
                    break
                elif status == 'ERROR':
                    error_count = error_count + 1
                    if (error_count >= error_limit):
                        info("ERROR loading - retrials failed. Skipping chunk")
                        processed = 1
                    else:
                        info("ERROR loading - RETRYING loading")
                    break
                elif status == 'PENDING':
                    if (int(time.time()) - start_time > WAIT_TIME_LIMIT):
                        info("Skipping after waiting " + str(WAIT_TIME_LIMIT))
                        processed = 1
                        break
                    else:
                        info("Sleeping...")
                        time.sleep(pause)
    except IOError:
        info("IOError... Skipping chunk")
    except:
        #
        # Other unknown errors
        #
        info("Unknown exception")
        info(sys.exc_info()[1])
    finally:
        return status


def get_data(fname, is_first):
    info("Reading file :" + fname + "(is_first=" + str(is_first) + ")")
    fle = open(fname)
    #
    # Skip the first header line if not the first file
    #
    if (is_first == False):
        fle.readline()
    data = fle.read()
    fle.close()
    return data


#
# Main method.
#
def pump_data(flist, ds_id, falkonry, dst):
    count = 0
    LIMIT = SIZE_LIMIT  # 50MB at a time
    data = ""
    status = False
    cflist = []

    stat_success_files = 0
    stat_failed_files = 0
    stat_success_size = 0
    stat_failed_size = 0

    listsize = len(flist)
    nF = 0
    for f0 in flist:
        fname = f0
        nF += 1
        cflist.append(fname)
        data += get_data(fname, (count == 0))
        count += 1
        data_size = len(data)
        if (data_size >= LIMIT or nF >= listsize):
            info("Data size is : " + str(data_size))
            status = upload_chunk(data, ds_id, falkonry)
            data = ''
            #
            # Move processed files
            #
            if (status == True):
                for fle in cflist:
                    shutil.move(fle, dst)
                info("Processed files : " + str(cflist))
                stat_success_files += len(cflist)
                stat_success_size += data_size
            else:
                info("Skipped processing : " + str(cflist))
                stat_failed_files += len(cflist)
                stat_failed_size += data_size
            count = 0
            cflist = []  # Reset list

    return (stat_success_files, stat_failed_files, stat_success_size, stat_failed_size)


#
# The main method
#
def main():
    parser = argparse.ArgumentParser(description='Adds data to a named datastream.')
    parser.add_argument('name', metavar='n', nargs=1, help='datastream')
    parser.add_argument('file', metavar='f', nargs=1, help='token file')
    parser.add_argument('data', metavar='d', nargs=1, help='source directory')

    args = parser.parse_args()
    dsname = str(args.name[0])
    tname = str(args.file[0])
    dirname = str(args.data[0])

    if not os.path.exists(tname):
        err_msg("no token file found: " + tname)
        sys.exit()

    with open(tname) as f:
        token = f.readline().strip()

    pref = 'c:/' + dirname + '/'
    if not os.path.exists(pref):
        err_msg("no input directory found: " + pref)
        sys.exit()

    src = pref + '*.csv'
    dst = pref + 'done/'  # if this does not exist, files will be copied to a file named 'done'

    # instantiate Falkonry
    falkonry = Falkonry('https://awo-op-falk01:30061', token, None)

    dsid = ''

    p_start_time = int(time.time())
    # can replace this with ds ID
    datastreams = falkonry.get_datastreams()
    for ds in datastreams:
        if dsname == ds.get_name():
            dsid = ds.get_id()

    if len(dsid) == 0:
        err_msg("Could not find datastream named " + dsname)
        sys.exit()

    flist = glob.glob(src)
    (stat_success_files, stat_failed_files, stat_success_size, stat_failed_size) = pump_data(flist, dsid, falkonry, dst)
    p_end_time = int(time.time())

    #
    # Summary
    #
    info("Processing time is :" + str(p_end_time - p_start_time) + " seconds")
    info("Processed " + str(stat_success_files) + " files successfully out of total " + str(len(flist)))
    info("Failed to process " + str(stat_failed_files) + " files out of total " + str(len(flist)))
    info("Data transfer rate = " + str(
        int((stat_success_size + stat_failed_size) / (p_end_time - p_start_time))) + " bytes per second.")

    #
    # Check to see if any files are skipped
    #
    flist = glob.glob(src)
    if (len(flist) > 0):
        info("Number of files not processed " + str(len(flist)) + ".")
        info("Rerun this script to process the files skipped.")
    else:
        info("All Files processed successfully.  No more files to process!!!")

    info("Processing Complete!!!")


if __name__ == '__main__':
    main()