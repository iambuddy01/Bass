import os

# ======================
# BOT + ASSISTANT CONFIG
# ======================

API_ID = int(os.getenv("API_ID", "22657083"))          # from my.telegram.org
API_HASH = os.getenv("API_HASH", "d6186691704bd901bdab275ceaab88f3")
BOT_TOKEN = os.getenv("BOT_TOKEN", "8305955073:AAEAm8sFUlhEY-q3V33vEqbJ3vaGbQGTgnA")

# Assistant (user account) session string
SESSION_STRING = os.getenv("SESSION_STRING", "BQFMsJ0ASjjorZ8hjDZs3Dcm2Zo_D91wYeosTuTxPDtn4ZxJwtOba30i2O8n8kM4xbIitU4J5P6sn00_hdgWp2hBSroLFolv9m0PY-x3gH_PUEjnBQGeu9nqVtv_MwXWu9jWjdhnCjGnRYpMyj8W7XjoagUDgJuBYKxutiT2lwK0tX-mcKi49P6cZeYS_HVrliRb2DKbJs_GYInFjQcJfEaKEscuc3mIvC4UggeLu-ms1Gk-BBTf7pm_C1sLGrjZGOXTguphjHQ1edAwAOKMcAh02brBnTt0RFf94662YSJ6bdKLbUvRmwguDxAhC-MdaDXs1kqxmiRBPjPem5Ys1QMw4c7_cwAAAAHpMPeqAA")

# MongoDB (for saving user data)
MONGO_URL = os.getenv("MONGO_URL", "mongodb+srv://IVANxNISHA:IVANxNISHA@cluster0.pq52raw.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
