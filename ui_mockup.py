from devices_inheritance import Device
import streamlit as st
from datetime import date
from users_inheritance import User

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

if "last_page" not in st.session_state:             #Letzte Page immer speichern
    st.session_state.last_page = page

if st.session_state.last_page != page:              #Bei Seitenwechsel werden alle Zustände zurückgesetzt
    st.session_state.selected_model = None
    st.session_state.reservation_date = None
    st.session_state.open_reservation_dialog = False
    st.session_state.open_edit_dialog = False
    st.session_state.last_page = page

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

ALL_HOURS = list(range(8, 19))      #Mögliche Stunden

if "device_models" not in st.session_state:
    st.session_state.device_models = {}

    devices = Device.find_all()

    for dev in devices:
        dtype = dev.device_type or "Unbekannt"

        # Typ-Gruppe anlegen falls nicht vorhanden
        st.session_state.device_models.setdefault(dtype, {})

        # Gerät eintragen
        st.session_state.device_models[dtype][dev.device_name] = dev.count


if "users" not in st.session_state:
    st.session_state.users = {
        u.id: {"name": u.name, "email": u.id}
        for u in User.find_all()
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
            st.session_state.device_type = "Loetstationen"
            st.session_state.selected_model = None

    #Knopf um Geräte zu bearbeiten
    if st.session_state.device_type:
        st.divider()
        if st.button("🛠️ Geräte bearbeiten"):
            st.session_state.open_edit_dialog = True

    #Modelle auslesen, auflisten
    if st.session_state.device_type:
        device = st.session_state.device_type
        if device not in st.session_state.device_models:
            st.info("Für diesen Gerätetyp gibt es aktuell keine Geräte in der Datenbank.")
            st.stop()
        models = st.session_state.device_models[device]

        st.subheader(f"{device} - Modelle")

        cols = st.columns(len(models), gap="small")

        for col, (model, count) in zip(cols, models.items()):
            label = f"{model} (x{count})"

            with col:
                if st.button(label, use_container_width=True, key=f"btn_{model}"):
                    st.session_state.selected_model = model   #Nur Modellnamen speichern
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
    st.session_state.open_reservation_dialog = False

#Fenster für Gerätebearbeitung
if st.session_state.open_edit_dialog:

    @st.dialog("Geräte bearbeiten")
    def edit_dialog():

        device = st.session_state.device_type
        models = st.session_state.device_models[device]
        all_users = User.find_all()
        user_mapping = {u.id: u.name for u in all_users}   #Verantwortliche auslesen

        st.subheader(f"{device} – Modelle verwalten")

        st.markdown("### Neues Modell")
        new_name = st.text_input("Modellname")
        new_count = st.number_input("Anzahl", 1, 20, 1)

        # Verantwortlichen auswählen
        user_emails = list(st.session_state.users.keys())

        manager_email = st.selectbox(
            "Verantwortlicher Benutzer",
            options=user_emails,
            format_func=lambda x: f"{st.session_state.users[x]['name']} ({x})"
        )

        if st.button("Hinzufügen"):
            models[new_name] = new_count

            #In TinyDB speichern
            device = Device(
                device_name=new_name,
                managed_by_user_id=manager_email,
                count=new_count,
                device_type=st.session_state.device_type
            )
            device.store_data()

            st.success("Gerät gespeichert")
            st.rerun()

        st.divider()
        st.markdown("### Bestehende Modelle")

        for model in list(models.keys()):
            c1, c2, c3, c4 = st.columns([3, 2, 1, 1])

            with c1:
                st.write(model)

            #Verantwortlichen aus DB laden
            dev = Device.find_by_attribute("device_name", model)
            current_manager = dev.managed_by_user_id if dev else None

            with c2:
                # Drop-Down mit allen Usern
                new_manager = st.selectbox(
                    "Verantwortlicher",
                    options=list(user_mapping.keys()),
                    format_func=lambda x: f"{user_mapping[x]} ({x})",
                    index=list(user_mapping.keys()).index(current_manager)
                        if current_manager in user_mapping else 0,
                    key=f"mgr_{model}"
                )

                # Wenn geändert → DB speichern
                if dev and new_manager != current_manager:
                    dev.set_managed_by_user_id(new_manager)
                    dev.store_data()
                    st.success("Verantwortlicher aktualisiert")
                    st.rerun()

            with c3:
                new_val = st.number_input(
                    "Anzahl", 1, 20, models[model], key=f"cnt_{model}"
                )
                if new_val != models[model]:                                #Wenn neuer count-Wert angegeben wird - speichern
                    models[model] = new_val

                    dev = Device.find_by_attribute("device_name", model)
                    if dev:
                        dev.count = new_val
                        dev.store_data()

                    st.success("Anzahl aktualisiert")
                    st.rerun()

            with c4:
                if st.button("🗑️", key=f"del_{model}"):
                    if dev:
                        dev.delete()
                    del models[model]
                    st.success("Gerät gelöscht")
                    st.rerun()

        st.divider()
        if st.button("❌ Schließen"):
            st.session_state.open_edit_dialog = False
            st.rerun()

    edit_dialog()
    st.session_state.open_edit_dialog = False           #Dialog nur einmal aktiv lassen, so kann bleibt Dialog nicht geöffnet

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

        col1, col2 = st.columns(2)

        #Daten werden später aus TinyDB ausgelesen, gespeichert

        with col1:
            if st.button("Speichern"):
                if not name or not email:
                    st.warning("Bitte alle Felder ausfüllen")
                elif email in st.session_state.users:
                    st.error("Diese E-Mail existiert bereits")
                else:
                    # UI speichern
                    st.session_state.users[email] = {
                        "name": name,
                        "email": email
                    }

                    # DB speichern
                    user = User(email, name)
                    user.store_data()

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

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("Änderungen speichern"):
                # UI aktualisieren
                users[user_email]["name"] = name

                # DB aktualisieren
                u = User(user_email, name)
                u.store_data()

                st.success("Änderungen gespeichert")
                st.rerun()

        with col2:
            if st.button("Nutzer löschen"):
                User(user_email, user["name"]).delete()
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
