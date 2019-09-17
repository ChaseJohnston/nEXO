import glob
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks, find_peaks_cwt
from peak_detect import peakdet
import math
import os

#must run pulse analysis first

class main:
    def slope(self, x1, y1, x2, y2):
        m = (y2 - y1)/(x2 - x1)
        return m
    def pulse_volts(self, peak_adc):
        #signal max is 1.4V and resolution is 4096 counts
        val = (peak_adc * 1.4) / 4096
        return val * 1000
    def gain(self, peak_volts):
        #input peak in mV
        #test cap is 200 fC and pulse height for step 0 is 18.75 mV
        #returns gain in units of mV/fC
        test_charge = 200 * 0.01875
        return peak_volts / test_charge
    def distance(self, x1, y1, x2, y2 ):
        dist = round(math.sqrt(pow((x2 - x1), 2) + pow((y2 - y1), 2)), 2)
        return dist
    def data_plot(self, values, x, choice):
        #import data
        x[0] = 1
        self.cal_dir_name = (glob.glob(self.cur_path + self.calibration_folder)[0]) + "\\"
        if choice == 'RMS' or choice == "PULSE":
            if choice == 'PULSE':
                directory = self.cal_dir_name + "25.0mV_3.0us_200mV\\chip_data" #only use this configuration
            else:
                directory = self.cal_dir_name + "25.0mV_3.0us_200mV\\chip_data_RMS" #only use this configuration
        else:
            raise ValueError("Invalid Input")
        #print(directory)

        chn = 0
        place = 0
        #path to chip data file
        for chip in range(4):
                path = directory + "\\data_" + str(chip) + ".dat"
                with open(path, "r") as f:
                    data = f.readlines()
                    for i in data:
                        val = int(i.rstrip(), 16)
                        if(val == 1):
                            chn = chn + 1
                            place = 0
                        else:
                            #print(str(chip) + ":" + str(chn) + ":" + str(place) + ":" + str(val))
                            if(chn != 16):
                                values[chip][chn][place] = val
                        if(val != 1):
                            place = place + 1
                chn = 0
        f.close()

        #self.raw_data = chip_data

    def loop(self):
        choice = input("PULSE or RMS analysis: ")
        flag = []
        self.cal_dir_name = (glob.glob(self.cur_path + self.calibration_folder)[0]) + "\\"
        if choice == 'PULSE':
            directory = self.cal_dir_name + "25.0mV_3.0us_200mV\\chip_data" #only use this configuration
        else:
            directory = self.cal_dir_name + "25.0mV_3.0us_200mV\\chip_data_RMS" #only use this configuration

        peakheights = []

        flag.append(0)
        values = np.zeros((4, 16, 155154))
        #raw_in = input("Enter desired chip (0, 1, 2, 3):")
        #path = directory + "//GainResults_chip" + raw_in + ".txt"
        #file_write = open(path, 'w')
        #file_write.write("Chip " +raw_in + "\n")

        for chip in range(4):
            flag[0] = 0
            if choice == 'RMS':
                print("RMS analysis for Chip " + str(chip))
                path = directory + "//RMSResults_chip" + str(chip) + ".txt"
                file_write = open(path, 'w')
                for chn in range(16):
                    if flag[0] != 1:
                        main().data_plot(values, flag, choice)
                    plot1 = values[int(chip)][int(chn)][0:50000]

                    #base = int((0.2 / 1.4) * 4096)
                    #print(base)
                    rms = np.sqrt(np.mean((plot1 - np.mean(plot1)) ** 2))

                    fig, ax = plt.subplots(figsize=(20,20))
                    x = np.linspace(0, len(plot1), num=len(plot1))
                    ax.plot(x, plot1, color='blue', linestyle='-',label="Chip $" + str(chip) + "$, Channel $" + str(chn) + "$")

                    self.cal_dir_name = (glob.glob(self.cur_path + self.calibration_folder)[0]) + "\\"
                    directory = self.cal_dir_name + "25.0mV_3.0us_200mV\\chip_data_RMS"  # only use this configuration

                    if not os.path.exists(directory + "\\chip_data_plots"):
                        os.makedirs(directory + "\\chip_data_plots\\")

                    path = directory + "\\chip_data_plots\\"
                    os.chdir(path)

                    plt.savefig("Chip_" + str(chip) + "_Channel_" + str(chn) + ".png")
                    plt.close()

                    file_write.write("%f\n" % rms)

                file_write.close()
            else:
                print("Gain analysis for Chip " + str(chip))
                path = directory + "//GainResults_chip" + str(chip) + ".txt"
                file_write = open(path, 'w')
                for chn in range(16):

                    #print(flag[0])
                    if flag[0] != 1:
                        main().data_plot(values, flag, choice)

                    plot1 = values[int(chip)][int(chn)][0:155154]
                    #plot2 = values[int(raw_in3)][int(raw_in4)][0:1000]
                    #base = int((0.2 / 1.4) * 4096)
                    #print(base)
                    rms = np.sqrt(np.mean((plot1 ** 2)))

                    #maxs, mins = peakdet(plot1,150)
                    peaks, _ = find_peaks(plot1, height=rms+100)





                    #fig, ax = plt.subplots(figsize=(20,20))
                    #x = np.linspace(0, len(plot1), num=len(plot1))

                    #print(plot1[4708])

                    maxX = []
                    removed = []
                    maxY = []
                    dis1 = []
                    #ax.grid()
                    #ax.plot(x, plot1, color='blue', linestyle='-',label="Chip $" + str(chip) + "$, Channel $" + str(chn) + "$")
                    #ax.hlines(y=rms, xmin=0, xmax=len(plot1), color='red', linestyle=':')
                    #print(rms)

                    if(peaks != [] and rms < 1200):
                        for x in peaks:
                            maxX.append(x)
                            maxY.append(plot1[x])

                        for i in range(len(peaks)):
                            dis1.append(main().distance(peaks[i], rms, peaks[i], plot1[peaks[i]]))

                        #for i in range(len(dis1)):
                            #ax.plot([peaks[i], peaks[i]], [rms, plot1[peaks[i]]], color='r')

                        #for i in range(len(peaks)):
                            #ax.scatter(peaks[i], plot1[peaks[i]], color='r')


                    #ax.set_ylabel('ADC Counts')
                    #ax.set_xlabel('Time (us)') #needs to be divided by 2
                    #ax.legend(loc='lower center', bbox_to_anchor=(0, 1.01), ncol=2)


                    #save plot to folder
                    self.cal_dir_name = (glob.glob(self.cur_path + self.calibration_folder)[0]) + "\\"
                    directory = self.cal_dir_name + "25.0mV_3.0us_200mV\\chip_data"  # only use this configuration

                    #if not os.path.exists(directory + "\\chip_data_plots"):
                    #    os.makedirs(directory + "\\chip_data_plots\\")

                    #path = directory + "\\chip_data_plots\\"
                    #os.chdir(path)

                    #plt.savefig("Chip_" + str(chip) + "_Channel_" + str(chn) + ".png")
                    #plt.close()
                    avgpeak = 0
                    if len(dis1) != 0 and rms < 1200:
                        for x in dis1:
                            avgpeak = avgpeak + x
                        avgpeak = avgpeak / len(dis1)

                        #peakInVolts = main().pulse_volts(avgpeak)
                        charge = 200*0.01875
                        #gainVal = main().gain(peakInVolts)
                        file_write.write("%f\n" % avgpeak)

                    else:
                        file_write.write("1\n")
                        #file_write.write("Error for channel " + str(chn) + ", no pulses found\n")

                file_write.close()
                #print("Analysis complete for chip " + str(chip))


    def plot_rms(self):
        print("RMS plot started...")
        self.cal_dir_name = (glob.glob(self.cur_path + self.calibration_folder)[0]) + "\\"
        directory = self.cal_dir_name + "25.0mV_3.0us_200mV\\chip_data_RMS"  # only use this configuration


    def ENC(self):
        self.cal_dir_name = (glob.glob(self.cur_path + self.calibration_folder)[0]) + "\\"
        directory = self.cal_dir_name + "25.0mV_3.0us_200mV\\chip_data_RMS"  # only use this configuration
        chip0_R = []
        chip1_R = []
        chip2_R = []
        chip3_R = []

        for chip in range(4):
            with open(directory + "//RMSResults_chip" + str(chip) + ".txt", 'r') as f:
                val = f.readlines()
                for i in val:
                    i = i.strip('\n')
                    if (chip == 0):
                        chip0_R.append(float(i))
                    if (chip == 1):
                        chip1_R.append(float(i))
                    if (chip == 2):
                        chip2_R.append(float(i))
                    if (chip == 3):
                        chip3_R.append(float(i))
            f.close()

        directory = self.cal_dir_name + "25.0mV_3.0us_200mV\\chip_data"  # only use this configuration

        chip0_G = []
        chip1_G = []
        chip2_G = []
        chip3_G = []

        for chip in range(4):
            with open(directory + "//GainResults_chip" + str(chip) + ".txt", 'r') as f:
                val = f.readlines()
                for i in val:
                    i = i.strip('\n')
                    if (chip == 0):
                        chip0_G.append(float(i))
                    if (chip == 1):
                        chip1_G.append(float(i))
                    if (chip == 2):
                        chip2_G.append(float(i))
                    if (chip == 3):
                        chip3_G.append(float(i))
            f.close()

        charge = 200 * 0.01875
        e = 0.00016021766
        val = 0
        for chip in range(4):
            with open(directory + "//ENCResults_chip" + str(chip) + ".txt", 'w') as f:
                for chn in range(16):
                    if (chip == 0):
                        val = ((chip0_R[chn] / chip0_G[chn]) * charge) / e
                        #print(((1 / chip0_G[chn]) * charge) / e)
                    if (chip == 1):
                        val = ((chip1_R[chn] / chip1_G[chn]) * charge) / e
                        print('factor:',chip1_G[chn])
                    if (chip == 2):
                        val = ((chip2_R[chn] / chip2_G[chn]) * charge) / e
                    if (chip == 3):
                        val = ((chip3_R[chn] / chip3_G[chn]) * charge) / e
                    f.write("Channel " + str(chn) + " ENC: " + "%f\n" % val)
            f.close()



    #function for ploting gain
    def plot_gain(self):
        print("Gain plot started...")
        self.cal_dir_name = (glob.glob(self.cur_path + self.calibration_folder)[0]) + "\\"
        directory = self.cal_dir_name + "25.0mV_3.0us_200mV\\chip_data"  # only use this configuration

        chip0 = []
        chip1 = []
        chip2 = []
        chip3 = []

        for chip in range(4):
            with open(directory + "//GainResults_chip" + str(chip) + ".txt", 'r') as f:
                val = f.readlines()
                for i in val:
                    i = i.strip('\n')
                    if(chip == 0):
                        chip0.append(float(i))
                    if(chip == 1):
                        chip1.append(float(i))
                    if(chip == 2):
                        chip2.append(float(i))
                    if(chip == 3):
                        chip3.append(float(i))

        fig, ax = plt.subplots(figsize=(20,20))

        x = np.linspace(0, 15, num=16)

        if not os.path.exists(directory + "\\gain_plots"):
            os.makedirs(directory + "\\gain_plots\\")

        os.chdir(directory + "\\gain_plots\\")

        ax.grid()
        ax.set_ylim(0, 30)
        ax.plot(x, chip0, color='b', label="Chip 0 Gain")
        ax.set_ylabel("Gain mV/fC")
        ax.set_xlabel("Channel")

        plt.savefig("Gains0.png")
        plt.cla()

        ax.grid()
        ax.set_ylim(0, 30)
        ax.plot(x, chip1, color='b', label="Chip 1 Gain")
        ax.set_ylabel("Gain mV/fC")
        ax.set_xlabel("Channel")

        plt.savefig("Gains1.png")
        plt.cla()

        ax.grid()
        ax.set_ylim(0, 30)
        ax.plot(x, chip2, color='b', label="Chip 2 Gain")
        ax.set_ylabel("Gain mV/fC")
        ax.set_xlabel("Channel")

        plt.savefig("Gains2.png")
        plt.cla()

        ax.grid()
        ax.set_ylim(0, 30)
        ax.plot(x, chip3, color='b', label="Chip 3 Gain")
        ax.set_ylabel("Gain mV/fC")
        ax.set_xlabel("Channel")

        plt.savefig("Gains3.png")

        print("Gain plot finished!")







    def __init__(self):
        self.cur_path = "G:\\nEXO\\2019_09_12_1\\" #must update to most recent folder
        self.cal_dir_name = None
        self.calibration_folder = "*Calibration*"
        #self.raw_data = np.zeros((4,16,155154))

if __name__ == "__main__":
    #main().data_plot()
    main().loop()
    main().plot_rms()
    main().plot_gain()
    #main().ENC()