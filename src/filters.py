
import scipy

def notch_filt(data, Fs, band=10, freq=60, ripple=1, order=2, filter_type='butter', analog_filt=False,
               showresponse=0):
    '''# Required input defintions are as follows;
    # time:   Time between samples
    # band:   The bandwidth around the centerline freqency that you wish to filter
    # freq:   The centerline frequency to be filtered
    # ripple: The maximum passband ripple that is allowed in db
    # order:  The filter order.  For FIR notch filters this is best set to 2 or 3,
    #         IIR filters are best suited for high values of order.  This algorithm
    #         is hard coded to FIR filters
    # filter_type: 'butter', 'bessel', 'cheby1', 'cheby2', 'ellip'
    # data:         the data to be filtered'''

    cutoff = freq
    nyq = Fs / 2.0
    low = freq - band / 2.0
    high = freq + band / 2.0
    low = low / nyq
    high = high / nyq
    b, a =scipy.signal.iirfilter(order, [low, high], rp=ripple, btype='bandstop', analog=analog_filt, ftype=filter_type)

    filtered_data = np.array([])

    if len(data) != 0:
        if len(data.shape) > 1:  # lfilter is one dimensional so we need to perform for loop on multi-dimensional array
            # filtered_data = np.zeros((data.shape[0], data.shape[1]))
            filtered_data =scipy.signal.filtfilt(b, a, data, axis=1)
            # for channel_num in range(0, data.shape[0]):
            # filtered_data[channel_num,:] =scipy.signal.lfilter(b, a, data[channel_num,:])
            #   filtered_data[channel_num, :] =scipy.signal.filtfilt(b, a, data[channel_num, :])
        else:
            # filtered_data =scipy.signal.lfilter(b, a, data)
            filtered_data =scipy.signal.filtfilt(b, a, data)

    FType = ''
    if showresponse == 1:
        if filter_type == 'butter':
            FType = 'Butterworth'
        elif filter_type == 'cheby1':
            FType = 'Chebyshev I'
        elif filter_type == 'cheby2':
            FType = 'Chebyshev II'
        elif filter_type == 'ellip':
            FType = 'Cauer/Elliptic'
        elif filter_type == 'bessel':
            FType = 'Bessel/Thomson'

        if analog_filt == 1:
            mode = 'Analog'
        else:
            mode = 'Digital'

        if analog_filt is False:
            w, h =scipy.signal.freqz(b, a, worN=8000)  # returns the requency response h, and the normalized angular
            # frequencies w in radians/sample
            # w (radians/sample) * Fs (samples/sec) * (1 cycle/2pi*radians) = Hz
            f = Fs * w / (2 * np.pi)  # Hz
        else:
            w, h =scipy.signal.freqs(b, a, worN=8000)  # returns the requency response h, and the angular frequencies
            # w in radians/sec
            # w (radians/sec) * (1 cycle/2pi*radians) = Hz
            f = w / (2 * np.pi)  # Hz

        plt.figure(figsize=(20, 15))
        plt.subplot(211)
        plt.semilogx(f, np.abs(h), 'b')
        plt.xscale('log')
        plt.title('%s Filter Frequency Response (%s)' % (FType, mode))
        plt.xlabel('Frequency(Hz)')
        plt.ylabel('Gain [V/V]')
        plt.margins(0, 0.1)
        plt.grid(which='both', axis='both')
        plt.axvline(cutoff, color='green')

    return filtered_data

def iirfilt(bandtype, data, Fs, Wp, Ws=[], order=3, analog_val=False, automatic=0, Rp=3, As=60, filttype='butter',
            showresponse=0):
    '''Designs butterworth filter:
    Data is the data that you want filtered
    Fs is the sampling frequency (in Hz)
    Ws and Wp are stop and pass frequencies respectively (in Hz)

    Passband (Wp) : This is the frequency range which we desire to let the signal through with minimal attenuation.
    Stopband (Ws) : This is the frequency range which the signal should be attenuated.

    Digital: Ws is the normalized stop frequency where 1 is the nyquist freq (pi radians/sample in digital)
             Wp is the normalized pass frequency

    Analog: Ws is the stop frequency in (rads/sec)
            Wp is the pass frequency in (rads/sec)

    Analog is false as default, automatic being one has Python select the order for you. pass_atten is the minimal attenuation
    the pass band, stop_atten is the minimal attenuation in the stop band. Fs is the sample frequency of the signal in Hz.

    Rp = 0.1      # passband maximum loss (gpass)
    As = 60 stoppand min attenuation (gstop)


    filttype : str, optional
        The type of IIR filter to design:
        Butterworth : ‘butter’
        Chebyshev I : ‘cheby1’
        Chebyshev II : ‘cheby2’
        Cauer/elliptic: ‘ellip’
        Bessel/Thomson: ‘bessel’

    bandtype : {‘bandpass’, ‘lowpass’, ‘highpass’, ‘bandstop’}, optional
    '''

    cutoff = Wp

    if Ws != []:
        cutoff2 = Ws

    b, a = get_a_b(bandtype, Fs, Wp, Ws, order=order, Rp=Rp, As=As, analog_val=analog_val, filttype=filttype, automatic=automatic)

    if len(data) != 0:
        if len(data.shape) > 1:

            filtered_data = np.zeros((data.shape[0], data.shape[1]))
            filtered_data = scipy.signal.filtfilt(b, a, data, axis=1)
        else:
            filtered_data = scipy.signal.filtfilt(b, a, data)

    if showresponse == 1:  # set to 1 if you want to visualize the frequency response of the filter
        if filttype == 'butter':
            FType = 'Butterworth'
        elif filttype == 'cheby1':
            FType = 'Chebyshev I'
        elif filttype == 'cheby2':
            FType = 'Chebyshev II'
        elif filttype == 'ellip':
            FType = 'Cauer/Elliptic'
        elif filttype == 'bessel':
            FType = 'Bessel/Thomson'

        if analog_val:
            mode = 'Analog'
        else:
            mode = 'Digital'

        if not analog_val:
            w, h = scipy.signal.freqz(b, a, worN=8000)  # returns the requency response h, and the normalized angular
            # frequencies w in radians/sample
            # w (radians/sample) * Fs (samples/sec) * (1 cycle/2pi*radians) = Hz
            f = Fs * w / (2 * np.pi)  # Hz
        else:
            w, h = scipy.signal.freqs(b, a, worN=8000)  # returns the requency response h,
            # and the angular frequencies w in radians/sec
            # w (radians/sec) * (1 cycle/2pi*radians) = Hz
            f = w / (2 * np.pi)  # Hz

        plt.figure(figsize=(10, 5))
        plt.semilogx(f, np.abs(h), 'b')
        plt.xscale('log')

        if 'cutoff2' in locals():
            plt.title('%s Bandpass Filter Frequency Response (Order = %s, Wp=%s (Hz), Ws =%s (Hz))'
                      % (FType, order, cutoff, cutoff2))
        else:
            plt.title('%s Lowpass Filter Frequency Response (Order = %s, Wp=%s (Hz))'
                      % (FType, order, cutoff))

        plt.xlabel('Frequency(Hz)')
        plt.ylabel('Gain [V/V]')
        plt.margins(0, 0.1)
        plt.grid(which='both', axis='both')
        plt.axvline(cutoff, color='green')
        if 'cutoff2' in locals():
            plt.axvline(cutoff2, color='green')
            # plt.plot(cutoff, 0.5*np.sqrt(2), 'ko') # cutoff frequency
        plt.show()
    if len(data) != 0:
        return filtered_data

def get_a_b(bandtype, Fs, Wp, Ws, order=3, Rp=3, As=60, analog_val=False, filttype='butter', automatic=0):

    stop_amp = 1.5
    stop_amp2 = 1.4

    if not analog_val:  # need to convert the Ws and Wp to have the units of pi radians/sample
        # this is for digital filters
        if bandtype in ['low', 'high']:
            Wp = Wp / (Fs / 2)  # converting to fraction of nyquist frequency

            Ws = Wp * stop_amp

        elif bandtype == 'band':
            Wp = Wp / (Fs / 2)  # converting to fraction of nyquist frequency
            Wp2 = Wp / stop_amp2

            Ws = Ws / (Fs / 2)  # converting to fraction of nyquist frequency
            Ws2 = Ws * stop_amp2

    else:  # need to convert the Ws and Wp to have the units of radians/sec
        # this is for analog filters
        if bandtype in ['low', 'high']:
            Wp = 2 * np.pi * Wp

            Ws = Wp * stop_amp

        elif bandtype == 'band':
            Wp = 2 * np.pi * Wp
            Wp2 = Wp / stop_amp2

            Ws = 2 * np.pi * Ws
            Ws2 = Ws * stop_amp2

    if automatic == 1:
        if bandtype in ['low', 'high']:
            b, a = scipy.signal.iirdesign(wp=Wp, ws=Ws, gpass=Rp, gstop=As, analog=analog_val, ftype=filttype)
        elif bandtype == 'band':
            b, a = scipy.signal.iirdesign(wp=[Wp, Ws], ws=[Wp2, Ws2], gpass=Rp, gstop=As, analog=analog_val, ftype=filttype)
    else:
        if bandtype in ['low', 'high']:
            if filttype == 'cheby1' or 'cheby2' or 'ellip':
                b, a = scipy.signal.iirfilter(order, Wp, rp=Rp, rs=As, btype=bandtype, analog=analog_val, ftype=filttype)
            else:
                b, a = scipy.signal.iirfilter(order, Wp, btype=bandtype, analog=analog_val, ftype=filttype)
        elif bandtype == 'band':
            if filttype == 'cheby1' or 'cheby2' or 'ellip':
                b, a = scipy.signal.iirfilter(order, [Wp, Ws], rp=Rp, rs=As, btype=bandtype, analog=analog_val,
                                        ftype=filttype)
            else:
                b, a = scipy.signal.iirfilter(order, [Wp, Ws], btype=bandtype, analog=analog_val, ftype=filttype)

    return b, a