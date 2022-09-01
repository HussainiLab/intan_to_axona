import numpy as np

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

def write_pos(filepath, pos_dict: dict):
    with open(filepath, 'wb+') as f:
        header_vals = [
            'trial_time' % pos_dict['t'],
            '\r\nx_pos' % pos_dict['x'],
            '\r\ny_pos' % pos_dict['y'],
            '\r\ndata_start'
        ]

        write_list = []

        for value in header_vals:
            write_list.append(bytes(value, 'utf-8'))

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


def _read_pos(pos_path, ppm):

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

    pos_data = _get_position(pos_path, ppm)

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