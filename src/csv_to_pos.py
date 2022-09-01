import numpy as np
import json, struct
import scipy

# refactor into a function that takes a pandas data frame
# that has columns for time, x and y coordinates
# aliases: (t | time | timestamp | timestamps) and (x | y | x_coord | y_coord)
# and returns a dictionary with the lines to be written to the .pos file
# and another function that takes the dictionary and writes the .pos file


def pd_to_dict(data_frame):
    time_aliases = ['t', 'time', 'timestamp', 'timestamps']
    # freq_aliases = ['sample_rate', 'fs', 'sample_freq', 'sampling_freq', 'sampling_rate', 'Fs']
    x_aliases = ['x','x_coord', 'pos_x', 'x_pos']
    y_aliases = ['y', 'y_coord', 'pos_y', 'y_pos']


    for col in data_frame.columns:
        if col in time_aliases:
            pos_t = data_frame.loc[:,col].tolist()
        if col in x_aliases:
            pos_x = data_frame.loc[:,col].tolist()
        if col in y_aliases:
            pos_y = data_frame.loc[:,col].tolist()
        # if col in freq_aliases:
        #     pos_dict['fs'] = data_frame.loc[:,col]

    posx, posy, post = pos2hz(pos_t, pos_x, pos_y, start=pos_t[0], stop=pos_t[-1])

    pos_dict = {}
    pos_dict['x'] =  list(pos_x)
    pos_dict['y'] =  list(pos_y)
    pos_dict['t'] =  list(pos_t)

    return pos_dict

def text_to_dict(position_text_file):

    pos_t, pos_x, pos_y = [], [], []

    f = open(position_text_file, "r")
    for line in f:
        if '#' not in line:
            line = line.split()
            pos_t.append(float(line[0]))
            pos_x.append(float(line[1]))
            pos_y.append(float(line[2]))

    n_samples = len(pos_x)

    posx, posy, post = pos2hz(pos_t, pos_x, pos_y, start=pos_t[0], stop=pos_t[-1])

    pos_dict = {}
    pos_dict['x'] =  list(pos_x)
    pos_dict['y'] =  list(pos_y)
    pos_dict['t'] =  list(pos_t)

    return pos_dict

def get_pos_header(pos_dict, **kwargs):
 pass

def write_pos(filepath, jsonpath, pos_dict: dict):

    with open(jsonpath, 'r') as f:
        expter_dict = json.load(f)

    with open(filepath, 'wb+') as f:
        # header_vals = [
        #     'trial_time' % pos_dict['t'],
        #     '\r\nx_pos' % pos_dict['x'],
        #     '\r\ny_pos' % pos_dict['y'],
        #     '\r\ndata_start'
        # ]

        header_vals = ['trial_date %s' % expter_dict['trial_date'],
          '\r\ntrial_time %s' % expter_dict['trial_time'],
          '\r\nexperimenter %s' % expter_dict['experimenter'],
          '\r\ncomments :%s' % expter_dict['comments'],
          '\r\nduration %d' % expter_dict['duration'],
          '\r\nsw_version %s' % expter_dict['sw_version'],
          '\r\nnum_colours %d' % expter_dict['num_colours'],
          '\r\nmin_x %d' % expter_dict['min_x'],
          '\r\nmax_x %d' % expter_dict['max_x'],
          '\r\nmin_y %d' % expter_dict['min_y'],
          '\r\nmax_y %d' % expter_dict['max_y'],
          '\r\nwindow_min_x %d' % expter_dict['window_min_x'],
          '\r\nwindow_max_x %d' % expter_dict['window_max_x'],
          '\r\nwindow_min_y %d' % expter_dict['window_min_y'],
          '\r\nwindow_max_y %d' % expter_dict['window_max_y'],
          '\r\ntimebase %d hz' % expter_dict['timebase'],
          '\r\nbytes_per_timestamp %d' % expter_dict['bytes_per_timestamp'],
          '\r\nsample_rate %.1f hz' % expter_dict['sample_rate'],
          '\r\nEEG_samples_per_position %d' % expter_dict['EEG_samples_per_position'],
          '\r\nbearing_colour_1 %d' % expter_dict['bearing_colour_1'],
          '\r\nbearing_colour_2 %d' % expter_dict['bearing_colour_2'],
          '\r\nbearing_colour_3 %d' % expter_dict['bearing_colour_3'],
          '\r\nbearing_colour_4 %d' % expter_dict['bearing_colour_4'],
          '\r\npos_format t,x1,y1,x2,y2,numpix1,numpix2',
          '\r\nbytes_per_coord %d' % expter_dict['bytes_per_coord'],
          '\r\npixels_per_metre %s' % expter_dict['pixels_per_metre'],
          '\r\nnum_pos_samples %d' % expter_dict['num_pos_samples'],
          '\r\ndata_start']

        write_list = []

        for value in header_vals:
            write_list.append(bytes(value, 'utf-8'))

        for sample_num in np.arange(0, len(pos_dict['x'])):
            '''
            twospot => format: t,x1,y1,x2,y2,numpix1,numpix2
            onespot mode has the same format as two-spot mode except x2 and y2 take on values of 1023 (untracked value)
            note: timestamps and positions are big endian, i has 4 bytes, and h has 2 bytes
            '''
            numpix1 = 1
            numpix2 = 0
            x2 = 1023
            y2 = 1023
            unused = 0
            total_pix = numpix1  # total number of pixels tracked
            write_list.append(struct.pack('>i', sample_num))
            write_list.append(struct.pack('>8h', int(np.rint(pos_dict['x'][sample_num])),
                                          int(np.rint(pos_dict['y'][sample_num])), x2, y2, numpix1,
                                          numpix2, total_pix, unused))

        write_list.append(bytes('\r\ndata_end\r\n', 'utf-8'))
        f.writelines(write_list)



def pos2hz(t, x, y, start=None, stop=None, Fs=50):
    """This will convert the positions to 50 Hz values"""
    if start is None:
        start = 0
    if stop is None:
        stop = np.amax(t)
    # step = 1 / Fs  # 50 Hz sample rate
    # post = MatlabNumSeq(start, stop, step, exclude=True)

    duration = stop - start
    n = duration * Fs
    post = np.arange(n) / Fs + start

    posx = np.zeros_like(post)
    posy = np.zeros_like(post)

    for i, t_value in enumerate(post):
        index = np.where(t <= t_value)[0][-1]
        posx[i] = x[index]
        posy[i] = y[index]

    return posx, posy, post

def _fix_timestamps(post):
    first = post[0]
    N = len(post)
    uniquePost = np.unique(post)

    if len(uniquePost) != N:
        didFix = True
        numZeros = 0
        # find the number of zeros at the end of the file

        while True:
            if post[-1 - numZeros] == 0:
                numZeros += 1
            else:
                break
        last = first + (N-1-numZeros)*0.02
        fixedPost = np.arange(first, last+0.02, 0.02)
        fixedPost = fixedPost.reshape((len(fixedPost), 1))

    else:
        didFix = False
        fixedPost = []

    return didFix, fixedPost

def _arena_config(posx, posy, ppm, center, flip_y=True):
    """
    :param posx:
    :param posy:
    :param arena:
    :param conversion:
    :param center:
    :param flip_y: bool value that will determine if you want to flip y or not. When recording on Intan we inverted the
    positions due to the camera position. However in the virtualmaze you might not want to flip y values.
    :return:
    """
    center = center
    conversion = ppm

    posx = 100 * (posx - center[0]) / conversion

    if flip_y:
        # flip the y axis
        posy = 100 * (-posy + center[1]) / conversion
    else:
        posy = 100 * (posy + center[1]) / conversion

    return posx, posy

def _find_center(NE, NW, SW, SE):
    """Finds the center point (x,y) of the position boundaries"""

    x = np.mean([np.amax([NE[0], SE[0]]), np.amin([NW[0], SW[0]])])
    y = np.mean([np.amax([NW[1], NE[1]]), np.amin([SW[1], SE[1]])])
    return np.array([x, y])

def _center_box(posx, posy):
    # must remove Nans first because the np.amin will return nan if there is a nan
    posx = posx[~np.isnan(posx)]  # removes NaNs
    posy = posy[~np.isnan(posy)]  # remove Nans

    NE = np.array([np.amax(posx), np.amax(posy)])
    NW = np.array([np.amin(posx), np.amax(posy)])
    SW = np.array([np.amin(posx), np.amin(posy)])
    SE = np.array([np.amax(posx), np.amin(posy)])

    return _find_center(NE, NW, SW, SE)

def _remove_nan(posx, posy, post):
    """Remove any NaNs from the end of the array"""
    remove_nan = True
    while remove_nan:
        if np.isnan(posx[-1]):
            posx = posx[:-1]
            posy = posy[:-1]
            post = post[:-1]
        else:
            remove_nan = False
    return posx, posy, post

def _get_position(pos_fpath, flip_y=True):
    """
    _get_position function:
    ---------------------------------------------
    variables:
    -pos_fpath: the full path (C:\example\session.pos)

    output:
    t: column numpy array of the time stamps
    x: a column array of the x-values (in pixels)
    y: a column array of the y-values (in pixels)
    """

    with open(pos_fpath, 'rb+') as f:  # opening the .pos file
        headers = ''  # initializing the header string
        for line in f:  # reads line by line to read the header of the file
            if 'data_start' in str(line):  # if it reads data_start that means the header has ended
                headers += 'data_start'
                break  # break out of for loop once header has finished
            elif 'duration' in str(line):
                headers += line.decode(encoding='UTF-8')
            elif 'num_pos_samples' in str(line):
                num_pos_samples = int(line.decode(encoding='UTF-8')[len('num_pos_samples '):])
                headers += line.decode(encoding='UTF-8')
            elif 'bytes_per_timestamp' in str(line):
                bytes_per_timestamp = int(line.decode(encoding='UTF-8')[len('bytes_per_timestamp '):])
                headers += line.decode(encoding='UTF-8')
            elif 'bytes_per_coord' in str(line):
                bytes_per_coord = int(line.decode(encoding='UTF-8')[len('bytes_per_coord '):])
                headers += line.decode(encoding='UTF-8')
            elif 'timebase' in str(line):
                timebase = (line.decode(encoding='UTF-8')[len('timebase '):]).split(' ')[0]
                headers += line.decode(encoding='UTF-8')
            elif 'pixels_per_metre' in str(line):
                ppm = float(line.decode(encoding='UTF-8')[len('pixels_per_metre '):])
                headers += line.decode(encoding='UTF-8')
            elif 'min_x' in str(line) and 'window' not in str(line):
                min_x = int(line.decode(encoding='UTF-8')[len('min_x '):])
                headers += line.decode(encoding='UTF-8')
            elif 'max_x' in str(line) and 'window' not in str(line):
                max_x = int(line.decode(encoding='UTF-8')[len('max_x '):])
                headers += line.decode(encoding='UTF-8')
            elif 'min_y' in str(line) and 'window' not in str(line):
                min_y = int(line.decode(encoding='UTF-8')[len('min_y '):])
                headers += line.decode(encoding='UTF-8')
            elif 'max_y' in str(line) and 'window' not in str(line):
                max_y = int(line.decode(encoding='UTF-8')[len('max_y '):])
                headers += line.decode(encoding='UTF-8')
            elif 'pos_format' in str(line):
                headers += line.decode(encoding='UTF-8')
            elif 'sample_rate' in str(line):
                sample_rate = float(line.decode(encoding='UTF-8').split(' ')[1])
                headers += line.decode(encoding='UTF-8')

            else:
                headers += line.decode(encoding='UTF-8')

        
    with open(pos_fpath, 'rb+') as f:
        '''get_pos for one_spot'''
        pos_data = f.read()  # all the position data values (including header)
        pos_data = pos_data[len(headers):-12]  # removes the header values

        byte_string = 'i8h'

        pos_data = np.asarray(struct.unpack('>%s' % (num_pos_samples * byte_string), pos_data))
        pos_data = pos_data.astype(float).reshape((num_pos_samples, 9))  # there are 8 words and 1 time sample

    x = pos_data[:, 1]
    y = pos_data[:, 2]
    t = pos_data[:, 0]

    x = x.reshape((len(x), 1))
    y = y.reshape((len(y), 1))
    t = t.reshape((len(t), 1))


    t = np.divide(t, np.float(timebase))  # converting the frame number from Axona to the time value

    # values that are NaN are set to 1023 in Axona's system, replace these values by NaN's

    x[np.where(x == 1023)] = np.nan
    y[np.where(y == 1023)] = np.nan

    didFix, fixedPost = _fix_timestamps(t)

    if didFix:
        t = fixedPost

    t = t - t[0]

    x, y = _arena_config(x, y, ppm, center=_center_box(x,y), flip_y=flip_y)

        # remove any NaNs at the end of the file
    x, y, t = _remove_nan(x, y, t)

    return x.reshape((len(x), 1)), y.reshape((len(y), 1)), t.reshape((len(t), 1)), sample_rate

def _rem_bad_track(x, y, t, threshold):
    """function [x,y,t] = _rem_bad_track(x,y,t,treshold)

    % Indexes to position samples that are to be removed
   """

    remInd = []
    diffx = np.diff(x, axis=0)
    diffy = np.diff(y, axis=0)
    diffR = np.sqrt(diffx ** 2 + diffy ** 2)

    # the MATLAB works fine without NaNs, if there are Nan's just set them to threshold they will be removed later
    diffR[np.isnan(diffR)] = threshold # setting the nan values to threshold
    ind = np.where((diffR > threshold))[0]

    if len(ind) == 0:  # no bad samples to remove
        return x, y, t

    if ind[-1] == len(x):
        offset = 2
    else:
        offset = 1

    for index in range(len(ind) - offset):
        if ind[index + 1] == ind[index] + 1:
            # A single sample position jump, tracker jumps out one sample and
            # then jumps back to path on the next sample. Remove bad sample.
            remInd.append(ind[index] + 1)
        else:
            ''' Not a single jump. 2 possibilities:
             1. Tracker jumps out, and stay out at the same place for several
             samples and then jumps back.
             2. Tracker just has a small jump before path continues as normal,
             unknown reason for this. In latter case the samples are left
             untouched'''
            idx = np.where(x[ind[index] + 1:ind[index + 1] + 1 + 1] == x[ind[index] + 1])[0]
            if len(idx) == len(x[ind[index] + 1:ind[index + 1] + 1 + 1]):
                remInd.extend(
                    list(range(ind[index] + 1, ind[index + 1] + 1 + 1)))  # have that extra since range goes to end-1

    # keep_ind = [val for val in range(len(x)) if val not in remInd]
    keep_ind = np.setdiff1d(np.arange(len(x)), remInd)

    x = x[keep_ind]
    y = y[keep_ind]
    t = t[keep_ind]

    return x.reshape((len(x), 1)), y.reshape((len(y), 1)), t.reshape((len(t), 1))

def read_pos(pos_path):

    '''
        Extracts position data from .pos file

        Params:
            pos_path (str):
                Directory of where the position file is stored
            ppm (float):
                Pixel per meter value

        Returns:
            Tuple: pos_x,pos_y,pos_t,(pos_x_width,pos_y_width)
            --------
            pos_x, pos_y, pos_t (np.ndarray):
                Array of x, y coordinates, and timestamps
            pos_x_width (float):
                max - min x coordinate value (arena width)
            pos_y_width (float)
                max - min y coordinate value (arena length)
    '''

    pos_data = _get_position(pos_path)

    # Correcting pos_t data in case of bad position file
    new_pos_t = np.copy(pos_data[2])
    if len(new_pos_t) < len(pos_data[0]):
        while len(new_pos_t) != len(pos_data[0]):
            new_pos_t = np.append(new_pos_t, float(new_pos_t[-1] + 0.02))
    elif len(new_pos_t) > len(pos_data[0]):
        while len(new_pos_t) != len(pos_data[0]):
            new_pos_t = np.delete(new_pos_t, -1)

    Fs_pos = pos_data[3]

    pos_x = pos_data[0]
    pos_y = pos_data[1]
    pos_t = new_pos_t

    # Rescale coordinate values with respect to a center point
    # (i.e arena center = origin (0,0))
    center = _center_box(pos_x, pos_y)
    pos_x = pos_x - center[0]
    pos_y = pos_y - center[1]

    # Correct for bad tracking
    pos_data_corrected = _rem_bad_track(pos_x, pos_y, pos_t, 2)
    pos_x = pos_data_corrected[0]
    pos_y = pos_data_corrected[1]
    pos_t = pos_data_corrected[2]

    # Remove NaN values
    nonNanValues = np.where(np.isnan(pos_x) == False)[0]
    pos_t = pos_t[nonNanValues]
    pos_x = pos_x[nonNanValues]
    pos_y = pos_y[nonNanValues]

    # Smooth data using boxcar convolution
    B = np.ones((int(np.ceil(0.4 * Fs_pos)), 1)) / np.ceil(0.4 * Fs_pos)
    pos_x = scipy.ndimage.convolve(pos_x, B, mode='nearest')
    pos_y = scipy.ndimage.convolve(pos_y, B, mode='nearest')

    pos_x_width = max(pos_x) - min(pos_x)
    pos_y_width = max(pos_y) - min(pos_y)

    return pos_x, pos_y, pos_t, (pos_x_width, pos_y_width)