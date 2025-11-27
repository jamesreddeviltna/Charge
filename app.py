import streamlit as st
import plotly.graph_objects as go
import numpy as np

st.title("Drag the charge to see the electric field!")

# Initial position stored in session_state
if "charge_pos" not in st.session_state:
    st.session_state.charge_pos = [0.0, 0.0]

x0, y0 = st.session_state.charge_pos

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=[x0],
    y=[y0],
    mode="markers",
    marker=dict(size=20),
    name="Charge",
))

fig.update_layout(
    xaxis=dict(range=[-5, 5]),
    yaxis=dict(range=[-5, 5]),
    dragmode="pan",
    title="(Prototype) – use Plotly's edit tools to move the point"
)

st.plotly_chart(fig, use_container_width=True)

st.info(
    "In a proper implementation, you would use Plotly's editable features "
    "or a custom JS callback to detect the new coordinates after dragging."
)

# Once you get new (x, y), compute field:
# Ex: E ∝ r / |r|^3, etc.
