import zipfile
import os
import shutil
import argparse
from PIL import Image

# Funzione per comprimere le immagini
def compress_image(image_path, quality=70):
    try:
        img = Image.open(image_path)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")  # Convertire in RGB se necessario
        img.save(image_path, "JPEG", quality=quality)
    except Exception as e:
        print(f"Errore durante la compressione di {image_path}: {e}")

def compress_epub(epub_file, quality):
    # Nome del file EPUB compresso
    compressed_epub_file = os.path.splitext(epub_file)[0] + "_compressed.epub"

    # Directory temporanea per estrarre i file
    temp_dir = "temp_epub"

    # Estrai l'EPUB
    with zipfile.ZipFile(epub_file, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)

    # Trova e comprimi le immagini
    for root, _, files in os.walk(temp_dir):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                image_path = os.path.join(root, file)
                compress_image(image_path, quality)

    # Crea il nuovo file EPUB compresso
    with zipfile.ZipFile(compressed_epub_file, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
        for root, _, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, temp_dir)
                zip_ref.write(file_path, arcname)

    # Pulizia della directory temporanea
    shutil.rmtree(temp_dir)

    print(f"EPUB compresso creato: {compressed_epub_file}")

# Parsing degli argomenti da linea di comando
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Comprimere immagini all'interno di file EPUB con qualità specificata.")
    parser.add_argument("quality", type=int, help="Qualità di compressione delle immagini (1-100).")
    parser.add_argument("-f", "--all-files", action="store_true",
                        help="Comprime tutti i file EPUB nella directory corrente.")
    parser.add_argument("epub_file", nargs="?", default=None,
                        help="Il percorso del file EPUB da comprimere (ignorato se -f è specificato).")
    args = parser.parse_args()

    if not (1 <= args.quality <= 100):
        print("Errore: La qualità deve essere un valore tra 1 e 100.")
    elif args.all_files:
        # Comprime tutti i file EPUB nella directory corrente
        epub_files = [f for f in os.listdir('.') if f.lower().endswith('.epub')]
        if not epub_files:
            print("Nessun file EPUB trovato nella directory corrente.")
        else:
            print(f"Trovati {len(epub_files)} file EPUB. Inizio compressione...")
            for epub_file in epub_files:
                compress_epub(epub_file, args.quality)
    elif args.epub_file:
        # Comprime un singolo file EPUB specificato
        if not os.path.isfile(args.epub_file):
            print(f"Errore: Il file {args.epub_file} non esiste.")
        elif not args.epub_file.lower().endswith('.epub'):
            print("Errore: Il file specificato non è un EPUB.")
        else:
            compress_epub(args.epub_file, args.quality)
    else:
        print("Errore: Specificare un file EPUB o utilizzare l'opzione -f per comprimere tutti i file EPUB.")
