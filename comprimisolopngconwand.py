from wand.image import Image

def comprimi_png_wand(input_path, output_path, quality=75):
    """Comprime un'immagine PNG utilizzando Wand.

    Args:
        input_path (str): Percorso dell'immagine PNG originale.
        output_path (str): Percorso dell'immagine PNG compressa.
        quality (int, optional): Livello di qualità della compressione (0-100). Defaults to 75.
    """

    with Image(filename=input_path) as img:
        img.compression_quality = quality
        img.save(filename=output_path)

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 4:
        print("Utilizzo: python script.py <input_file> <output_file> <livello_compressione>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    try:
        quality = int(sys.argv[3])
        if quality < 0 or quality > 100:
            raise ValueError("Il livello di compressione deve essere compreso tra 0 e 100.")
    except ValueError:
        print("Il livello di compressione deve essere un numero intero.")
        sys.exit(1)

    comprimi_png_wand(input_file, output_file, quality)