import tkinter
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg)
from matplotlib import pyplot as plt, animation
from mpl_toolkits import mplot3d
from stl import mesh
import numpy as np
import serial
from serial.tools import list_ports
import time
import csv
import matplotlib
import seaborn as sns
matplotlib.use("TkAgg")

sns.set_style("whitegrid")
with sns.axes_style("whitegrid"):
    fig = plt.subplots()

for param in ['figure.facecolor', 'axes.facecolor', 'savefig.facecolor']:
    plt.rcParams[param] = '141417'  # bluish dark grey

for param in ['text.color', 'axes.labelcolor', 'xtick.color', 'ytick.color']:
    plt.rcParams[param] = '0.9'  # very light grey

fig = plt.figure()
fig.set_tight_layout(True)
ax1 = fig.add_subplot(1,2,2,projection="3d")
ax2 = fig.add_subplot(3,2,1)
ax3 = fig.add_subplot(3,2,3)
ax4 = fig.add_subplot(3,2,5)

COM = "/dev/cu.usbmodem14101"
data = mesh.Mesh.from_file('RocketFast.stl')
fieldnames = ["Time", "Yaw", "Pitch", "Roll", "Pressure", "Altitude", "R_Altitude", "B_Temp", "AccelX", "AccelY",
              "AccelZ", "GyroX", "GyroY", "GyroZ", "A_Temp"]

with open('data.csv', 'w', newline='') as csv_file:
    csv_file.truncate()
    csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    csv_writer.writeheader()

# Identify the correct port
ports = list_ports.comports()
for port in ports:
    print(port)

while True:
    try:
        serialCom = serial.Serial(port=COM, baudrate=115200, timeout=0.1)
        break
    except:
        print('Could not connect!')
        print('Retrying...')
        time.sleep(0.1)

time_x = []
ori_x = []
ori_y = []
ori_z = []
accel_x = []
accel_y = []
accel_z = []
gyro_x = []
gyro_y = []
gyro_z = []
alt = []
r_alt = []
a_temp = []
b_temp = []

class Processing():
    def animate(self, i):

        ctr = 0

        # Get data from Arduino
        try:
            while serialCom.inWaiting() > 0:
                # Read the line
                s_bytes = serialCom.readline()
                decoded_bytes = s_bytes.decode("utf-8").strip('\r\n')
                # print(decoded_bytes)

                ori = [float(x) for x in decoded_bytes.split()]

                # Parse the line
                # First line may be read in the middle, so the data would be incomplete.
                if ctr == 0:
                    ctr = ctr + 1
                else:
                    values = [float(x) for x in decoded_bytes.split()]
                    print(values)

                    # Write to CSV
                    with open('data.csv', 'a') as csv_file:
                        csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

                        info = {
                            "Time": values[0],
                            "Yaw": values[1],
                            "Pitch": values[2],
                            "Roll": values[3],
                            "Pressure": values[4],
                            "Altitude": values[5],
                            "R_Altitude": values[6],
                            "B_Temp": values[7],
                            "AccelX": values[8],
                            "AccelY": values[9],
                            "AccelZ": values[10],
                            "GyroX": values[11],
                            "GyroY": values[12],
                            "GyroZ": values[13],
                            "A_Temp": values[14],
                        }

                        csv_writer.writerow(info)
                        csv_file.close()


        except:
            # In real life you would want logic that would reattempt after certain delay.
            print('Communication lost...')
            print('Exiting Program...')
            exit()


        try:
            # Gets data for other graphs
            time_x.append(float(ori[0])/1000)
            ori_x.append(float(ori[1]))
            ori_y.append(float(ori[2]))
            ori_z.append(float(ori[3]))
            alt.append(float(ori[5]))
            r_alt.append(float(ori[6]))
            b_temp.append(float(ori[7]))
            accel_x.append(float(ori[8]))
            accel_y.append(float(ori[9]))
            accel_z.append(float(ori[10]))
            gyro_x.append(float(ori[11]))
            gyro_y.append(float(ori[12]))
            gyro_z.append(float(ori[13]))
            '''
            '''
            a_temp.append(float(ori[14]))

        except:
            return 1

        # Deals with 3D graphing
        if ori_y[len(ori_y)-2] != ori[1] or ori_x[len(ori_x)-2] != ori[1] or ori_z[len(ori_z)-2] != ori[1]:

            ax1.clear()
            data.rotate([1, 0, 0], np.radians(ori_y[len(ori_y)-2]-float(ori[2])))
            data.rotate([0, 1, 0], np.radians(-ori_x[len(ori_x)-2]+float(ori[1])))
            data.rotate([0, 0, 1], np.radians(-ori_z[len(ori_z)-2]+float(ori[3])))

            collection = mplot3d.art3d.Poly3DCollection(data.vectors)
            collection.set_facecolor('#17205B')
            ax1.add_collection3d(collection)

            scale = data.points.flatten("A")
            ax1.auto_scale_xyz(scale, scale, scale)

        if len(time_x) > 50:
            time_x.pop(0)
            ori_x.pop(0)
            ori_y.pop(0)
            ori_z.pop(0)
            alt.pop(0)
            r_alt.pop(0)
            accel_x.pop(0)
            accel_y.pop(0)
            accel_z.pop(0)
            gyro_x.pop(0)
            gyro_y.pop(0)
            gyro_z.pop(0)
            a_temp.pop(0)
            b_temp.pop(0)

        # Deals with plotting the orientation outputs
        ax2.clear()
        ax2.plot(time_x, ori_x, label="X-axis")
        ax2.plot(time_x, ori_y, label="Y-axis")
        ax2.plot(time_x, ori_z, label="Z-axis")
        ax2.set_ylabel("Orientation (deg)")
        ax2.set_xticklabels([])
        ax2.grid(b=True)

        # Deals with plotting altitude
        ax3.clear()
        ax3.plot(time_x, accel_x, label="X")
        ax3.plot(time_x, accel_y, label="Y")
        ax3.plot(time_x, accel_z, label="Z")
        ax3.set_ylabel("Acceleration (m/s^2)")
        ax3.set_xticklabels([])
        ax3.grid(b=True)

        # Deals with plotting temperature
        ax4.clear()
        ax4.plot(time_x, gyro_x, label="X")
        ax4.plot(time_x, gyro_y, label="Y")
        ax4.plot(time_x, gyro_z, label="Z")
        ax4.set_xlabel("Time")
        ax4.set_ylabel("Angular Rates (deg/s)")
        ax4.grid(b=True)

        ax2.legend(bbox_to_anchor=[0.5, 1.2], loc='upper center', ncol=3, mode="tight", borderaxespad=0)

        return 1


class Window():
    def __init__(self):

        root = tkinter.Tk()
        root.geometry("1500x735")
        root.wm_title("Graphical User Interface")

        canvas = FigureCanvasTkAgg(fig, master=root)
        canvas.draw()

        canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

        process = Processing()

        anim = animation.FuncAnimation(fig, process.animate)

        root.mainloop()


if __name__ == "__main__":
    win = Window()
