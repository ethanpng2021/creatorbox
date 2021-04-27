# How to Generate Random Routes and Run Traffic Simulation the Easy Way
### A simple Pythonic way to simulate traffic on your local map without using SUMO or VISSIM
\
When you are doing research in urban mobility such as traffic congestion, most people would be using either SUMO or VISSIM. Both are very good platforms as they have lots of functions and good editors.
However, there are situations when you only need a quickie Python script for let’s say a paper you are working on without spending weeks mastering the two software and their APIs.
\
\
This is how I do it. To begin, you have to determine the boundaries of the area you want to simulate. Go to the site https://www.openstreetmap.org/ and type in your district, town, or city to display the map. Next, click **Export** on the top bar. You will see a box containing 4 variables. They are the GPS coordinates representing the **North**, **South**, **East**, and **West** boundaries. Try to zoom in and out the map using your mouse wheel to choose the region of your choice. Copy down the 4 variables when you have decided on the area. Download my Python script *fullrun.py* and insert the 4 GPS values into the respective positions of the following lines:

>Line 15: G = ox.graph_from_bbox(1.3763 __(north)__, 1.3007 __(south)__, 103.6492 __(east)__, 103.7840 __(west)__, network_type=’drive’)

>Line 50: lat = round(random.uniform(1.3007, 1.3763), 5)

>Line 51: lon = round(random.uniform(103.6492, 103.7840), 5)  

>Line 54: lat = round(random.uniform(1.3007, 1.3763), 5)

>Line 55: lon = round(random.uniform(103.6492, 103.7840), 5)

>Line 61: lat = round(random.uniform(1.3007, 1.3763), 5)

>Line 62: lon = round(random.uniform(103.6492, 103.7840), 5)

>Line 161: gdf = ox.geometries_from_bbox(1.3763, 1.3007, 103.6492, 103.7840, tags={"building": True})

After that, run *fullrun.py* in IDLE (I use Python Version 3.7.5). It will display an animated plot where you will see vehicles (represented by dots) running around.
\
\
If you want to have a copy of the generated output for machine learning, uncomment this line:

>Line 139: #df.to_csv(“output.csv”)

![Output Excel file](https://i.imgur.com/cJ2Gywq.jpg)


If you want to increase the number of vehicles, change the number on this line:

>Line 23: vehnumber = 10

Output display: https://i.imgur.com/riH10a7.gifv

