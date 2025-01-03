from colorama import Fore, Style, init
from tqdm import tqdm
import zipfile
import os
import shutil
import argparse
from PIL import Image

# Inizializza Colorama
init(autoreset=True)

def compress_image(image_path, quality=70):
    """
    Comprime un'immagine:
    - Se è un JPEG, applica la compressione lossless con la qualità specificata.
    - Se è un PNG, riduce i colori a 256 (8-bit).
    """
    try:
        img = Image.open(image_path)
        if image_path.lower().endswith('.jpg') or image_path.lower().endswith('.jpeg'):
            # Compressione lossless per JPEG
            img.save(image_path, "JPEG", quality=quality, optimize=True)
        elif image_path.lower().endswith('.png'):
            # Riduzione a 256 colori per PNG
            img = img.convert('P', palette=Image.ADAPTIVE, colors=256)
            img.save(image_path, "PNG", optimize=True)
    except Exception as e:
        print(f"{Fore.RED}Errore durante la compressione di {image_path}: {e}")

def compress_epub(epub_file, quality, output_dir):
    """
    Comprime un file EPUB, applicando la compressione alle immagini.
    """
    print(f"\n{Fore.YELLOW}Inizio compressione: {epub_file}")

    initial_size = os.path.getsize(epub_file)
    temp_compressed_file = os.path.splitext(epub_file)[0] + "_compressed.epub"
    temp_dir = "temp_epub"

    try:
        # Estrai l'EPUB
        with zipfile.ZipFile(epub_file, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        # Trova tutte le immagini
        image_paths = []
        for root, _, files in os.walk(temp_dir):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    image_paths.append(os.path.join(root, file))

        # Comprimi le immagini
        with tqdm(total=len(image_paths), desc=f"Compressione immagini", unit="immagine") as pbar:
            for image_path in image_paths:
                compress_image(image_path, quality)
                pbar.update(1)

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

        print(f"{Fore.GREEN}Fine compressione con successo: {epub_file}")
        return (os.path.basename(epub_file), initial_size, final_size, compression_ratio)

    except Exception as e:
        print(f"{Fore.RED}Errore durante la compressione di {epub_file}: {e}")
        return None
    finally:
        # Rimuovi la directory temporanea
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

def print_report(files_info):
    """
    Stampa un report delle dimensioni dei file prima e dopo la compressione.
    """
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
    parser = argparse.ArgumentParser(description="Comprimere immagini all'interno di file EPUB.")
    parser.add_argument("quality", type=int, help="Qualità di compressione per le immagini JPEG (1-100).")
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
                if file_info:
                    files_info.append(file_info)
            print_report(files_info)
    elif args.epub_file:
        if not os.path.isfile(args.epub_file):
            print(f"{Fore.RED}Errore: Il file {args.epub_file} non esiste.")
        elif not args.epub_file.lower().endswith('.epub'):
            print(f"{Fore.RED}Errore: Il file specificato non è un EPUB.")
        else:
            file_info = compress_epub(args.epub_file, args.quality, output_dir)
            if file_info:
                files_info.append(file_info)
            print_report(files_info)
    else:
        print(f"{Fore.RED}Errore: Specificare un file EPUB o utilizzare l'opzione -f per comprimere tutti i file EPUB.")