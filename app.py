import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from streamlit_plotly_events import plotly_events

# ---------- Physics helper ----------

def E_point_charge(q, xq, yq, X, Y):
    """
    Electric field of a point charge q at (xq, yq),
    evaluated on grid (X, Y), with k set to 1:
        E = q * r / |r|^3
    """
    dx = X - xq
    dy = Y - yq
    r2 = dx**2 + dy**2
    r = np.sqrt(r2)
    r3 = r2 * r

    # Avoid division by zero right at the charge
    r3 = np.where(r3 == 0, np.nan, r3)

    Ex = q * dx / r3
    Ey = q * dy / r3
    return Ex, Ey

# ---------- Streamlit app ----------

st.title("Interactive Dipole: Move Charges and See the Electric Field")

st.write(
    """
    - Use the radio buttons to choose which charge (**+q** or **−q**) you want to move.  
    - Click anywhere in the Plotly panel to place that charge at the clicked position.  
    - The electric field streamlines update automatically.
    """
)

# Initial positions stored in session_state
if "q_pos" not in st.session_state:
    st.session_state.q_pos = {
        "+": [-1.0, 0.0],  # +q starting at (-1, 0)
        "-": [ 1.0, 0.0],  # -q starting at ( 1, 0)
    }

charge_to_move = st.radio("Charge to move", ["+", "-"], horizontal=True)

# Current positions
x_plus, y_plus = st.session_state.q_pos["+"]
x_minus, y_minus = st.session_state.q_pos["-"]

# ---------- Plotly figure for clicking / moving charges ----------

fig_click = go.Figure()

fig_click.add_trace(
    go.Scatter(
        x=[x_plus, x_minus],
        y=[y_plus, y_minus],
        mode="markers+text",
        marker=dict(size=16, color=["red", "blue"]),
        text=["+q", "−q"],
        textposition="top center",
        name="charges",
    )
)

fig_click.update_layout(
    xaxis=dict(range=[-4, 4], zeroline=True),
    yaxis=dict(
        range=[-4, 4],
        zeroline=True,
        scaleanchor="x",  # keep aspect ratio 1:1
        scaleratio=1,
    ),
    title="Click to reposition the selected charge",
    margin=dict(l=40, r=20, t=40, b=40),
)

click_result = plotly_events(
    fig_click,
    click_event=True,
    hover_event=False,
    select_event=False,
    key="click_fig",
)

# If user clicked somewhere, update the chosen charge position
if click_result:
    event = click_result[0]
    x_new = event["x"]
    y_new = event["y"]
    st.session_state.q_pos[charge_to_move] = [x_new, y_new]
    x_plus, y_plus = st.session_state.q_pos["+"]
    x_minus, y_minus = st.session_state.q_pos["-"]

st.markdown("### Electric field from +q and −q")

# ---------- Compute electric field on a grid ----------

x = np.linspace(-4, 4, 41)
y = np.linspace(-4, 4, 41)
X, Y = np.meshgrid(x, y)

q = 1.0  # magnitude (k set to 1)

Ex_plus, Ey_plus = E_point_charge(q, x_plus, y_plus, X, Y)
Ex_minus, Ey_minus = E_point_charge(-q, x_minus, y_minus, X, Y)

Ex = Ex_plus + Ex_minus
Ey = Ey_plus + Ey_minus

# Mask near the charges for nicer plotting
mask1 = (X - x_plus)**2 + (Y - y_plus)**2 < 0.05
mask2 = (X - x_minus)**2 + (Y - y_minus)**2 < 0.05
mask = mask1 | mask2

Ex = np.ma.array(Ex, mask=mask)
Ey = np.ma.array(Ey, mask=mask)

# ---------- Matplotlib streamplot of the field ----------

fig, ax = plt.subplots(figsize=(6, 6))

E_mag = np.hypot(Ex, Ey)
color = np.log(E_mag)  # log scale for better contrast

ax.streamplot(
    X, Y, Ex, Ey,
    color=color,
    density=1.2,
    linewidth=1,
    arrowsize=1.2,
)

# Plot charges
ax.scatter([x_plus], [y_plus], color="red", s=80)
ax.scatter([x_minus], [y_minus], color="blue", s=80)

ax.set_aspect("equal")
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.set_title("Electric Field of Two Charges (k = 1)")

st.pyplot(fig)
