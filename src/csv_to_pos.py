
# refactor into a function that takes a pandas data frame
# that has columns for time, x and y coordinates
# aliases: (t | time | timestamp | timestamps) and (x | y | x_coord | y_coord)
# and returns a dictionary with the lines to be written to the .pos file
# and another function that takes the dictionary and writes the .pos file


def write_pos(self, filepath, data, time, track_settings, create_date, create_time, Fs=50, timebase=50, ):
    """
    Write a pos file to filepath.

    """
        expter_file = 'experimenter.json'
        with open(expter_file, 'r') as f:
            expter_dict = json.load(f)

        for key, value in expter_dict.items():
            if self.exptername.currentText() == key:
                expter_values = value
            else:
                pass
        for i in range(0, len(expter_values)):
            if value[i] == '':
                if i == 1:  # min x
                    expter_values[i] = '0'
                elif i == 2:  # max x
                    expter_values[i] = '768'
                elif i == 3:  # min y
                    expter_values[i] = '0'
                elif i == 4:  # max y
                    expter_values[i] = '574'
                elif i == 5:  # min x window
                    expter_values[i] = '233'
                elif i == 6:  # max x window
                    expter_values[i] = '439'
                elif i == 7:  # min y window
                    expter_values[i] = '144'
                elif i == 8:
                    expter_values[i] = '350'
                elif i == 9:
                    expter_values[i] = '700'  # pix/meter

        with open(filepath, 'w') as f:
            date = 'trial_date %s' % (create_date)
            time_head = '\ntrial_time %s' % (create_time)
            expter = '\nexperimenter %s' % (self.exptername.currentText())
            comments = '\ncomments %s' % (self.comment_e.toPlainText())
            # dur = '\nduration %d' % (int(math.ceil(time[-1])))
            dur = '\nduration %.2f' % (time[-1])
            sw_vers = '\nsw_version %s' % (self.sw_combo.currentText())
            num_colours = '\nnum_colours %d' % (4)
            min_x = '\nmin_x %s' % (expter_values[1])
            max_x = '\nmax_x %s' % (expter_values[2])
            min_y = '\nmin_y %s' % (expter_values[3])
            max_y = '\nmax_y %s' % (expter_values[4])
            window_min_x = '\nwindow_min_x %s' % (expter_values[5])
            window_max_x = '\nwindow_max_x %s' % (expter_values[6])
            window_min_y = '\nwindow_min_y %s' % (expter_values[7])
            window_max_y = '\nwindow_max_y %s' % (expter_values[8])
            timebase_val = '\ntimebase %d hz' % (timebase)
            b_p_timestamp = '\nbytes_per_timestamp %d' % (4)
            sample_rate = '\nsample_rate %.1f hz' % (float(Fs))
            eeg_samp_per_pos = '\nEEG_samples_per_position %d' % (5)
            bearing_colours_1 = '\nbearing_colour_1 %d' % (0)
            bearing_colours_2 = '\nbearing_colour_2 %d' % (0)
            bearing_colours_3 = '\nbearing_colour_3 %d' % (0)
            bearing_colours_4 = '\nbearing_colour_4 %d' % (0)
            pos_format = '\npos_format %s' % ('t,x1,y1,x2,y2,numpix1,numpix2')
            bytes_per_cord = '\nbytes_per_coord %d' % (2)
            # bytes_per_cord = '\nbytes_per_coord %d' % (4)
            pixels_per_metre = '\npixels_per_metre %s' % (expter_values[9])
            num_pos_samples = '\nnum_pos_samples %d' % (time[-1] * Fs)
            start = '\ndata_start'

            write_order = [date, time_head, expter, comments, dur, sw_vers, num_colours,
                           min_x, max_x, min_y, max_y, window_min_x, window_max_x,
                           window_min_y, window_max_y, timebase_val, b_p_timestamp, sample_rate,
                           eeg_samp_per_pos, bearing_colours_1, bearing_colours_2,
                           bearing_colours_3, bearing_colours_4, pos_format, bytes_per_cord,
                           pixels_per_metre, num_pos_samples, start]

            f.writelines(write_order)

        if track_settings['mode'] == 'No Tracking':

            with open(filepath, 'rb+') as f:
                for t in time:
                    t_val = int(t * timebase)
                    t_byte = struct.pack('>i', t_val)  # big endian timestamps, 4 bytes long
                    f.seek(0, 2)
                    f.write(t_byte)

                    x1 = 0  # x1, signed short, 2 bytes long (MSB first)
                    y1 = 0  # y1, signed short, 2 bytes long (MSB first)
                    x2 = 0  # x2, signed short, 2 bytes long (MSB first)
                    y2 = 0
                    np1 = 0
                    np2 = 0
                    total_pix = 0
                    unused = 0

                    pos_byte = struct.pack('>8h', x1, y1, x2, y2, np1, np2, total_pix,
                                           unused)  # x1, signed short, 2 bytes long (MSB first)

                    f.seek(0, 2)
                    f.write(pos_byte)

            with open(filepath, 'rb+') as f:
                f.seek(0, 2)
                f.write(bytes('\r\ndata_end\r\n', 'utf-8'))
        else:
            print('Haven\'t coded the method for actual tracking yet')