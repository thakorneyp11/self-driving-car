import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

from simulations.car_simulation import CarSimulator
from controllers.pid_controller import PID


# Config Streamlit page
st.set_page_config(layout="wide")

# Initialize car and PID controller
simulation = CarSimulator()
pid = PID(Kp=0.2, Ki=0, Kd=0)  # Initial PID values, adjust as necessary

# Config time samples for PID controller
max_steps = 500
time_sample = 0.1
timesteps = np.linspace(0, max_steps*time_sample, max_steps)
pid.set_sample_time(time_sample)

st.title("PID Controller: Car Lane Changing")

config_column1, config_column2 = st.columns(2)

with config_column1:
    # Config PID value from UI sliders
    kp = st.slider('Kp', 0.0, 2.0, 0.2)
    ki = st.slider('Ki', 0.0, 2.0, 0.0)
    kd = st.slider('Kd', 0.0, 2.0, 0.2)
    pid.Kp = kp
    pid.Ki = ki
    pid.Kd = kd

with config_column2:
    # Config target value from UI slider
    initial_value = st.slider('Initial Y-Position', 0, 200, 0)
    setpoint = st.slider('Setpoint Y-Position', 0, 200, 100)
    pid.set_target(int(setpoint))

# Run simulation to receive trajectory
trajectory: list = simulation.simulate_session(controller=pid, 
                                                initial_position=[0, initial_value], 
                                                max_steps=max_steps,
                                                time_sample=time_sample)

x_positions = [x for x, y in trajectory]
y_positions = [y for x, y in trajectory]

column1, column2, column3 = st.columns(3)

with column1:
    # Plot for Y-axis position over time
    st.subheader("Car Trajectory over Y-axis Perspective")
    fig, ax = plt.subplots()
    ax.plot(timesteps, y_positions, label='Car Trajectory (Y-axis)')
    ax.axhline(y=setpoint, color='r', linestyle='--', label='Setpoint')
    ax.set_xlabel('Time')
    ax.set_ylabel('Y-axis Position')
    ax.legend()
    st.pyplot(fig)

with column2:
    # Plot for X-axis position over time
    st.subheader("Car Trajectory over X-axis Perspective")
    fig_x, ax_x = plt.subplots()
    ax_x.plot(timesteps, x_positions, label='Car Trajectory (X-axis)', color='b')
    ax_x.set_xlabel('Time')
    ax_x.set_ylabel('X-axis Position')
    ax_x.legend()
    st.pyplot(fig_x)
    
with column3:
    # Plot for X-Y coordinates trajectory
    st.subheader("Car Trajectory: Bird's Eye View")
    fig_xy, ax_xy = plt.subplots()
    ax_xy.plot(x_positions, y_positions, label='Car X-Y Trajectory', color='g')
    ax_xy.axhline(y=setpoint, color='r', linestyle='--', label='Setpoint')
    ax_xy.set_xlabel('X Position')
    ax_xy.set_ylabel('Y Position')
    ax_xy.legend()
    st.pyplot(fig_xy)
