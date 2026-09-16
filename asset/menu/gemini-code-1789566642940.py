from PIL import Image

files = ["Start_Button.png", "Exit_Button.png"]

for file in files:
    img = Image.open(file)
    # Convertir et sauvegarder sans enregistrer le profil iCCP
    img.save(file, icc_profile=None)
    print(f"{file} nettoyé avec succès.")
