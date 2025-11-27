import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly.figure_factory as ff
from streamlit_plotly_events import plotly_events

# ----------------- Physics helper -----------------

def E_point_charge(q, xq, yq, X, Y):
    """
    Electric field of a point charge q at (xq, yq),
    evaluated on grid (X, Y), with k set to 1:

        E = q * r / |r|^3

    Returns Ex, Ey on the grid.
    """
    dx = X - xq
    dy = Y - yq
    r2 = dx**2 + dy**2
    r = np.sqrt(r2)

    # Avoid division by zero near the charge
    r3 = r2 * r
    r3 = np.where(r3 == 0, np.nan, r3)

    Ex = q * dx / r3
    Ey = q * dy / r3
    return Ex, Ey

# ----------------- Streamlit app -----------------

st.title("Interactive Electric Dipole with Movable Charges")

st.write(
    """
    **Instructions**  
    1. Choose which charge you want to move (**+q** or **−q**) below.  
    2. Click anywhere in the Plotly plot to place that charge there.  
    3. The electric field vector field (quiver) will update immediately.
    """
)

# Initial positions in session_state
if "q_pos" not in st.session_state:
    st.session_state.q_pos = {
        "+": [-1.0, 0.0],  # +q at (-1, 0)
        "-": [ 1.0, 0.0],  # -q at ( 1, 0)
    }

charge_to_move = st.radio("Charge to move", ["+", "-"], horizontal=True)

# Current positions of charges
x_plus, y_plus = st.session_state.q_pos["+"]
x_minus, y_minus = st.session_state.q_pos["-"]

# Grid for field vectors
x = np.linspace(-4, 4, 21)
y = np.linspace(-4, 4, 21)
X, Y = np.meshgrid(x, y)

q = 1.0  # magnitude of charges (k set to 1)

# Compute electric field from both charges
Ex_plus, Ey_plus = E_point_charge(q, x_plus, y_plus, X, Y)
Ex_minus, Ey_minus = E_point_charge(-q, x_minus, y_minus, X, Y)

Ex = Ex_plus + Ex_minus
Ey = Ey_plus + Ey_minus

# Mask near charges to avoid huge arrows
mask1 = (X - x_plus)**2 + (Y - y_plus)**2 < 0.05
mask2 = (X - x_minus)**2 + (Y - y_minus)**2 < 0.05
mask = mask1 | mask2
Ex_masked = np.ma.array(Ex, mask=mask)
Ey_masked = np.ma.array(Ey, mask=mask)

# Normalize arrows for plotting
E_mag = np.hypot(Ex_masked, Ey_masked)
E_mag_max = np.nanmax(E_mag)
if E_mag_max == 0 or np.isnan(E_mag_max):
    E_mag_max = 1.0

Ux = Ex_masked / E_mag_max
Uy = Ey_masked / E_mag_max

# Flatten for quiver
Xf = X.flatten()
Yf = Y.flatten()
Uxf = Ux.filled(0).flatten()
Uyf = Uy.filled(0).flatten()

# Create Plotly quiver figure
fig = ff.create_quiver(
    Xf, Yf, Uxf, Uyf,
    scale=0.4,  # adjust arrow length
    arrow_scale=0.4,
    name="E field"
)

# Add charges as scatter markers
fig.add_trace(
    go.Scatter(
        x=[x_plus, x_minus],
        y=[y_plus, y_minus],
        mode="markers+text",
        marker=dict(size=18, color=["red", "blue"]),
        text=["+q", "−q"],
        textposition="top center",
        name="charges",
    )
)

fig.update_layout(
    xaxis=dict(range=[-4, 4], zeroline=True),
    yaxis=dict(
        range=[-4, 4],
        zeroline=True,
        scaleanchor="x",
        scaleratio=1,
    ),
    title="Click to move the selected charge; arrows show the electric field",
    margin=dict(l=40, r=40, t=50, b=40),
)

# Use plotly_events to capture click position
click_result = plotly_events(
    fig,
    click_event=True,
    hover_event=False,
    select_event=False,
    key="field_fig",
)

# Update charge position if user clicked
if click_result:
    event = click_result[0]
    x_new = event["x"]
    y_new = event["y"]
    st.session_state.q_pos[charge_to_move] = [x_new, y_new]

    # Trigger re-run so positions & field update
    st.experimental_rerun()
