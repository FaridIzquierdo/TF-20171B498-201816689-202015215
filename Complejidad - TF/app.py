import csv
import random
import tkinter
from tkinter import *
from xml.dom.minicompat import NodeList
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import math
import heapq as hq


class Interfaz():
    def __init__(self,window):
        self.window=window
        self.window.geometry("920x500")
        self.window.title("LIMAPP")
        self.window.config(bg="#005")

        # BackGround
        self.img = PhotoImage(file="images/image.png")
        self.lbl_img = Label(window, image=self.img)
        self.lbl_img.pack()

        # Etiqueta del titulo
        self.title = Label(text="LIMAPP", font=("Arial", 30))
        # title= Label(window, text="WAZE")
        self.title.place(x=400, y=10)

        # Etiqueta del x1 y1
        self.x1_label = Label(text="latitud (X1)", font=("Arial", 10)).place(x=550, y=130)
        self.y1_label = Label(text="longitud (Y1)", font=("Arial", 10)).place(x=720, y=130)

        # Etiqueta del x2 y2
        self.x2_label = Label(text="latitud (X2)", font=("Arial", 10)).place(x=550, y=211)
        self.y2_label = Label(text="longitud (Y2)", font=("Arial", 10)).place(x=720, y=211)

        # Botón graficar
        self.button_graph = Button(self.window, font=("Arial", 9), text="updatePlot", command=self.updatePlot, bg="#fff")
        self.button_graph.place(x=700, y=260)

        # Caja x1 y y1
        self.x1 = tkinter.StringVar()
        self.y1 = tkinter.StringVar()
        self.box_x1 = Entry(self.window, textvariable = self.x1, font=("Arial", 10), width = 12).place(x=620, y=132)
        self.box_y1 = Entry(self.window, textvariable = self.y1, font=("Arial", 10), width = 12).place(x=802, y=132)

        # Caja x2 y y2
        self.x2 = tkinter.StringVar()
        self.y2 = tkinter.StringVar()
        self.box_x2 = Entry(self.window, textvariable = self.x2, font=("Arial", 10), width = 12).place(x=620, y=212)
        self.box_y2 = Entry(self.window, textvariable = self.y2, font=("Arial", 10), width = 12).place(x=802, y=212)

        # Etiqueta Subtitulo 1
        self.subtitle1_label = Label(text="Coordenada geográfica de la intersección origen: ", font=("Arial", 10)).place(x=550, y=100)

        # Etiqueta Subtitulo 2
        self.subtitle2_label = Label(text="Coordenada geográfica de la intersección final: ", font=("Arial", 10)).place(x=550, y=180)

        # Etiqueta hora
        self.text_hour = Label(text="Hora:", font=("Arial", 10)).place(x=550, y=350)

        # Caja hora
        self.hour_changed = tkinter.StringVar()
        self.box_hour = Entry(self.window, textvariable = self.hour_changed,font=("Arial", 10), width = 12).place(x=590, y=350)

        # Botón hora confirmar
        self.button_graph = Button(self.window, font=("Arial", 10),text="Cambiar Hora", command = self.updateHour, bg="#fff").place(x=690, y=350)

        #Check Button
        self.selected = tkinter.IntVar()
        self.trafico=Checkbutton(self.window, font=("Arial", 10), text=("Visualizar Tráfico"), variable = self.selected, onvalue = 1, offvalue = 0, command = self.plot).place(x=550, y=380)

        self.hour = self.randomHour()
        #lima_streets_list = self.loadFile('datasets/Lima-calles.csv')
        self.lima_intersections_list = self.loadFile('datasets/Lima-intersecciones.csv', traffic_intensity_list = True)
        self.node_list = []           #Lista de intersecciones (NODOS)
        self.node_list_id = []        #Solo lista de los id de las intersecciones
        self.ad_list = []             #Lista de adyacencia
        self.x_data = []
        self.y_data = []
        self.nodeList()
        self.change_id()
        self.adjacencyList()          #Edita la lista de adyancencia y asigna los pesos correspondientes
        self.hour = self.randomHour()      #Cambiamos la hora
        self.updateTrafficIntensity() #Actualizamos los pesos de las aristas

        self.figure = plt.figure(figsize = (5,4), dpi = 100)
        self.plot()

    def updateHour(self):
        self.hour = self.hour_changed.get()
        self.updateTrafficIntensity()
        if self.selected.get() == 1:
            self.plot()
        return None

    def plot(self, event = None):
        _selected = self.selected.get()
        chart = FigureCanvasTkAgg(self.figure, self.window)
        chart.get_tk_widget().place(x=20, y=80)
        graph = self.figure.add_subplot(111)

        if _selected == 0:
            for row in self.lima_intersections_list:
                graph.plot([float(row[11]), float(row[13])], [float(row[12]), float(row[14])], 'gray')
        else: 
            for row in self.lima_intersections_list:
                if 0 <= row[16] <= 1.5:
                    graph.plot([float(row[11]), float(row[13])], [float(row[12]), float(row[14])], 'green')
                elif 1.5 < row[16] <= 3:
                    graph.plot([float(row[11]), float(row[13])], [float(row[12]), float(row[14])], 'orange')
                else:
                    graph.plot([float(row[11]), float(row[13])], [float(row[12]), float(row[14])], 'red')
        return None
    
    def updatePlot(self, event=None):
        # Mostrar grafo de la ciudad
        chart = FigureCanvasTkAgg(self.figure, self.window)
        chart.get_tk_widget().place(x=20, y=80)
        graph = self.figure.add_subplot(111)

        for row in self.lima_intersections_list:
            graph.plot([float(row[11]), float(row[13])], [float(row[12]), float(row[14])], 'gray')

        # Mostrar puntos: Interseccion origen y final
        x1 = self.x1.get()
        y1 = self.y1.get()

        x2 = self.x2.get()
        y2 = self.y2.get()

        start_node_index = self.node_list.index([x1,y1])
        final_node_index = self.node_list.index([x2,y2])

        graph.scatter(float(x1), float(y1), s = 15, color='blue', zorder=2)
        graph.scatter(float(x2), float(y2), s = 15, color='blue', zorder=2)

        # Dijkstra
        dijkstra_path = self.dijkstraPath(self.ad_list, start_node_index, final_node_index)

        for street in dijkstra_path:
            graph.plot(street[0], street[1], 'blue')

        # Algoritmo #2

        # Algoritmo #3

        return None

    def randomHour(self):
        random_h = random.randrange(24)
        random_m = random.randrange(60)

        hour = ""
        if random_h < 10:
            hour += str(0) + str(random_h) + ":"
        else:
            hour += str(random_h) + ":"

        if random_m < 10:
            hour += str(0) + str(random_m)
        else:
            hour += str(random_m)
        return hour

    def trafficIntensity(self):
        temp = []

        for i in range(24):
            if i < 4:
                intensity = round(random.uniform(0,0.3),2)
            else:
                intensity = round(random.uniform(0.3,5),2)
            temp.append(intensity)

        return temp

    def loadFile(self, fileName, traffic_intensity_list = False):
        data = []
        with open(fileName, encoding="ISO-8859-1") as file_name:  
            file = csv.reader(file_name)
            for row in file:
                data.append(row)
                if traffic_intensity_list == True:
                    intensity_list = self.trafficIntensity()
                    row.append(intensity_list)
                    weight = float(row[7]) * intensity_list[int(self.hour[:2])]
                    row.append(weight)
        return data

    def nodeList(self):
        for row in self.lima_intersections_list:

            id_origin_interection = row[5]
            id_final_intersection = row[6]

            if id_origin_interection not in self.node_list_id:
                temp = []
                temp.append(row[11])                #Latitud_Origen_Interseccion
                temp.append(row[12])                #Longitud_Origen_Interseccion
                self.node_list.append(temp)

                self.ad_list.append([])
                self.node_list_id.append(id_origin_interection)

            if id_final_intersection not in self.node_list_id:
                temp = []
                temp.append(row[13])                #Latitud_Destino_Interseccion
                temp.append(row[14])                #Longitud_Destino_Interseccion
                self.node_list.append(temp)

                self.ad_list.append([])
                self.node_list_id.append(id_final_intersection)
        return None

    def change_id(self):
        for row in self.lima_intersections_list:
            row[5] = self.node_list_id.index(row[5])
            row[6] = self.node_list_id.index(row[6])

        self.node_list_id.clear()
        return None

    def adjacencyList(self):
        n = len(self.node_list)

        for row in self.lima_intersections_list:
            index_origin = row[5]
            index_final = row[6]

            weight = row[16]

            self.ad_list[index_origin].append([index_final, weight])
            self.ad_list[index_final].append([index_origin, weight])
        return None

    def updateTrafficIntensity(self):
        for row in self.lima_intersections_list:
            index_origin = row[5]
            index_final = row[6]

            weight = float(row[7]) * row[15][int(self.hour[:2])]
            row[16] = weight

            for edge in self.ad_list[index_origin]:
                if edge[0] == index_final:
                    edge[1] = weight

            for edge in self.ad_list[index_final]:
                if edge[0] == index_origin:
                    edge[1] = weight
        return None
    
    def dijkstra(self, G, n, s_node, f_node):
        visited = [False]*n
        path = [None]*n
        cost = [math.inf]*n
        cost[s_node] = 0
        queue = [(0, s_node)]
        while queue:
            g_u, u = hq.heappop(queue)
            if not visited[u]:
                visited[u] = True
                for v, w in G[u]:
                    f = g_u + w
                    if f < cost[v]:
                        cost[v] = f
                        path[v] = u
                        hq.heappush(queue, (f, v))

                    if v == f_node and visited[u]:
                        return path
        return path

    def dijkstraPath(self, G, s_node, f_node):
        not_end = True
        path = self.dijkstra(G, len(G), s_node, f_node)
        _path = []
        while not_end:
            node = path[f_node]
            _path.append([node,f_node])
            if node == s_node: 
                break
        return path

obj= Interfaz(Tk())
obj.window.mainloop()