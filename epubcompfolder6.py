"""
Script per comprimere immagini all'interno di file EPUB e salvare i file compressi in una directory separata.

Esempi di utilizzo:
1. Comprimere un singolo file EPUB con qualità specificata:
   python script.py 70 example.epub

2. Comprimere tutti i file EPUB nella directory corrente con qualità specificata:
   python script.py 70 -f

Funzionamento:
- I file EPUB compressi vengono salvati nella sottocartella "compressed", che viene creata automaticamente nella 
  directory corrente se non esiste.
- I file compressi avranno lo stesso nome dei file originali, ma saranno salvati nella directory "compressed".
- Se la directory "compressed" esiste già, i nuovi file compressi la utilizzeranno senza necessità di ulteriori interventi.

Parametri:
- quality: Qualità di compressione delle immagini (1-100).
- -f, --all-files: Opzionale. Se specificato, comprime tutti i file EPUB nella directory corrente.
- epub_file: Nome del file EPUB da comprimere (obbligatorio se -f non è specificato).
"""

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

def compress_epub(epub_file, quality, output_dir):
    # Salva la dimensione iniziale
    initial_size = os.path.getsize(epub_file)

    # Nome del file EPUB compresso temporaneamente
    temp_compressed_file = os.path.splitext(epub_file)[0] + "_compressed.epub"

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
    with zipfile.ZipFile(temp_compressed_file, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
        for root, _, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, temp_dir)
                zip_ref.write(file_path, arcname)

    # Sposta il file compresso nella directory di output con il nome originale
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    final_compressed_file = os.path.join(output_dir, os.path.basename(epub_file))
    shutil.move(temp_compressed_file, final_compressed_file)

    # Salva la dimensione finale
    final_size = os.path.getsize(final_compressed_file)

    # Calcola il rapporto di compressione
    compression_ratio = (initial_size - final_size) / initial_size * 100 if initial_size > 0 else 0

    # Pulizia della directory temporanea
    shutil.rmtree(temp_dir)

    return (os.path.basename(epub_file), initial_size, final_size, compression_ratio)

# Funzione per stampare il report
def print_report(files_info):
    print("\nReport di compressione:")
    for file_info in files_info:
        filename, initial_size, final_size, compression_ratio = file_info
        # Stampa il nome del file sulla prima riga
        print(f"{filename}")
        # Stampa le dimensioni e il rapporto di compressione sulla seconda riga
        print(f"{initial_size / (1024 * 1024):<25.2f} MB, {final_size / (1024 * 1024):<25.2f} MB, {compression_ratio:<.2f}%")
        print("-" * 70)  # Separatore tra i file

# Parsing degli argomenti da linea di comando
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Comprimere immagini all'interno di file EPUB con qualità specificata.")
    parser.add_argument("quality", type=int, help="Qualità di compressione delle immagini (1-100).")
    parser.add_argument("-f", "--all-files", action="store_true",
                        help="Comprime tutti i file EPUB nella directory corrente.")
    parser.add_argument("epub_file", nargs="?", default=None,
                        help="Il percorso del file EPUB da comprimere (ignorato se -f è specificato).")
    args = parser.parse_args()

    output_dir = "compressed"
    files_info = []

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
                file_info = compress_epub(epub_file, args.quality, output_dir)
                files_info.append(file_info)
            print_report(files_info)
    elif args.epub_file:
        # Comprime un singolo file EPUB specificato
        if not os.path.isfile(args.epub_file):
            print(f"Errore: Il file {args.epub_file} non esiste.")
        elif not args.epub_file.lower().endswith('.epub'):
            print("Errore: Il file specificato non è un EPUB.")
        else:
            file_info = compress_epub(args.epub_file, args.quality, output_dir)
            files_info.append(file_info)
            print_report(files_info)
    else:
        print("Errore: Specificare un file EPUB o utilizzare l'opzione -f per comprimere tutti i file EPUB.")
