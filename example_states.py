import streamlit as st
import time

# Initialize state
if "state" not in st.session_state:
    st.session_state["state"] = "state_start"
    st.session_state["drink"] = "None"
    st.session_state["inserted"] = 0

# Callback function to change state
# Callback function are triggered when the button is clicked
def go_to_state_start():
    st.session_state["inserted"] = 0
    st.session_state["state"] = "state_start"

def go_to_state_a():
    st.session_state["state"] = "state_pay"
    st.session_state["drink"] = "zero"

def go_to_state_b():
    st.session_state["state"] = "state_pay"
    st.session_state["drink"] = "extra"

def go_to_state_c():
    st.session_state["state"] = "state_pay"
    st.session_state["drink"] = "cocaine"

def insert_money():
    st.session_state["inserted"] += 0.1

def go_to_state_exit():
    st.session_state["state"] = "state_exit"

if st.session_state["state"] == "state_start":
    st.text("Select a drink!")   
    st.button("Zero", type="primary", on_click=go_to_state_a)
    st.button("Extra sugar", type="primary", on_click=go_to_state_b)
    st.button("With cocaine", type="primary", on_click=go_to_state_c)    

elif st.session_state["state"] == "state_pay":
    amount = 0
    if st.session_state["drink"] == "zero":
        amount = 2.5
    elif st.session_state["drink"] == "extra":
        amount = 362.32
    elif st.session_state["drink"] == "cocaine":
        amount = 1.6

    st.text(f"Pay the needed amount: {amount}€")
    st.text(f"Money inserted: {st.session_state['inserted']:.2f} €")

    st.button("Insert 10c coin", type="primary", on_click=insert_money)

    if st.session_state["inserted"] >= amount - 0.05:
        go_to_state_exit()
    


elif st.session_state["state"] == "state_exit":
    st.text(f"Hier deine Cola mit der Kurzbeschreibung {st.session_state["drink"]} (Weil der Programmierer keine Lust hatte)")
    time.sleep(3)
    st.button("Restart!", type="primary", on_click=go_to_state_start)
