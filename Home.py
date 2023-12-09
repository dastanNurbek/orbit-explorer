import streamlit as st
import pyvista as pv
import numpy as np
from stpyvista import stpyvista
from pyvista import examples
from skyfield.api import load, EarthSatellite
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

pyvista.start_xvfb()
st.set_page_config(page_title="OrbitExplorer", page_icon="🌎")

"# Визуализация Орбиты Спутника"

st.sidebar.success("Select a demo above.")

st.divider()

r = st.number_input("Радиус орбиты (км)",min_value=300,max_value=35793)
inclination = st.slider("Наклонение орбиты (°)", -90.0000, 90.0000, step=0.0005)
lan = st.slider("Долгота восходящего узла (°)", 0.0000, 360.0000, step=0.0005)
aop = st.slider("Аргумент перигея (°)", 0.0000, 180.0000, step=0.0005)
ma = st.slider("Средняя аномалия (°)", 0.0000, 360.0000, step=0.0005)
mm = st.slider("Частота обращения", 1.00000000, 17.00000000, step=0.00000005)

ts = load.timescale(builtin=True)

TLE = f"""ISS (ZARYA)             
1 25544U 23067A   23203.81086311  .00000606  00000-0  -11606-4 0  9996
2 25544  {inclination} {lan} 0006740 {aop} {ma} {mm}180787"""

if st.button("Смоделировать"):

    # Creating Earth model
    earth_r = 6371
    axes = pv.Axes(show_actor=True, actor_scale=0.2, line_width=5)
    axes.origin = (0.0, 0.0, 0.0)
    earth = pv.Sphere(
        radius=1, theta_resolution=120, phi_resolution=120, start_theta=270.001, end_theta=270
    )
    earth.active_t_coords = np.zeros((earth.points.shape[0], 2))
    for i in range(earth.points.shape[0]):
        earth.active_t_coords[i] = [
            0.5 + np.arctan2(-earth.points[i, 0], earth.points[i, 1]) / (2 * np.pi),
            0.5 + np.arcsin(earth.points[i, 2]) / np.pi,
        ]
    tex = examples.load_globe_texture()
    orbit = pv.Tube(pointa=(0.0, 0.0, -0.008), pointb=(0.0, 0.0, 0.008), resolution=1, radius=(r+earth_r)/earth_r, n_sides=100)
    new_orbit = orbit.rotate_y(inclination, point=axes.origin, inplace=False)

    ## Set up plotter
    plotter = pv.Plotter(window_size=[600,600])
    plotter.add_actor(axes.actor)
    plotter.add_mesh(earth, texture=tex)
    #plotter.add_mesh(orbit, color="red")
    plotter.add_mesh(new_orbit, color="red")

    # Adjust the camera position to zoom out
    plotter.camera_position = [(3, 3, 3), (0, 0, 0), (0, 0, 1)]

    ## Pass the plotter (not the mesh) to stpyvista
    stpyvista(plotter)

    ## Plotting ground track
    name, L1, L2 = TLE.splitlines()

    sat = EarthSatellite(L1, L2)

    minutes = np.arange(0, 5000, 0.1) # about two orbits
    times   = ts.utc(2023, 9, 12, 0, minutes)

    geocentric = sat.at(times)
    subsat = geocentric.subpoint()

    fig = plt.figure(figsize=(20, 10))
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

    ax.stock_img()

    plt.scatter(subsat.longitude.degrees, subsat.latitude.degrees, transform=ccrs.PlateCarree(),
                color='red')
    st.pyplot(fig=fig)
