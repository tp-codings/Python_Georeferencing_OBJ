import tkinter as tk
from math import *
from tkinter import filedialog
import numpy as np


def dotproduct(v1, v2):
  return sum((a*b) for a, b in zip(v1, v2))

def determinant(v1, v2):
  return v1[0]*v2[1] - v1[1]*v2[0] 

def length(v):
  return sqrt(dotproduct(v, v))

def angle(v1, v2):
  return acos(dotproduct(v1, v2) / (length(v1) * length(v2)))*360/(2*pi)

def angle360(v1, v2):
   dot = dotproduct(v1, v2)
   det = determinant(v1, v2)
   return atan2(det, dot)*360/(2*pi)

def read_points():
    #noch ungültige Eingaben abfangen!!
    valueMissing = False
    global entry_A, entry_B, entry_A_prime, entry_B_prime

    try:
        A = [float(entry_A.get()), float(entry_A_y.get()), float(entry_A_z.get())]
        B = [float(entry_B.get()), float(entry_B_y.get()), float(entry_B_z.get())]
        A_prime = [float(entry_A_prime.get()), float(entry_A_prime_y.get()), float(entry_A_prime_z.get())]
        B_prime = [float(entry_B_prime.get()), float(entry_B_prime_y.get()), float(entry_B_prime_z.get())]
    except:
        valueMissing = True
    
    if not valueMissing:
        #2D Vektoren
        translation_xy = [A_prime[i]-A[i] for i in range(2)]

        A_to_B = [B[i]-A[i] for i in range(2)]

        A_prime_to_B_prime = [B_prime[i]-A_prime[i] for i in range(2)]

        translation_z = [0, 0, A_prime[2] - A[2]]

        #kleinster Winkel in Richtung AA' bis Vektor (VZ von Vektor aus betrachtet)
        alpha = angle360(A_to_B, translation_xy)              
        beta = angle360(A_prime_to_B_prime, translation_xy)

        total_rotation = 0

        if alpha <= 0 and beta >= 0:
            total_rotation = -(abs(alpha)+beta)
        elif alpha <= 0 and beta <= 0:
            total_rotation = -(abs(alpha)-abs(beta))
        elif alpha >= 0 and beta >= 0:
            total_rotation = alpha - beta
        elif alpha >= 0 and beta <= 0:
            total_rotation = alpha + abs(beta)
        else:
            print("Bug...")


        print("Translation XY:", translation_xy)
        print("Translation Z:", translation_z)

        print("AB:", A_to_B)
        print("A'B':", A_prime_to_B_prime)

        print("aplha:", alpha)
        print("beta:", beta)
        print("Gesamtrotation: ", total_rotation)

        print("Punkt A:", A)
        print("Punkt B:", B)
        print("Punkt A':", A_prime)
        print("Punkt B':", B_prime)
        transformObject(translation_xy, translation_z, total_rotation, A_prime)
    else:
       print("Wert fehlt")

def transformObject(translation_xy, translation_z, total_rotation, A_prime):
    directoryFalse = False
    wrongDataType = False

    obj_file_path = ''
    output_file_path = ''
    print(translation_xy, translation_z, total_rotation)

    expectedEnding = ".obj"

    #Zu transformierendes Mesh auswählen und Datei anlegen, wo transformiertes Mesh gespeichert werden soll
    obj_file_path = filedialog.askopenfilename(title="Wähle OBJ-Datei")

    if expectedEnding not in obj_file_path:
        wrongDataType = True

    if obj_file_path != '' and not wrongDataType:
        output_file_path = filedialog.asksaveasfilename(title="Wähle Ausgabedatei", defaultextension=".obj")

        if expectedEnding not in output_file_path and output_file_path != '':
            wrongDataType = True

    if obj_file_path == '' or output_file_path == '':
        directoryFalse = True

    if directoryFalse:
        result_label.config(text=f"Überprüfe Verzeichnis")
    if wrongDataType:
        result_label.config(text=f"Falscher Datentyp, bitte wähle OBJ aus")

    if not directoryFalse and not wrongDataType:
        with open(obj_file_path, 'r') as file:
            lines = file.readlines()

        transformedLines = []

        test = 0

        for line in lines:
            if line.startswith('v '):
                coordinates = line.strip().split()[1:]
                x, y, z = map(float, coordinates)
                
                #Translation aller Punkte um gegebenen Vektor
                x += translation_xy[0]
                y += translation_xy[1]

                P = np.array([x, y, 1])

                origin_back_matrix = np.array([[1, 0, A_prime[0]],
                                         [0, 1, A_prime[1]],
                                         [0, 0, 1]])
                
                origin_matrix = np.array([[1, 0, -(A_prime[0])],
                                               [0, 1, -(A_prime[1])],
                                               [0, 0, 1]])
                
                rotation_matrix = np.array([[cos(radians(total_rotation)), -sin(radians(total_rotation)), 0],
                                            [sin(radians(total_rotation)),  cos(radians(total_rotation)), 0],
                                            [0,                             0,                            1]])
                
                #P' = origin_matrix * rotation_matrix * origin_back_matrix * P

                P_prime = np.matmul(origin_back_matrix, rotation_matrix)
                P_prime = np.matmul(P_prime, origin_matrix)
                P_prime = np.matmul(P_prime, P)

                x = P_prime[0]
                y = P_prime[1]

                z += translation_z[2]

                test = P_prime

                shifted_line = f"v {x} {y} {z}\n"
                transformedLines.append(shifted_line)

            else:
                transformedLines.append(line)

        print(test)
        with open(output_file_path, 'w') as file:
            file.writelines(transformedLines)

        result_label.config(text=f"Mesh wurde um Vektor {translation_xy} verschoben,\num {translation_z[2]} m angehoben,\num {total_rotation}° gedreht\nund unter {output_file_path} gespeichert\n\n")

    else:
        result_label.config(text=f"Bitte Eingabe überprüfen")


# Erstelle das Hauptfenster
window = tk.Tk()
window.title("Punkte einlesen")

# Zentriere das Fenster auf dem Bildschirm
window_width = 800
window_height = 300
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
x = int((screen_width / 2) - (window_width / 2))
y = int((screen_height / 2) - (window_height / 2))
window.geometry(f"{window_width}x{window_height}+{x}+{y}")

# Setze eine minimale Breite für das Fenster
window.minsize(400, window_height)

# Erstelle die Eingabefelder für die Punkte
label_A = tk.Label(window, text="Punkt A:")
label_A.grid(row=0, column=0, sticky="e")
entry_A = tk.Entry(window)
entry_A.grid(row=0, column=1)

label_A_y = tk.Label(window, text="y-Koordinate:")
label_A_y.grid(row=0, column=2, sticky="e")
entry_A_y = tk.Entry(window)
entry_A_y.grid(row=0, column=3)

label_A_z = tk.Label(window, text="z-Koordinate:")
label_A_z.grid(row=0, column=4, sticky="e")
entry_A_z = tk.Entry(window)
entry_A_z.grid(row=0, column=5)

label_B = tk.Label(window, text="Punkt B:")
label_B.grid(row=1, column=0, sticky="e")
entry_B = tk.Entry(window)
entry_B.grid(row=1, column=1)

label_B_y = tk.Label(window, text="y-Koordinate:")
label_B_y.grid(row=1, column=2, sticky="e")
entry_B_y = tk.Entry(window)
entry_B_y.grid(row=1, column=3)

label_B_z = tk.Label(window, text="z-Koordinate:")
label_B_z.grid(row=1, column=4, sticky="e")
entry_B_z = tk.Entry(window)
entry_B_z.grid(row=1, column=5)

label_A_prime = tk.Label(window, text="Punkt A':")
label_A_prime.grid(row=3, column=0, sticky="e")
entry_A_prime = tk.Entry(window)
entry_A_prime.grid(row=3, column=1)

label_A_prime_y = tk.Label(window, text="y-Koordinate:")
label_A_prime_y.grid(row=3, column=2, sticky="e")
entry_A_prime_y = tk.Entry(window)
entry_A_prime_y.grid(row=3, column=3)

label_A_prime_z = tk.Label(window, text="z-Koordinate:")
label_A_prime_z.grid(row=3, column=4, sticky="e")
entry_A_prime_z = tk.Entry(window)
entry_A_prime_z.grid(row=3, column=5)

label_B_prime = tk.Label(window, text="Punkt B':")
label_B_prime.grid(row=4, column=0, sticky="e")
entry_B_prime = tk.Entry(window)
entry_B_prime.grid(row=4, column=1)

label_B_prime_y = tk.Label(window, text="y-Koordinate:")
label_B_prime_y.grid(row=4, column=2, sticky="e")
entry_B_prime_y = tk.Entry(window)
entry_B_prime_y.grid(row=4, column=3)

label_B_prime_z = tk.Label(window, text="z-Koordinate:")
label_B_prime_z.grid(row=4, column=4, sticky="e")
entry_B_prime_z = tk.Entry(window)
entry_B_prime_z.grid(row=4, column=5)

# Erstelle den Button zum Einlesen der Punkte
button = tk.Button(window, text="Punkte einlesen", command=read_points)
button.grid(row=6, column=3)

result_label = tk.Label(window, text="")
result_label.grid(row=7, column = 1)

# Starte die Hauptloop des Fensters
window.mainloop()
