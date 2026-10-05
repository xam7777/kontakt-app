import sqlite3
import tkinter as tk

FARBE_HINTERGRUND = "#12121f"
FARBE_FELD = "#1e1e32"
FARBE_AKZENT = "#6c5ce7"
FARBE_AKZENT_HOVER = "#5a4bd6"
FARBE_TEXT = "#f0f0f5"
FARBE_TEXT_GEDAEMPFT = "#8a8aa3"
FARBE_LOESCHEN = "#e74c3c"

bearbeite_id = None  # Merkt sich: bearbeiten wir gerade einen Kontakt, und welchen? None = nein, neuer Kontakt


def erstelle_datenbank():
    verbindung = sqlite3.connect("kontakte.db")
    cursor = verbindung.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS kontakte (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            telefon TEXT,
            email TEXT
        )
    """)
    verbindung.commit()
    verbindung.close()


def hole_alle_kontakte():
    verbindung = sqlite3.connect("kontakte.db")
    cursor = verbindung.cursor()
    cursor.execute("SELECT id, name, telefon, email FROM kontakte ORDER BY name")
    ergebnisse = cursor.fetchall()
    verbindung.close()
    return ergebnisse


def liste_neu_zeichnen():
    liste.delete(0, tk.END)
    for kontakt in hole_alle_kontakte():
        _id, name, telefon, email = kontakt
        zusatz = telefon if telefon else email
        text = f"  {name}" + (f"   ·   {zusatz}" if zusatz else "")
        liste.insert(tk.END, text)


def felder_leeren():
    eingabe_name.delete(0, tk.END)
    eingabe_telefon.delete(0, tk.END)
    eingabe_email.delete(0, tk.END)
    for feld, platzhalter in [(eingabe_name, "Name"), (eingabe_telefon, "Telefon"), (eingabe_email, "Email")]:
        feld.insert(0, platzhalter)  # Platzhaltertext wieder einsetzen
        feld.config(fg=FARBE_TEXT_GEDAEMPFT)


def modus_zuruecksetzen():
    """Verlässt den Bearbeiten-Modus und geht zurück zu 'neuer Kontakt'."""
    global bearbeite_id
    bearbeite_id = None  # Kein Kontakt mehr in Bearbeitung
    button_speichern.config(text="＋  Kontakt speichern", bg=FARBE_AKZENT)  # Button-Text/Farbe zurücksetzen
    button_abbrechen.pack_forget()  # Versteckt den "Abbrechen"-Button wieder
    felder_leeren()


def kontakt_speichern():
    global bearbeite_id
    name = eingabe_name.get().strip()
    telefon = eingabe_telefon.get().strip()
    email = eingabe_email.get().strip()

    # Platzhaltertexte zählen als "leer", nicht als echter Wert
    if name in ("", "Name"):
        status_label.config(text="⚠  Bitte einen Namen eingeben", fg="#e74c3c")
        return
    if telefon == "Telefon":
        telefon = ""
    if email == "Email":
        email = ""

    verbindung = sqlite3.connect("kontakte.db")
    cursor = verbindung.cursor()

    if bearbeite_id is None:
        # Kein Kontakt in Bearbeitung -> neuen Kontakt anlegen
        cursor.execute(
            "INSERT INTO kontakte (name, telefon, email) VALUES (?, ?, ?)",
            (name, telefon, email)
        )
        status_label.config(text=f"✓  '{name}' gespeichert", fg="#2ecc71")
    else:
        # Ein Kontakt wird gerade bearbeitet -> bestehenden Eintrag aktualisieren
        cursor.execute(
            "UPDATE kontakte SET name = ?, telefon = ?, email = ? WHERE id = ?",
            (name, telefon, email, bearbeite_id)
        )
        status_label.config(text=f"✓  '{name}' aktualisiert", fg="#2ecc71")

    verbindung.commit()
    verbindung.close()

    modus_zuruecksetzen()
    liste_neu_zeichnen()
    eingabe_name.focus()


def kontakt_bearbeiten():
    """Lädt den ausgewählten Kontakt in die Eingabefelder, um ihn zu ändern."""
    global bearbeite_id
    auswahl = liste.curselection()
    if not auswahl:
        status_label.config(text="⚠  Bitte zuerst einen Kontakt anklicken", fg="#e74c3c")
        return

    alle_kontakte = hole_alle_kontakte()
    kontakt = alle_kontakte[auswahl[0]]  # (id, name, telefon, email)
    bearbeite_id = kontakt[0]  # Merkt sich die ID des Kontakts, der gerade bearbeitet wird

    # Felder leeren und mit den vorhandenen Werten befüllen
    eingabe_name.delete(0, tk.END)
    eingabe_name.insert(0, kontakt[1])
    eingabe_name.config(fg=FARBE_TEXT)  # Normale Textfarbe, kein Platzhalter-Grau

    eingabe_telefon.delete(0, tk.END)
    eingabe_telefon.insert(0, kontakt[2] if kontakt[2] else "Telefon")
    eingabe_telefon.config(fg=FARBE_TEXT if kontakt[2] else FARBE_TEXT_GEDAEMPFT)

    eingabe_email.delete(0, tk.END)
    eingabe_email.insert(0, kontakt[3] if kontakt[3] else "Email")
    eingabe_email.config(fg=FARBE_TEXT if kontakt[3] else FARBE_TEXT_GEDAEMPFT)

    button_speichern.config(text="✓  Änderung speichern", bg="#2ecc71")  # Zeigt an: wir sind im Bearbeiten-Modus
    button_abbrechen.pack(pady=(0, 8), padx=20, fill="x")  # Zeigt den Abbrechen-Button an
    status_label.config(text=f"✎  Bearbeite '{kontakt[1]}'", fg=FARBE_TEXT_GEDAEMPFT)


def kontakt_loeschen():
    auswahl = liste.curselection()
    if not auswahl:
        status_label.config(text="⚠  Bitte zuerst einen Kontakt anklicken", fg="#e74c3c")
        return

    alle_kontakte = hole_alle_kontakte()
    gewaehlter_kontakt = alle_kontakte[auswahl[0]]
    kontakt_id = gewaehlter_kontakt[0]

    verbindung = sqlite3.connect("kontakte.db")
    cursor = verbindung.cursor()
    cursor.execute("DELETE FROM kontakte WHERE id = ?", (kontakt_id,))
    verbindung.commit()
    verbindung.close()

    if bearbeite_id == kontakt_id:  # Falls genau der gelöschte Kontakt gerade bearbeitet wurde
        modus_zuruecksetzen()

    status_label.config(text=f"🗑  '{gewaehlter_kontakt[1]}' gelöscht", fg=FARBE_TEXT_GEDAEMPFT)
    liste_neu_zeichnen()


def erstelle_eingabefeld(parent, platzhalter):
    feld = tk.Entry(
        parent, font=("Segoe UI", 11), bg=FARBE_FELD, fg=FARBE_TEXT,
        insertbackground=FARBE_TEXT,
        relief="flat", highlightthickness=1,
        highlightbackground=FARBE_FELD, highlightcolor=FARBE_AKZENT
    )
    feld.insert(0, platzhalter)
    feld.config(fg=FARBE_TEXT_GEDAEMPFT)

    def bei_fokus(event):
        if feld.get() == platzhalter:
            feld.delete(0, tk.END)
            feld.config(fg=FARBE_TEXT)

    def bei_fokus_verlassen(event):
        if feld.get() == "":
            feld.insert(0, platzhalter)
            feld.config(fg=FARBE_TEXT_GEDAEMPFT)

    feld.bind("<FocusIn>", bei_fokus)
    feld.bind("<FocusOut>", bei_fokus_verlassen)
    return feld


erstelle_datenbank()

fenster = tk.Tk()
fenster.title("Kontakte")
fenster.geometry("380x560")
fenster.configure(bg=FARBE_HINTERGRUND)

tk.Label(
    fenster, text="Kontakte", font=("Segoe UI", 18, "bold"),
    bg=FARBE_HINTERGRUND, fg=FARBE_TEXT
).pack(pady=(20, 15))

rahmen_eingabe = tk.Frame(fenster, bg=FARBE_HINTERGRUND)
rahmen_eingabe.pack(padx=20, fill="x")

eingabe_name = erstelle_eingabefeld(rahmen_eingabe, "Name")
eingabe_name.pack(pady=4, fill="x", ipady=6)

eingabe_telefon = erstelle_eingabefeld(rahmen_eingabe, "Telefon")
eingabe_telefon.pack(pady=4, fill="x", ipady=6)

eingabe_email = erstelle_eingabefeld(rahmen_eingabe, "Email")
eingabe_email.pack(pady=4, fill="x", ipady=6)

button_speichern = tk.Button(
    fenster, text="＋  Kontakt speichern", command=kontakt_speichern,
    font=("Segoe UI", 10, "bold"), bg=FARBE_AKZENT, fg="white",
    activebackground=FARBE_AKZENT_HOVER, activeforeground="white",
    relief="flat", cursor="hand2", padx=10, pady=8, bd=0
)
button_speichern.pack(pady=(12, 4), padx=20, fill="x")

button_abbrechen = tk.Button(
    fenster, text="Abbrechen", command=modus_zuruecksetzen,
    font=("Segoe UI", 9), bg=FARBE_HINTERGRUND, fg=FARBE_TEXT_GEDAEMPFT,
    activebackground=FARBE_HINTERGRUND, relief="flat", cursor="hand2", bd=0
)  # Wird erst bei Bedarf mit .pack() sichtbar gemacht, siehe kontakt_bearbeiten()

status_label = tk.Label(fenster, text="", font=("Segoe UI", 9), bg=FARBE_HINTERGRUND, fg=FARBE_TEXT_GEDAEMPFT)
status_label.pack(pady=(2, 10))

tk.Frame(fenster, bg=FARBE_FELD, height=1).pack(fill="x", padx=20)

tk.Label(
    fenster, text="GESPEICHERTE KONTAKTE", font=("Segoe UI", 8, "bold"),
    bg=FARBE_HINTERGRUND, fg=FARBE_TEXT_GEDAEMPFT
).pack(pady=(12, 6))

rahmen_liste = tk.Frame(fenster)
rahmen_liste.pack(pady=(0, 5), padx=20, fill="both", expand=True)

scrollbar = tk.Scrollbar(rahmen_liste)
scrollbar.pack(side="right", fill="y")

liste = tk.Listbox(
    rahmen_liste, font=("Segoe UI", 10), bg=FARBE_FELD, fg=FARBE_TEXT,
    selectbackground=FARBE_AKZENT, selectforeground="white",
    relief="flat", bd=0, highlightthickness=0,
    yscrollcommand=scrollbar.set, activestyle="none"
)
liste.pack(side="left", fill="both", expand=True)
scrollbar.config(command=liste.yview)
liste.bind("<Double-Button-1>", lambda event: kontakt_bearbeiten())  # Doppelklick startet direkt die Bearbeitung

rahmen_buttons_unten = tk.Frame(fenster, bg=FARBE_HINTERGRUND)
rahmen_buttons_unten.pack(pady=(5, 15))

tk.Button(
    rahmen_buttons_unten, text="Bearbeiten", command=kontakt_bearbeiten,
    font=("Segoe UI", 9), bg=FARBE_HINTERGRUND, fg=FARBE_AKZENT,
    activebackground=FARBE_HINTERGRUND, relief="flat", cursor="hand2", bd=0
).pack(side="left", padx=10)

tk.Button(
    rahmen_buttons_unten, text="Löschen", command=kontakt_loeschen,
    font=("Segoe UI", 9), bg=FARBE_HINTERGRUND, fg=FARBE_LOESCHEN,
    activebackground=FARBE_HINTERGRUND, relief="flat", cursor="hand2", bd=0
).pack(side="left", padx=10)

liste_neu_zeichnen()
fenster.mainloop()