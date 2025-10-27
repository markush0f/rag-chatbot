# ☁️ Integración de Google Drive en el Chatbot con RAG

Este documento explica cómo se integra **Google Drive** en el proyecto del chatbot utilizando un enfoque **RAG (Retrieval-Augmented Generation)**. El objetivo es permitir que el modelo de IA responda preguntas basándose en información actualizada proveniente de documentos almacenados en Google Drive.

---

## 🧩 1. Objetivo de la integración

El chatbot está diseñado para responder únicamente con información específica de la **Agencia**. En lugar de depender de una base de datos estática, se utiliza un documento en Google Drive (PDF, DOCX o Google Docs) como fuente de conocimiento.

Cada vez que este documento cambia, el backend puede descargar la nueva versión y **reconstruir el índice vectorial (FAISS)**, manteniendo el chatbot siempre actualizado.

---

## ⚙️ 2. Flujo general del sistema RAG con Google Drive

1. **Documento fuente:** El archivo principal está en Google Drive.
2. **Descarga y exportación:** El backend descarga el archivo mediante la API de Google Drive, usando OAuth o una Service Account. Si el archivo es un Google Docs, se exporta automáticamente como PDF.
3. **Procesamiento:** LangChain carga el documento, lo divide en fragmentos (chunks) y genera embeddings con OpenAI.
4. **Vectorización:** Los embeddings se guardan en FAISS, una base vectorial local.
5. **Consulta:** Cuando el usuario hace una pregunta, el sistema busca los fragmentos más similares en FAISS y pasa ese contexto al modelo de IA (GPT-4o-mini) para generar la respuesta.

---

## 🔐 3. Configuración en Google Cloud Console

Antes de poder acceder a Google Drive mediante la API, es necesario configurar correctamente el entorno en Google Cloud Console.

### 🔸 Pasos para habilitar la API de Google Drive:

1. Accede a [Google Cloud Console](https://console.cloud.google.com/).
2. Crea un **nuevo proyecto** o selecciona uno existente (por ejemplo, `chatbot-agencia`).
3. En el menú lateral, entra en:

   ```
   API y servicios → Biblioteca
   ```
4. Busca **Google Drive API**.
5. Haz clic en **Habilitar**.
6. Espera unos minutos a que la activación se propague.

---

### 🔸 Crear credenciales OAuth 2.0

1. Dentro del mismo proyecto, entra en:

   ```
   API y servicios → Credenciales → Crear credenciales → ID de cliente de OAuth
   ```
2. En tipo de aplicación selecciona **“Aplicación de escritorio”**.
3. Asigna un nombre (por ejemplo, `Chatbot Drive Access`).
4. Descarga el archivo JSON de credenciales.
5. Renómbralo a:

   ```
   client_secrets.json
   ```
6. Colócalo en la raíz del proyecto (`chatbot-agencia/client_secrets.json`).

> ⚠️ Este archivo **no debe subirse a GitHub**. Inclúyelo en el `.gitignore`.

---

### 🔸 Configurar la pantalla de consentimiento OAuth

1. En el menú lateral, entra en:

   ```
   API y servicios → Pantalla de consentimiento de OAuth
   ```
2. Configura el nombre de la app, correo de soporte y dominio (si aplica).
3. En la sección **Usuarios de prueba**, añade tu cuenta de Gmail:

   ```
   abramianmedina@gmail.com
   ```
4. Guarda los cambios.

> 🔐 Esto es necesario porque la app está en modo “Testing” y solo los usuarios de prueba pueden autenticarse.

---

### 🔸 Autenticación inicial (primer uso)

1. Ejecuta el endpoint `/auth/login` o corre el script `ingest.py`.
2. Se abrirá una ventana del navegador con el mensaje de advertencia:

   > *“Google hasn’t verified this app”*
   > Pulsa **“Avanzado → Ir a Chatbot (inseguro)”** y luego **Continuar**.
3. Inicia sesión con tu cuenta de Google.
4. Se generará automáticamente un archivo `token.json` con los tokens de acceso.

> ✅ En futuras ejecuciones ya no será necesario autenticarse manualmente.

---

## 📂 4. Descarga y exportación del documento

La función `download_from_drive()` maneja la descarga automática y la exportación si se trata de un Google Docs.

| Tipo           | MIME Original                              | Exportado como    |
| -------------- | ------------------------------------------ | ----------------- |
| Google Docs    | `application/vnd.google-apps.document`     | `application/pdf` |
| Google Sheets  | `application/vnd.google-apps.spreadsheet`  | `.xlsx`           |
| Google Slides  | `application/vnd.google-apps.presentation` | `application/pdf` |
| Archivo normal | —                                          | Descarga directa  |

El archivo descargado se guarda en la ruta definida en `.env` (por ejemplo `agencia.pdf`).

---

## 🧠 5. Construcción de la base vectorial FAISS

El proceso de vectorización se realiza con LangChain:

1. Detecta el tipo de archivo (`.txt`, `.pdf`, `.docx`).
2. Carga el contenido con los loaders de LangChain.
3. Divide el texto en fragmentos (`RecursiveCharacterTextSplitter`).
4. Genera embeddings con `OpenAIEmbeddings`.
5. Guarda la base FAISS localmente (`VECTOR_DB_PATH`).

Cada fragmento del documento se representa como un vector semántico, lo que permite búsquedas por similitud.

---

## 🤖 6. Consulta y generación de respuestas

Cuando el usuario envía una pregunta:

1. FAISS busca los fragmentos más relevantes en la base vectorial.
2. Esos fragmentos se combinan en un contexto.
3. El contexto y la pregunta se envían al modelo GPT.
4. El modelo genera una respuesta basada **solo** en la información del documento.

---

## 🔁 7. Endpoints relacionados con Google Drive

| Endpoint             | Descripción                                             |
| -------------------- | ------------------------------------------------------- |
| `POST /auth/login`   | Autentica el acceso a Google Drive (crea `token.json`). |
| `POST /drive/update` | Descarga la última versión del documento desde Drive.   |
| `POST /vector/build` | Reconstruye la base vectorial FAISS.                    |
| `POST /chat`         | Responde preguntas utilizando el modelo RAG.            |

Flujo típico para actualizar el conocimiento:

```bash
POST /drive/update
POST /vector/build
```

---

## 🧰 8. Variables clave del entorno (.env)

```env
OPENAI_API_KEY=tu_api_key
DRIVE_FILE_ID=1AbCdEfGhIjKlMnOpQrStUvWxYz123456
LOCAL_FILE=agencia.pdf
VECTOR_DB_PATH=vectordb
```

---

## 🚀 9. Beneficios del enfoque RAG con Drive

* **Actualización automática:** sincroniza el conocimiento del bot con los documentos reales.
* **Privacidad total:** los documentos se mantienen en tu cuenta de Drive.
* **Integración fluida:** el backend descarga, procesa y actualiza todo vía API.
* **Escalabilidad:** permite añadir más documentos en el futuro.

---

## ✅ 10. Buenas prácticas

* No subir `client_secrets.json` ni `token.json` al repositorio.
* Incluir `/vectordb` en `.gitignore`.
* Reautenticar si cambias de proyecto o cuenta en Google Cloud.
* Usar `POST /vector/build` después de cada actualización del documento.

---

### 🏁 Conclusión

La integración de **Google Drive** con el backend del chatbot ofrece un flujo RAG completo: acceso a información viva, generación de embeddings, búsqueda semántica y respuestas contextuales con IA.
Este sistema garantiza que el chatbot de la Agencia se mantenga **siempre actualizado, sincronizado y seguro**.
