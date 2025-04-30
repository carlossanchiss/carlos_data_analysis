
# Strava Analytics Starter (Streamlit + Supabase)

Plantilla minimal para crear un panel Streamlit que permite a varios ciclistas conectar su cuenta Strava.  
Los datos básicos se guardan en Supabase y el entrenador puede cambiar de ciclista desde la barra lateral.

## ¿Qué incluye?

* Autenticación OAuth2 con Strava
* Almacenamiento de tokens y datos de atleta en Supabase
* Selección de ciclista (modo coach)
* Tabla y mapa muy simples como ejemplo

## Variables de entorno necesarias (se añaden como GitHub Secrets)

* STRAVA_CLIENT_ID  
* STRAVA_CLIENT_SECRET  
* SUPABASE_URL  
* SUPABASE_SERVICE_KEY  
* COACH_EMAIL  
* REDIRECT_URI  → la URL de esta app en Streamlit (una vez desplegada)
