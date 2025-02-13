import psycopg2
from googletrans import Translator
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate
import folium

db_params = {
    "dbname": "map_translation",    
    "user": "postgres",        
    "password": "vivek",    
    "host": "localhost",            
    "port": "5432"                  
}

try:
    # Establish connection
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()
    print("Connected to PostgreSQL")

    # 🔹 Step 2: Fetch Place Names and Coordinates from Database
    cursor.execute("SELECT id, place_name, latitude, longitude FROM map_data;")
    places = cursor.fetchall()  # Example: [(1, 'Pune', 18.5204, 73.8567), (2, 'Mumbai', 19.076, 72.8777)]

    # 🔹 Step 3: Initialize Translation & Transliteration
    translator = Translator()
    translated_data = []  # Store processed data for visualization

    # 🔹 Step 4: Process Each Place Name
    for place_id, place_name, lat, lon in places:
        # Translation (Meaning-based)
        translated_name = translator.translate(place_name, src="en", dest="hi").text
        
        # Transliteration (Phonetic-based)
        transliterated_name = transliterate(place_name, sanscript.ITRANS, sanscript.DEVANAGARI)

        # Update Database with Translated & Transliterated Names
        cursor.execute(
            "UPDATE map_data SET translated_name=%s, transliterated_name=%s WHERE id=%s",
            (translated_name, transliterated_name, place_id)
        )

        # Store data for visualization
        translated_data.append((place_name, translated_name, transliterated_name, lat, lon))
        print(f"🌍 {place_name} → 📝 Translation: {translated_name}, 🔡 Transliteration: {transliterated_name}")

    # Commit database changes
    conn.commit()
    print("✅ Database Updated Successfully!")

    # 🔹 Step 5: Create an Interactive Folium Map
    m = folium.Map(location=[19.7515, 75.7139], zoom_start=7)

    # Add markers for each place
    for name, translated, transliterated, lat, lon in translated_data:
        folium.Marker(
            location=[lat, lon],
            popup=f"English: {name}<br>Hindi (Translation): {translated}<br>Hindi (Transliteration): {transliterated}",
            tooltip=name
        ).add_to(m)

    # 🔹 Step 6: Save Map to HTML File
    m.save("map_with_translations.html")
    print("✅ Map has been saved as 'map_with_translations.html'")

    # Close Connection
    cursor.close()
    conn.close()
    print("🔒 Connection Closed")

except Exception as e:
    print("❌ Error:", e)
