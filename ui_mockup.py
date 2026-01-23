from devices_inheritance import Device
import streamlit as st
from datetime import date
from users_inheritance import User
from reservation_service import ReservationService
from datetime import datetime, timedelta


# ================= Sidebar =================
st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Menü",
    ["Geräteverwaltung", "Nutzerverwaltung", "Reservierungen", "Wartungen"]
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
        st.session_state.device_models.setdefault(dtype, {})
        # Speichere das ganze Objekt dev statt nur dev.count
        st.session_state.device_models[dtype][dev.device_name] = dev


if "users" not in st.session_state:
    st.session_state.users = {
        u.id: {"name": u.name, "email": u.id}
        for u in User.find_all()
    }


if "reservation_service" not in st.session_state:
    st.session_state.reservation_service = ReservationService()


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

        for col, (model_name, dev_obj) in zip(cols, models.items()):
            label = f"{model_name} (x{dev_obj.count})"

            with col:
                if st.button(label, use_container_width=True, key=f"btn_{model_name}"):
                    # Speichere die ID für die Logik und den Namen für die Anzeige
                    st.session_state.selected_model = dev_obj.id  
                    st.session_state.selected_model_name = model_name
                    st.session_state.reservation_date = None

#Kalender für Reservierung
if st.session_state.selected_model:

    device = st.session_state.device_type
    model = st.session_state.selected_model

    st.subheader(f"Reservierung – {st.session_state.selected_model_name}")

    selected_date = st.date_input(
        "Datum auswählen",
        min_value=date.today()
    )

    date_str = selected_date.isoformat()

    service = st.session_state.reservation_service

    # Alle Reservierungen für dieses Gerät
    device_res = service.find_all_reservations_by_device_id(model)

    reserved = []
    for r in device_res:
        if r.start_date.date().isoformat() == date_str:
            # Stunden blockieren
            start_h = r.start_date.hour
            end_h = r.end_date.hour
            reserved.extend(list(range(start_h, end_h)))


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
        service = st.session_state.reservation_service
        
        # WICHTIG: Hier brauchen wir die ID für die Datenbank-Abfragen
        model_id = st.session_state.selected_model 
        # Und den Namen nur für die Anzeige im Text
        model_name = st.session_state.selected_model_name
        
        date_str = st.session_state.reservation_date

        # Hier muss die model_id (UUID) rein!
        device_res = service.find_all_reservations_by_device_id(model_id)

        reserved = []
        for r in device_res:
            # (Dein bestehender Code zur Zeitberechnung...)
            start_dt = r.start_date
            end_dt = r.end_date
            if isinstance(start_dt, str): start_dt = datetime.fromisoformat(start_dt)
            if isinstance(end_dt, str): end_dt = datetime.fromisoformat(end_dt)

            if start_dt.date().isoformat() == date_str:
                reserved.extend(list(range(start_dt.hour, end_dt.hour)))

        free = [h for h in ALL_HOURS if h not in reserved]

        st.write(f"Modell: **{model_name}**") # Anzeige des Namens
        start = st.selectbox("Startzeit", free)
        max_duration = len([h for h in free if h >= start])
        duration = st.slider("Dauer (Stunden)", 1, max_duration)

        # ... (Nutzer-Auswahl Code) ...
        users = st.session_state.users
        user_labels = [f'{u["name"]} ({u["email"]})' for u in users.values()]
        label_to_id = {f'{u["name"]} ({u["email"]})': uid for uid, u in users.items()}
        selected_label = st.selectbox("Benutzer auswählen", user_labels)
        selected_user_id = label_to_id[selected_label]
        purpose = st.text_area("Zweck")
        
        if selected_user_id != "service@mci.edu":
            costs = 0
        else:
            costs = st.number_input("Kosten Service", value=None, placeholder="Gib eine Nummer ein")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Reservieren"):
                if not purpose:
                    st.warning("Bitte Zweck angeben")
                    return

                start_dt = datetime.fromisoformat(date_str) + timedelta(hours=start)
                end_dt = start_dt + timedelta(hours=duration)

                try:
                    # WICHTIG: Hier muss device_id=model_id (die UUID) übergeben werden!
                    service.create_reservation(                
                        user_id=selected_user_id,
                        device_id=model_id, 
                        start_date=start_dt,
                        end_date=end_dt,
                        purpose=purpose,
                        costs=costs
                    )
                    st.success("Reservierung gespeichert")
                    st.session_state.open_reservation_dialog = False
                    st.rerun()
                except ValueError as e:
                    st.error(f"Fehler: {str(e)}")

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
    st.header("📋 Aktuelle Reservierungen")
    
    service = st.session_state.reservation_service
    reservations = service.find_all_reservations()

    if not reservations:
        st.info("Es liegen aktuell keine Reservierungen vor.")
    else:
        # Tabellen-Header definieren
        # Spaltenbreiten: Name(2), Email(2), Zeitraum(3), Zweck(2), Aktion(1)
        h1, h2, h3, h4, h5 = st.columns([2, 2, 3, 2, 1])
        h1.write("**Gerät**")
        h2.write("**Benutzer**")
        h3.write("**Zeitraum**")
        h4.write("**Zweck**")
        h5.write("**Aktion**")
        st.divider()

        for r in reservations:
            # Gerätenamen anhand der ID finden
            device = Device.find_by_attribute("id", r.device_id)
            device_name = device.device_name if device else "Unbekanntes Gerät"
            
            # Zeitraum formatieren (z.B. 12.05. 14:00 - 16:00)
            zeitraum = f"{r.start_date.strftime('%d.%m. %H:%M')} - {r.end_date.strftime('%H:%M')}"
            
            # Zeile in Spalten aufteilen
            c1, c2, c3, c4, c5 = st.columns([2, 2, 3, 2, 1])
            
            with c1:
                st.write(device_name)
            with c2:
                st.write(r.user_id)
            with c3:
                st.write(zeitraum)
            with c4:
                # Zweck anzeigen (Feld haben wir im letzten Schritt hinzugefügt)
                st.write(getattr(r, 'purpose', '-')) 
            with c5:
                # Löschen-Knopf
                if st.button("🗑️", key=f"del_res_{r.id}"):
                    r.delete() # Löscht aus TinyDB
                    st.success("Reservierung gelöscht!")
                    st.rerun() # Seite neu laden, um Liste zu aktualisieren
            
            st.divider()

elif page == "Wartungen":

    
    service = st.session_state.reservation_service
    reservations = service.find_all_reservations_by_user_id("service@mci.edu")

    if not reservations:
        st.info("Es liegen aktuell keine Wartungen vor.")
    else:
        # Tabellen-Header definieren
        h1, h2, h3, h4, h5, h6 = st.columns([2, 2, 3, 2, 2, 1])
        h1.write("**Gerät**")
        h2.write("**Benutzer**")
        h3.write("**Zeitraum**")
        h4.write("**Wartung**")
        h5.write("**Kosten**")
        h6.write("**Aktion**")
        st.divider()

        for r in reservations:
            # Gerätenamen anhand der ID finden
            device = Device.find_by_attribute("id", r.device_id)
            device_name = device.device_name if device else "Unbekanntes Gerät"
            
            # Zeitraum formatieren (z.B. 12.05. 14:00 - 16:00)
            zeitraum = f"{r.start_date.strftime('%d.%m. %H:%M')} - {r.end_date.strftime('%H:%M')}"

            costs = f"{r.costs} €"

            # Zeile in Spalten aufteilen
            c1, c2, c3, c4, c5, c6 = st.columns([2, 2, 3, 2, 2, 1])
            
            with c1:
                st.write(device_name)
            with c2:
                st.write(r.user_id)
            with c3:
                st.write(zeitraum)
            with c4:
                # Zweck anzeigen (Feld haben wir im letzten Schritt hinzugefügt)
                st.write(getattr(r, 'purpose', '-')) 
            with c5:
                st.write(costs)
            with c6:
                # Löschen-Knopf
                if st.button("🗑️", key=f"del_res_{r.id}"):
                    r.delete() # Löscht aus TinyDB
                    st.success("Wartung gelöscht!")
                    st.rerun() # Seite neu laden, um Liste zu aktualisieren
            
            st.divider()

        
