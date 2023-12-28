import json
import tkinter as tk
from tkinter import messagebox

from PIL import Image,ImageTk
import math
from geographiclib.geodesic import Geodesic
import paho.mqtt.client as mqtt


class ComputeCoords:
    def __init__(self):
        self.geod = Geodesic.WGS84
        self.mpp = 0.1122
        self.ppm = 1 / self.mpp
        # one point (x,y) in the canvas and the corresponding position (lat,lon)
        self.refCoord = [489, 553]
        self.refPosition = [41.2761183, 1.9887426]

    def convertToCoords(self, position):
        g = self.geod.Inverse(
            float(position[0]),
            float(position[1]),
            self.refPosition[0],
            self.refPosition[1],
        )
        azimuth = 180 - float(g["azi2"])
        dist = float(g["s12"])

        # ATENCION: NO SE POR QUE AQUI TENGO QUE RESTAR EN VEZ DE SUMAR
        x = self.refCoord[0] - math.trunc(
            dist * self.ppm * math.sin(math.radians(azimuth))
        )
        y = self.refCoord[1] - math.trunc(
            dist * self.ppm * math.cos(math.radians(azimuth))
        )
        return x, y

    def convertToPosition(self, coords):
        # compute distance with ref coords
        dist = (
            math.sqrt(
                (coords[0] - self.refCoord[0]) ** 2
                + (coords[1] - self.refCoord[1]) ** 2
            )
            * self.mpp
        )
        # compute azimuth
        # azimuth = math.degrees(math.atan2((self.previousx - e.x), (self.previousy - e.y))) * (-1)

        azimuth = math.degrees(
            math.atan2((self.refCoord[0] - coords[0]), (self.refCoord[1] - coords[1]))
        ) * (-1)
        if azimuth < 0:
            azimuth = azimuth + 360
        # compute lat,log of new wayp
        g = self.geod.Direct(
            float(self.refPosition[0]), float(self.refPosition[1]), azimuth, dist
        )
        lat = float(g["lat2"])
        lon = float(g["lon2"])
        return lat, lon






def callback(event):
    print ("clicked at", event.x, event.y)

def dibujar_rectangulo():
    # Coordenadas del rectángulo
    global canvas
    global conversor
    global pos1, pos2, pos3

    pos1 = None
    pos2 = None
    pos3 = None

    conversor = ComputeCoords()
    # Crear la ventana
    ventana = tk.Tk()
    ventana.title("Rectángulo Relleno")

    # Crear un lienzo (canvas)
    canvas = tk.Canvas(ventana, width=800, height=600)
    canvas.pack()
    canvas.bind("<Button-1>", callback)
    ''' imagen_fondo = tk.PhotoImage(file="dronlab.png")  # Reemplaza con la ruta de tu imagen
    canvas.create_image(0, 0, anchor=tk.NW, image=imagen_fondo)'''

    # Load an image in the script
    img = (Image.open("dronlab.png"))

    # Resize the Image using resize method
    resized_image = img.resize((800, 600), Image.ANTIALIAS)
    new_image = ImageTk.PhotoImage(resized_image)

    # Add image to the Canvas Items
    canvas.create_image(10, 10, anchor=tk.NW, image=new_image)

    '''# Cargar la imagen de fondo
    imagen_fondo = tk.PhotoImage(file="dronlab.png")  # Reemplaza con la ruta de tu imagen

    # Obtener las dimensiones del lienzo
    ancho_canvas = canvas.winfo_reqwidth()
    alto_canvas = canvas.winfo_reqheight()

    # Redimensionar la imagen al tamaño del canvas
    imagen_fondo = imagen_fondo.subsample(int(imagen_fondo.width() / ancho_canvas),
                                          int(imagen_fondo.height() / alto_canvas))

    # Crear una etiqueta para la imagen de fondo
    etiqueta_imagen_fondo = tk.Label(ventana, image=imagen_fondo)
    etiqueta_imagen_fondo.place(x=0, y=0, relwidth=1, relheight=1)  # Ajustar al tamaño del canvas'''

    # Dibujar el rectángulo relleno de color rojo semitransparente
    #canvas.create_rectangle(x1, y1, x2, y2, fill="#FF000080")
    x1, y1, x2,y2, x3,y3, x4, y4 = 139, 257, 418,181, 450, 267,167,345
    canvas.create_polygon(x1, y1, x2, y2, x3,y3,x4,y4,fill="red", stipple="gray12")
    x1, y1, x2, y2, x3, y3, x4, y4 = 418, 181, 681,109, 705, 199,450, 267
    canvas.create_polygon(x1, y1, x2, y2, x3, y3, x4, y4, fill="green", stipple="gray12")
    x1, y1, x2, y2, x3, y3, x4, y4 = 167,345,450, 267,468, 368, 198,444
    canvas.create_polygon(x1, y1, x2, y2, x3,y3,x4,y4,fill="yellow", stipple="gray12")
    x1, y1, x2, y2, x3, y3, x4, y4 = 450, 267, 705, 199,735,294,468, 368
    canvas.create_polygon(x1, y1, x2, y2, x3, y3, x4, y4, fill="blue", stipple="gray12")

    print('voy a conectarme al broker')
    client = mqtt.Client("DashboardAdolfo2", transport="websockets")
    client.on_message = on_message
    client.on_connect = on_connect
    client.username_pw_set("dronsEETAC", "mimara1456.")
    client.connect("classpip.upc.edu", 8000)
    print("Connected to classpip.upc.edu:8000")
    client.subscribe("+/dashBoardAdolfo2/#")
    client.publish("dashBoardAdolfo2/autopilotService/5762/connect")
    client.publish("dashBoardAdolfo2/autopilotService/5772/connect")
    client.publish("dashBoardAdolfo2/autopilotService/5782/connect")

    client.loop_start()
    # Iniciar el bucle principal de la aplicación
    ventana.mainloop()

def move (port, lat,lon):
    global canvas
    global pos1, pos2, pos3
    global conversor
    posX, posY = conversor.convertToCoords((lat, lon))
    if port == '5762':
        if pos1 == None:
            pos1 = canvas.create_oval(
                    posX - 15,
                    posY- 15,
                    posX + 15,
                    posY + 15,
                    fill="yellow",
                )
        else:
            canvas.coords(pos1,
                      posX - 15,
                      posY - 15,
                      posX + 15,
                      posY + 15,
                )
    if port == '5772':
        if pos2 == None:
            pos2 = canvas.create_oval(
                    posX - 15,
                    posY- 15,
                    posX + 15,
                    posY + 15,
                    fill="red",
                )
        else:
            canvas.coords(pos2,
                      posX - 15,
                      posY - 15,
                      posX + 15,
                      posY + 15,
                )
    if port == '5782':
        if pos3 == None:
            pos3 = canvas.create_oval(
                    posX - 15,
                    posY- 15,
                    posX + 15,
                    posY + 15,
                    fill="green",
                )
        else:
            canvas.coords(pos3,
                      posX - 15,
                      posY - 15,
                      posX + 15,
                      posY + 15,
                )

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connection OK")
    else:
        messagebox.showinfo("Bad connection")
        print("Bad connection")

def on_message(client, userdata, message):
    global myAutopilotController
    global myCameraController
    global panel
    global lbl
    global table
    global originlat, originlon
    global new_window

    print ('recibo ', message.topic)
    splited = message.topic.split("/")
    origin = splited[0]
    command = splited[2]


    if command == "telemetryInfo":
        port = splited[3]
        telemetry_info = json.loads(message.payload)
        lat = telemetry_info['lat']
        lon= telemetry_info['lon']
        move (port, lat,lon)



# Llamar a la función para dibujar el rectángulo
dibujar_rectangulo()


