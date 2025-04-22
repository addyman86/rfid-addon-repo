import mariadb
import paho.mqtt.client as mqtt

# MQTT-Konfiguration
MQTT_BROKER = "192.168.10.2"
MQTT_UID_TOPIC = "rfid/uid"
MQTT_PRODUCT_TOPIC = "rfid/name"
MQTT_STOCK_TOPIC = "rfid/menge"
MQTT_STOCK_SET_TOPIC = "rfid/neue_menge"
MQTT_DATA1_TOPIC = "rfid/data1"
MQTT_DATA2_TOPIC = "rfid/data2"

# MQTT-Benutzername und Passwort
MQTT_USER = "mqtt"
MQTT_PASSWORD = "kcnei4293"

# DB-Konfiguration
db_config = {
    "host": "192.168.10.2",
    "port": 3306,
    "user": "testuser",
    "password": "kcnei4293",
    "database": "lager"
}

# Globale Variable für zuletzt bekannte UID
letzte_uid = None

# Funktion zum Nachschlagen eines Produkts
def get_product_info(uid):
    try:
        conn = mariadb.connect(**db_config)
        cur = conn.cursor()
        cur.execute("SELECT produktname, lagerbestand, data1, data2 FROM produkte WHERE uid = ?", (uid,))
        result = cur.fetchone()
        conn.close()
        return result
    except Exception as e:
        print(f"Fehler bei Datenbankabfrage: {e}")
        return None

# Funktion zum Aktualisieren des Lagerbestands
def update_stock(uid, neuer_bestand):
    try:
        conn = mariadb.connect(**db_config)
        cur = conn.cursor()
        cur.execute("UPDATE produkte SET lagerbestand = ? WHERE uid = ?", (neuer_bestand, uid))
        conn.commit()
        conn.close()
        print(f"Lagerbestand für UID {uid} auf {neuer_bestand} gesetzt.")
    except Exception as e:
        print(f"Fehler beim Aktualisieren des Lagerbestands: {e}")

# Callback für empfangene Nachrichten
def on_message(client, userdata, msg):
    global letzte_uid

    topic = msg.topic
    payload = msg.payload.decode().strip()

    if topic == MQTT_UID_TOPIC:
        uid = payload
        print(f"Empfangene UID: {uid}")
        letzte_uid = uid
        result = get_product_info(uid)
        if result:
            produkt, bestand, data1, data2 = result
            print(f"Gefunden: {produkt} ({bestand})")
            client.publish(MQTT_PRODUCT_TOPIC, produkt)
            client.publish(MQTT_STOCK_TOPIC, str(bestand))
            client.publish(MQTT_DATA1_TOPIC, str(data1))
            client.publish(MQTT_DATA2_TOPIC, str(data2))
        else:
            print("Unbekannte UID")
            letzte_uid = None
    elif topic == MQTT_STOCK_SET_TOPIC:
        if payload == "":
            return  # Leere Nachricht ignorieren

        if letzte_uid is None:
            print("Kein Produkt ausgewählt. Lagerbestand wird ignoriert.")
            return
        try:
            neuer_bestand = int(payload)
            update_stock(letzte_uid, neuer_bestand)
            client.publish(MQTT_STOCK_TOPIC, str(neuer_bestand))
        except ValueError:
            print(f"Ungültiger Lagerbestand: {payload}")
        finally:
            client.publish(MQTT_STOCK_SET_TOPIC, "")

# MQTT verbinden und abonnieren
client = mqtt.Client()
client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
client.on_message = on_message
client.connect(MQTT_BROKER)
client.subscribe(MQTT_UID_TOPIC)
client.subscribe(MQTT_STOCK_SET_TOPIC)

print(f"Höre auf Topics:\n - {MQTT_UID_TOPIC}\n - {MQTT_STOCK_SET_TOPIC}")
client.loop_forever()
