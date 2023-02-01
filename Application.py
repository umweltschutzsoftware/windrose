import streamlit as st
from windrose import WindroseAxes, plot_windrose
import numpy as np
import pandas as pd
import io
import os
import matplotlib.pyplot as plt

st.set_page_config(
        page_title="R&H Windrose",
)

st.write(
  '''# Windrose erstellen
Bei Upload einer *.akterm Datei wird die Häufigkeitsverteilung der Windgeschwindigkeit und Windrichtung als Windrose erzeugt und zum Download angeboten.
  ''')

uploadedfile = st.file_uploader(label="Akterm Wetterzeitreihe hochladen. ", type="akterm", accept_multiple_files=False)

if uploadedfile is not None:
  fname = os.path.splitext(uploadedfile.name)[0]

  # Find the number of rows to skip in the *.akterm file
  # We do not want to read the header information
  skiprows=-1
  line_no=1
  for line in uploadedfile:
    if "AK" in str(line[:2]):
      skiprows = line_no-1
      break
    line_no += 1

  if skiprows==-1:
    st.error("Die hochgeladene Datei ist keine gültige akterm.")

  df = pd.read_csv(uploadedfile, skiprows=skiprows, header=None, delim_whitespace=True)

  # Remove Missing values
  origlen=len(df)
  df = df[(df[7]< 9) & (df[8]<9)]
  validlen=len(df)

  st.write("Einträge in akterm: ", origlen)
  st.write("Einträge mit gültiger Windgeschwindigkeit und Windrichtung: ", validlen)

  # Set the windspeed in m/s
  df["speed"] = df.apply(lambda x:x[10]*0.51444 if x[8]==0 else x[10]/10, axis=1, result_type='expand')

  df["direction"] = df.apply(lambda x:x[10]*0.51444 if x[8]==0 else x[10]/10, axis=1, result_type='expand')
  #df["speed"] = df[10]/10
  #df["speed"] = df[df[8] == 0][10]*0.514444


  df["direction"] = df[9]

  binsrange = [1.4, 1.8, 2.3, 3.8, 5.4, 6.9, 8.4, 10]
  ax = WindroseAxes.from_ax(theta_labels=["O", "NO", "N", "NW", "W", "SW", "S", "SO"])
  ax.bar(df["direction"],df["speed"],normed=True,bins=binsrange, nsector=36, opening=0.9)

  # Find scale 
  df["bin"] = pd.cut(df["direction"], 36)
  smax = round((df.groupby(by="bin")["bin"].count()/len(df)).max()*100,-1)
  smin = smax / 5
  sstep = smin

  steps = np.arange(smin, smax+sstep, step=sstep)
  ax.set_yticks(steps)
  labels = ["{}%".format(i) for i in steps]
  ax.set_yticklabels(labels)

  ax.set_legend(bbox_to_anchor=(0.7, -0.1), title="Windgeschwindigkeit in m/s")
  plt.title("Windrose für die Ausbreitungsstatistik {}.".format(uploadedfile.name))

  img = io.BytesIO()
  plt.savefig(img, format='png')
  
  
  btn = st.download_button(
     label="Windrose herunterladen",
     data=img,
     file_name=fname + "-windrose",
     mime="image/png"
  )
  