# Importing all required libraries for the code to function
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

# Setting the matplotlib style with the seaborn module
sns.set_style("whitegrid")
with sns.axes_style("whitegrid"):
    fig = plt.subplots()

for param in ['figure.facecolor', 'axes.facecolor', 'savefig.facecolor']:
    plt.rcParams[param] = '141417'  # bluish dark grey

for param in ['text.color', 'axes.labelcolor', 'xtick.color', 'ytick.color']:
    plt.rcParams[param] = '0.9'  # very light grey

# Creating the matplotlib figure with subplots and axes
fig = plt.figure()
fig.set_tight_layout(True)
ax1 = fig.add_subplot(1,2,2,projection="3d")
ax2 = fig.add_subplot(3,2,1)
ax3 = fig.add_subplot(3,2,3)
ax4 = fig.add_subplot(3,2,5)

# Defining the USB serial port for the Arduino
COM = "/dev/cu.usbmodem14101"

# Importing the stl file for the 3D graph
data = mesh.Mesh.from_file('RocketFast.stl')

# Fieldnames to be written on the CSV file
fieldnames = ["Time", "Yaw", "Pitch", "Roll", "Pressure", "Altitude", "R_Altitude", "B_Temp", "AccelX", "AccelY",
              "AccelZ", "GyroX", "GyroY", "GyroZ", "A_Temp"]

# Creating or opening the data.csv file and writing the fieldnames
# If the file existed it will be truncated before being used again.
with open('data.csv', 'w', newline='') as csv_file:
    csv_file.truncate()
    csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    csv_writer.writeheader()

# Lists all serial ports
ports = list_ports.comports()
for port in ports:
    print(port)

# Try statement within infinite loop to attempt connection to the Arduino until connection
while True:
    try:
        serialCom = serial.Serial(port=COM, baudrate=115200, timeout=0.1)
        break
    except:
        print('Could not connect!')
        print('Retrying...')
        time.sleep(0.1)

# Creating all required empty NumPy arrays
time_x = np.empty([1, 1])
ori_x = np.empty([1, 1])
ori_y = np.empty([1, 1])
ori_z = np.empty([1, 1])
accel_x = np.empty([1, 1])
accel_y = np.empty([1, 1])
accel_z = np.empty([1, 1])
gyro_x = np.empty([1, 1])
gyro_y = np.empty([1, 1])
gyro_z = np.empty([1, 1])
alt = np.empty([1, 1])
r_alt = np.empty([1, 1])
a_temp = np.empty([1, 1])
b_temp = np.empty([1, 1])


# Main processing class
class Processing():
    def animate(self, i):

        ctr = 0

        # Gets data from Arduino
        try:
            while serialCom.inWaiting() > 0:
                # Read the serial line
                s_bytes = serialCom.readline()
                # Decode serial data
                decoded_bytes = s_bytes.decode("utf-8").strip('\r\n')
                # print(decoded_bytes)

                # Place serial data in list
                ori = [float(x) for x in decoded_bytes.split()]

                # Parse the line
                # First line may be read in the middle, so the data would be incomplete.
                if ctr == 0:
                    ctr = ctr + 1
                else:
                    values = [float(x) for x in decoded_bytes.split()]
                    print(values)

                    # Write to data to CSV
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
            # Exit program if communication is lost
            # In real life you would want logic that would reattempt after certain delay.
            print('Communication lost...')
            print('Exiting Program...')
            exit()


        try:
            # Gets data for other graphs by appending to numpy arrays from list.
            np.append(time_x, float(ori[0])/1000)
            np.append(ori_x, float(ori[1]))
            np.append(ori_y, float(ori[2]))
            np.append(ori_z, float(ori[3]))
            np.append(alt, float(ori[5]))
            np.append(r_alt, float(ori[6]))
            np.append(b_temp, float(ori[7]))
            np.append(accel_x, float(ori[8]))
            np.append(accel_y, float(ori[9]))
            np.append(accel_z, float(ori[10]))
            np.append(gyro_x, float(ori[11]))
            np.append(gyro_y, float(ori[12]))
            np.append(gyro_z, float(ori[13]))
            np.append(a_temp, float(ori[14]))

        except:
            return 1

        # Checks to see if orientation has changed in any axis
        # This is as this process would take a few cycles to compute,
        # if we can skip it when not necessary the program will be faster.
        if ori_y[ori_y.size-2] != ori[1] or ori_x[ori_x.size-2] != ori[1] or ori_z[ori_z.size-2] != ori[1]:

            # change the rotation of the 3 sides
            ax1.clear()
            data.rotate([1, 0, 0], np.radians(ori_y[ori_y.size-2]-float(ori[2])))
            data.rotate([0, 1, 0], np.radians(-ori_x[ori_x.size-2]+float(ori[1])))
            data.rotate([0, 0, 1], np.radians(-ori_z[ori_z.size-2]+float(ori[3])))

            # Graph the STL file onto the graph.
            collection = mplot3d.art3d.Poly3DCollection(data.vectors)
            collection.set_facecolor('#17205B')
            ax1.add_collection3d(collection)

            scale = data.points.flatten("A")
            ax1.auto_scale_xyz(scale, scale, scale)

        # If the size of the array has become larger than 50, delete the first index
        if time_x.size > 50:
            np.resize(time_x, (1, 50))
            np.resize(ori_x, (1, 50))
            np.resize(ori_y, (1, 50))
            np.resize(ori_z, (1, 50))
            np.resize(alt, (1, 50))
            np.resize(r_alt, (1, 50))
            np.resize(accel_x, (1, 50))
            np.resize(accel_y, (1, 50))
            np.resize(accel_z, (1, 50))
            np.resize(gyro_x, (1, 50))
            np.resize(gyro_y, (1, 50))
            np.resize(gyro_z, (1, 50))
            np.resize(a_temp, (1, 50))
            np.resize(b_temp, (1, 50))

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

        # Sets the legend to be above the first graph
        ax2.legend(bbox_to_anchor=[0.5, 1.2], loc='upper center', ncol=3, mode="tight", borderaxespad=0)

        return 1


# Creates the tkinter window and calls the main procesing class.
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


# Run the file while preventing accidental invokes
if __name__ == "__main__":
    win = Window()
