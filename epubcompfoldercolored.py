from colorama import Fore, Style, init
import zipfile
import os
import shutil
import argparse
from PIL import Image

# Inizializza Colorama
init(autoreset=True)

# Funzione per comprimere le immagini
def compress_image(image_path, quality=70):
    try:
        img = Image.open(image_path)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")  # Convertire in RGB se necessario
        img.save(image_path, "JPEG", quality=quality)
    except Exception as e:
        print(f"{Fore.RED}Errore durante la compressione di {image_path}: {e}")

def compress_epub(epub_file, quality, output_dir):
    initial_size = os.path.getsize(epub_file)
    temp_compressed_file = os.path.splitext(epub_file)[0] + "_compressed.epub"
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

    # Sposta il file compresso nella directory di output
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    final_compressed_file = os.path.join(output_dir, os.path.basename(epub_file))
    shutil.move(temp_compressed_file, final_compressed_file)

    # Salva la dimensione finale
    final_size = os.path.getsize(final_compressed_file)
    compression_ratio = (initial_size - final_size) / initial_size * 100 if initial_size > 0 else 0

    # Pulizia della directory temporanea
    shutil.rmtree(temp_dir)

    return (os.path.basename(epub_file), initial_size, final_size, compression_ratio)

# Funzione per stampare il report
def print_report(files_info):
    print(f"\n{Fore.CYAN}Report di compressione:")
    for file_info in files_info:
        filename, initial_size, final_size, compression_ratio = file_info
        print(f"{Fore.GREEN}{filename}")
        print(f"{Fore.CYAN}Dimensioni iniziali: {initial_size / (1024 * 1024):.2f} MB, "
              f"Dimensioni finali: {final_size / (1024 * 1024):.2f} MB, "
              f"Rapporto di compressione: {compression_ratio:.2f}%")
        print(f"{Fore.CYAN}{'-' * 70}")

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
        print(f"{Fore.RED}Errore: La qualità deve essere un valore tra 1 e 100.")
    elif args.all_files:
        epub_files = [f for f in os.listdir('.') if f.lower().endswith('.epub')]
        if not epub_files:
            print(f"{Fore.RED}Nessun file EPUB trovato nella directory corrente.")
        else:
            print(f"{Fore.GREEN}Trovati {len(epub_files)} file EPUB. Inizio compressione...")
            for epub_file in epub_files:
                file_info = compress_epub(epub_file, args.quality, output_dir)
                files_info.append(file_info)
            print_report(files_info)
    elif args.epub_file:
        if not os.path.isfile(args.epub_file):
            print(f"{Fore.RED}Errore: Il file {args.epub_file} non esiste.")
        elif not args.epub_file.lower().endswith('.epub'):
            print(f"{Fore.RED}Errore: Il file specificato non è un EPUB.")
        else:
            file_info = compress_epub(args.epub_file, args.quality, output_dir)
            files_info.append(file_info)
            print_report(files_info)
    else:
        print(f"{Fore.RED}Errore: Specificare un file EPUB o utilizzare l'opzione -f per comprimere tutti i file EPUB.")
