import streamlit as st
from datetime import date

# ================= Sidebar =================
st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Menü",
    ["Geräteverwaltung", "Nutzerverwaltung", "Reservierungen"]
)

st.title(page)

#Anfangszustände
defaults = {
    "device_type": None,
    "selected_model": None,
    "reservation_date": None,
    "open_reservation_dialog": False,
    "open_edit_dialog": False,
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

ALL_HOURS = list(range(8, 19))      #Mögliche Stunden

#Geräte, Modelle, werden später aus TinyDB gelesen
if "device_models" not in st.session_state:
    st.session_state.device_models = {
        "3D-Drucker": {
            "Prusa MK4": 2,
            "Bambu X1": 1
        },
        "Laser-Cutter": {
            "Glowforge": 2,
            "Epilog Zing": 1
        },
        "Lötstationen": {
            "Weller WX2": 2,
            "JBC CD-2BQ": 1
        }
    }

st.session_state.users = {
    "max.mustermann@fh.at": {
        "name": "Max Mustermann",
        "email": "max.mustermann@fh.at",
        "study": "Mechatronics"
    }
}


#Test-Reservierungen, werden später aus TinyDB gelesen
if "reservations" not in st.session_state:
    st.session_state.reservations = {
    "Laser-Cutter": {
        "Glowforge": {
            "2025-12-20": [9, 10, 11, 12],
            "2025-12-22": [14, 15]
        }
    },
    "3D-Drucker": {
        "Prusa MK4": {
            "2025-12-21": [8, 9]
        }
    }
}

#Verwaltung Geräte, Auswahl
if page == "Geräteverwaltung":

    col1, col2, col3 = st.columns(3, gap="small")

    with col1:
        if st.button("3D-Drucker", use_container_width=True):
            st.session_state.device_type = "3D-Drucker"
            st.session_state.selected_model = None

    with col2:
        if st.button("Laser-Cutter", use_container_width=True):
            st.session_state.device_type = "Laser-Cutter"
            st.session_state.selected_model = None

    with col3:
        if st.button("Lötstationen", use_container_width=True):
            st.session_state.device_type = "Lötstationen"
            st.session_state.selected_model = None

    #Knopf um Geräte zu bearbeiten
    if st.session_state.device_type:
        st.divider()
        if st.button("🛠️ Geräte bearbeiten"):
            st.session_state.open_edit_dialog = True

    #Modelle auslesen, auflisten
    if st.session_state.device_type:
        device = st.session_state.device_type
        models = st.session_state.device_models[device]

        st.subheader(f"{device} – Modelle")

        cols = st.columns(len(models), gap="small")
        for col, model in zip(cols, models.keys()):
            with col:
                if st.button(model, use_container_width=True):
                    st.session_state.selected_model = model
                    st.session_state.reservation_date = None

#Kalender für Reservierung
if st.session_state.selected_model:

    device = st.session_state.device_type
    model = st.session_state.selected_model

    st.subheader(f"Reservierung – {model}")

    selected_date = st.date_input(
        "Datum auswählen",
        min_value=date.today()
    )

    date_str = selected_date.isoformat()

    reserved = (
        st.session_state.reservations
        .get(device, {})
        .get(model, {})
        .get(date_str, [])
    )

    free = [h for h in ALL_HOURS if h not in reserved]

    if not free:
        st.error("🔴 Vollständig ausgebucht")
    elif len(free) < len(ALL_HOURS):
        st.warning("🟡 Teilweise belegt")
    else:
        st.success("🟢 Komplett frei")

    if free:
        if st.button("Reservieren"):
            st.session_state.reservation_date = date_str
            st.session_state.open_reservation_dialog = True

#Formular für Reservierung öffnen
if st.session_state.open_reservation_dialog:

    @st.dialog("Neue Reservierung")
    def reservation_dialog():

        device = st.session_state.device_type
        model = st.session_state.selected_model
        date_str = st.session_state.reservation_date

        reserved = (
            st.session_state.reservations
            .get(device, {})
            .get(model, {})
            .get(date_str, [])
        )

        free = [h for h in ALL_HOURS if h not in reserved]

        start = st.selectbox("Startzeit", free)
        max_duration = len([h for h in free if h >= start])
        duration = st.slider("Dauer (Stunden)", 1, max_duration)

        block = list(range(start, start + duration))
        if not set(block).issubset(set(free)):
            st.error("❌ Zeitraum nicht verfügbar")
            return

        name = st.text_input("Name")        #Hier wird später ein Benutzer ausgewählt
        email = st.text_input("E-Mail")     #Für Reparatur - Benutzer "Service" wählen
        purpose = st.text_area("Zweck")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Reservieren"):
                if not all([name, email, purpose]):
                    st.warning("Bitte alle Felder ausfüllen")
                    return

                st.session_state.reservations \
                    .setdefault(device, {}) \
                    .setdefault(model, {}) \
                    .setdefault(date_str, []) \
                    .extend(block)

                st.session_state.open_reservation_dialog = False
                st.success("Reservierung gespeichert")
                st.rerun()

        with col2:
            if st.button("❌ Abbrechen"):
                st.session_state.open_reservation_dialog = False
                st.rerun()

    reservation_dialog()

#Fenster für Gerätebearbeitung
if st.session_state.open_edit_dialog:

    @st.dialog("🛠️ Geräte bearbeiten")
    def edit_dialog():

        device = st.session_state.device_type
        models = st.session_state.device_models[device]

        st.subheader(f"{device} – Modelle verwalten")

        st.markdown("### Neues Modell")
        new_name = st.text_input("Modellname")
        new_count = st.number_input("Anzahl", 1, 20, 1)

        if st.button("Hinzufügen"):
            models[new_name] = new_count
            st.success("Modell hinzugefügt")
            st.rerun()

        st.divider()
        st.markdown("### Bestehende Modelle")

        for model in list(models.keys()):
            c1, c2, c3 = st.columns([3, 1, 1])
            with c1:
                st.write(model)
            with c2:
                models[model] = st.number_input(
                    "Anzahl", 1, 20, models[model], key=f"cnt_{model}"
                )
            with c3:
                if st.button("🗑️", key=f"del_{model}"):
                    del models[model]
                    st.rerun()

        st.divider()
        if st.button("❌ Schließen"):
            st.session_state.open_edit_dialog = False
            st.rerun()

    edit_dialog()

#Seite der Nutzerverwaltung
elif page == "Nutzerverwaltung":

    st.header("Nutzerverwaltung")

    #Initialisierungen
    if "users" not in st.session_state:
        st.session_state.users = {}

    if "user_mode" not in st.session_state:
        st.session_state.user_mode = None

    if "selected_user" not in st.session_state:
        st.session_state.selected_user = None

    #Auswahl Modus, hinzufügen oder bearbeiten
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Nutzer hinzufügen", use_container_width=True):
            st.session_state.user_mode = "add"
            st.session_state.selected_user = None

    with col2:
        if st.button("Nutzer bearbeiten", use_container_width=True):
            st.session_state.user_mode = "edit"

    st.divider()

    #Nutzer hinzufügen
    if st.session_state.user_mode == "add":

        st.subheader("Neuer Nutzer")

        name = st.text_input("Name")
        email = st.text_input("E-Mail")
        study = st.text_input("Studiengang")

        col1, col2 = st.columns(2)

        #Daten werden später aus TinyDB ausgelesen, gespeichert

        with col1:
            if st.button("Speichern"):
                if not name or not email or not study:
                    st.warning("Bitte alle Felder ausfüllen")
                elif email in st.session_state.users:
                    st.error("Diese E-Mail existiert bereits")
                else:
                    st.session_state.users[email] = {
                        "name": name,
                        "email": email,
                        "study": study
                    }
                    st.success("Nutzer angelegt")
                    st.session_state.user_mode = None
                    st.rerun()

        with col2:
            if st.button("Abbrechen"):
                st.session_state.user_mode = None
                st.rerun()

    #Nutzer bearbeiten
    if st.session_state.user_mode == "edit":

        users = st.session_state.users

        if not users:
            st.info("Noch keine Nutzer vorhanden")

        user_email = st.selectbox(
            "Nutzer auswählen",
            options=list(users.keys()),
            format_func=lambda x: f"{users[x]['name']} ({x})"
        )

        user = users[user_email]

        st.subheader("Nutzer bearbeiten")

        name = st.text_input("Name", value=user["name"])
        study = st.text_input("Studiengang", value=user["study"])

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("Änderungen speichern"):
                users[user_email]["name"] = name
                users[user_email]["study"] = study
                st.success("Änderungen gespeichert")
                st.rerun()

        with col2:
            if st.button("Nutzer löschen"):
                del users[user_email]
                st.session_state.user_mode = None
                st.success("Nutzer gelöscht")
                st.rerun()

        with col3:
            if st.button("Abbrechen"):
                st.session_state.user_mode = None
                st.rerun()


elif page == "Reservierungen":
    st.write("Reservierungsübersicht")
