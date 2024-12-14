import sys
from PIL import Image

def comprimi_png(input_path, output_path, compression_level=9):
    """Comprime un'immagine PNG utilizzando Pillow.

    Args:
        input_path (str): Percorso dell'immagine PNG originale.
        output_path (str): Percorso dell'immagine PNG compressa.
        compression_level (int, optional): Livello di compressione (0-9). Defaults to 9.
    """

    try:
        with Image.open(input_path) as img:
            img.save(output_path, optimize=True, compress_level=compression_level)
        print("Immagine compressa con successo!")
    except FileNotFoundError:
        print(f"Impossibile trovare il file: {input_path}")
    except Exception as e:
        print(f"Si è verificato un errore: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Utilizzo: python script.py <input_file> <output_file> <livello_compressione>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    try:
        compression_level = int(sys.argv[3])
        if compression_level < 0 or compression_level > 9:
            raise ValueError("Il livello di compressione deve essere compreso tra 0 e 9.")
    except ValueError:
        print("Il livello di compressione deve essere un numero intero.")
        sys.exit(1)

    comprimi_png(input_file, output_file, compression_level)