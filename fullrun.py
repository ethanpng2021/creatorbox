import osmnx as ox
import networkx as nx
import pandas as pd
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point
import matplotlib.animation as animation
import random
from geographiclib.geodesic import Geodesic
import time


geod = Geodesic.WGS84
G = ox.graph_from_bbox(1.3763, 1.3007, 103.6492, 103.7840, network_type='drive') #, simplify=True)
G = ox.add_edge_speeds(G)
G = ox.add_edge_travel_times(G)

projected_graph = ox.project_graph(G, to_crs="EPSG:3395")
Gc = ox.consolidate_intersections(projected_graph, dead_ends=True)
edges = ox.graph_to_gdfs(ox.get_undirected(Gc), nodes=False)

vehnumber = 10
routes = []
route = []
allAngleList = []
direction = []
all_route_roadnames = []
all_route_speeds = []

angleList = []
direzione = []
route_roadnames = []
route_speed = []

LEFT_SIG = ""
STRAIGHT_SIG = ""
RIGHT_SIG = ""

columns = ['vehID', 'subroute', 'speed', 'turn', 'angle', 'lengthOfSubroute']
data = []
df = pd.DataFrame()

for iroute in range(vehnumber):
    
    try:
        y0 = 0.0
        x0 = 0.0
        
        lat = round(random.uniform(1.3007, 1.3763), 5)
        lon = round(random.uniform(103.6492, 103.7840), 5)
        good_orig_node = ox.get_nearest_node(G, (lat, lon), method='euclidean')

        lat = round(random.uniform(1.3007, 1.3763), 5)
        lon = round(random.uniform(103.6492, 103.7840), 5)
        good_dest_node = ox.get_nearest_node(G, (lat, lon), method='euclidean')

        routep1 = nx.shortest_path(G, good_orig_node, good_dest_node)
        lengthOfRoute1 = nx.shortest_path_length(G, good_orig_node, good_dest_node, weight='length')

        lat = round(random.uniform(1.3007, 1.3763), 5)
        lon = round(random.uniform(103.6492, 103.7840), 5)
        next_dest_node = ox.get_nearest_node(G, (lat, lon), method='euclidean')

        routep2 = nx.shortest_path(G, good_dest_node, next_dest_node)
        lengthOfRoute2 = nx.shortest_path_length(G, good_dest_node, next_dest_node, weight='length')

        route = routep1 + routep2
        lengthOfRoute = lengthOfRoute1 + lengthOfRoute2
        
        lor = round(lengthOfRoute/1000.0, 2)
        
        angleList = []
        direzione = []
        route_roadnames = []
        route_speed = []

        ## iterate through roads (i.e. edges) in a route
        for irou in route:
            
            incident_edges = edges[(edges['u_original']==irou) | (edges['v_original']==irou)]
            
            for _, edge in incident_edges.fillna('').iterrows():
                #print("vehID: ", iroute, " Road name: ", edge['name'], ", ", "Speed: ", edge['speed_kph'], " kmph")
                instantroad = edge['name']
                instantspd = edge['speed_kph']
                route_roadnames.append(edge['name'])
                route_speed.append(edge['speed_kph'])
                
                latlat = G.nodes[irou]['y']
                lonlon = G.nodes[irou]['x']

                #print("Left! {:.3f} degrees.".format(turnAngle['azi1']))
                direzione.append("straight")
                
                TURN_SIG = "straight"
                
                #print("GPS Coordinates: ", latlat, ", ", lonlon)
                turnAngle = geod.Inverse(latlat,lonlon,y0,x0)

                if turnAngle['azi1'] > 45.0 and turnAngle['azi1'] < 135.0:
                    #print("Right! {:.3f} degrees.".format(turnAngle['azi1']))
                    direzione.append("right")
                 
                    TURN_SIG = "right"
                if (turnAngle['azi1'] > -135.0 and turnAngle['azi1'] < -45.0):
                   #print("Left! {:.3f} degrees.".format(turnAngle['azi1']))
                    direzione.append("left")
                    TURN_SIG = "left"
                  
                y0 = latlat
                x0 = lonlon
                
                angleList.append(turnAngle['azi1'])

                values = [iroute, instantroad, instantspd, TURN_SIG, turnAngle['azi1'], edge.get('length', None)]
                zipped = zip(columns, values)
                a_dictionary = dict(zipped)
                #print(a_dictionary)
                data.append(a_dictionary)

            df = df.append(data, True)
            
            my_dict = {i:round(direzione.count(i)/len(direzione)*100.0,1) for i in direzione}
            
            #print("vehID: ", iroute, " Total route length: ", lor, " km. ", "TurnRatio: ", my_dict)
      
    except:
        
        pass

    routes.append(route)
    allAngleList.append(angleList)
    direction.append(direzione)
    all_route_roadnames.append(route_roadnames)
    all_route_speeds.append(route_speed)

##Generate output file
#df.to_csv("output.csv")

print("No. of Vehicles/Routes: ", len(routes))

# Extrat coordinates of route nodes 
route_coorindates = []

for rou in routes:
    points = []
    for node_id in rou:
        x = projected_graph.nodes[node_id]['x']
        y = projected_graph.nodes[node_id]['y']
        points.append([x, y])
        
    route_coorindates.append(points)

n_routes = len(route_coorindates)

print("Extracted routes: ", n_routes)
max_route_len = max([len(x) for x in route_coorindates])

# Prepare the layout
gdf = ox.geometries_from_bbox(1.3763, 1.3007, 103.6492, 103.7840, tags={"building": True})
gdf_proj = ox.project_gdf(gdf, to_crs="EPSG:3395")

fig, ax = ox.plot_graph(projected_graph, node_size=0, edge_linewidth=1.5, edge_color='#2C2E2C', show=False, close=False, bgcolor='#12830E') #figsize=(12,8) for larger plots  

gdf_proj.plot(ax=ax, linewidth=1, alpha=0.8, color='#F5F5DC')

scatter_list = []

# Plot the first scatter plot (starting nodes = initial car locations)
for j in range(n_routes):
    scatter_list.append(ax.scatter(route_coorindates[j][0][0], # x coordiante of the first node of the j route
                                   route_coorindates[j][0][1], # y coordiante of the first node of the j route
                                   label=f'car {j}', 
                                   alpha=.75))
    
#plt.legend(frameon=False)

def animate(i):
   
    # Iterate over all routes
    for j in range(n_routes):
        # Some routes are shorter than others
        # Therefore we need to use try except with continue construction
        try:
            # Try to plot a scatter plot
            x_j = route_coorindates[j][i][0]
            y_j = route_coorindates[j][i][1]
            scatter_list[j].set_offsets(np.c_[x_j, y_j])
        except:
            continue

# Make the animation
#animation = FuncAnimation(fig, animate, frames=max_route_len)

line_ani = animation.FuncAnimation(fig, animate, interval=1)

plt.show()  
#line_ani.save('myAnimation.gif') #writer='imagemagick', fps=24, dpi=300)
# HTML(animation.to_jshtml()) # to display animation in Jupyter Notebook
#line_ani.save('animation.mp4', dpi=300) # to save animation
#line_ani.save('lines.mp4', writer=writer)


