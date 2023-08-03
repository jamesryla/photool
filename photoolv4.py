import argparse
import exifread
import png
import csv
import sys

def get_exif_data(file_path):
    with open(file_path, 'rb') as f:
        if file_path.endswith(".png"):
            tags = {}
            reader = png.Reader(file=f)
            for chunk in reader.chunks():
                chunk_type, chunk_data = chunk[0], chunk[1]
                if chunk_type == "tEXt":
                    data = chunk_data.decode("utf-8").strip().split("\0")
                    if len(data) == 2:
                        tags[data[0]] = data[1]
        else:
            tags = exifread.process_file(f)
        return {k: v for k, v in tags.items() if k not in ('JPEGThumbnail', 'TIFFThumbnail', 'Filename', 'EXIF MakerNote')}

def get_strings_from_file(file_path, encodings=['utf-8', 'ISO-8859-1']):
    strings = []
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
                strings.extend([s for s in content.split() if s.isprintable()])
        except UnicodeDecodeError:
            continue
    return strings

def main(file_path, output_file=None, output_format='txt'):
    try:
        with open(file_path, 'rb') as f:
            exif_data = get_exif_data(file_path)
            strings = get_strings_from_file(file_path)

            if output_format == 'txt':
                results = "PHOTOOL\n" + \
                          "____  __  ______  __________  ____  __ \n" + \
                          "   / __ \\ / / / __ \\_  __/ __ \\/ __ \\/ / \n" + \
                          "  / /_/ / /_/ / / / / / / / / / / / / /  \n" + \
                          " / ____/ __  / /_/ / / / / /_/ / /_/ / /___\n" + \
                          "/_/   /_/ /_/\\____/ /_/  \\____/\\____/_____/\n" + \
                          "\n" + \
                          "EXIF Data:\n" + \
                          "-------------------\n"
                for tag, value in exif_data.items():
                    results += f"{tag}: {value}\n"
                results += "\nStrings:\n" + \
                           "-------------------\n"
                results += "\n".join(strings)

                if output_file:
                    with open(output_file, 'w') as f:
                        f.write(results)
                else:
                    print(results)
            elif output_format == 'csv':
                if output_file:
                    with open(output_file, 'w') as f:
                        writer = csv.writer(f)
                        writer.writerow(['Tag', 'Value'])
                        for tag, value in exif_data.items():
                            writer.writerow([tag, value])
                        writer.writerow([])
                        writer.writerow(['Strings'])
                        for string in strings:
                            writer.writerow([string])
                else:
                    writer = csv.writer(sys.stdout)
                    writer.writerow(['Tag', 'Value'])
                    for tag, value in exif_data.items():
                        writer.writerow([tag, value])
                    writer.writerow([])
                    writer.writerow(['Strings'])
                    for string in strings:
                        writer.writerow([string])
            else:
                print("Invalid output format. Please choose from 'txt' or 'csv'.")
    except FileNotFoundError:
        print("Image file not found")
    except Exception as e:
        print("Image type not supported")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='PHOTOOL - Info From Images')
    parser.add_argument('-i', '--image', type=str, help='Path to the image file', required=True)
    parser.add_argument('-o', '--output', type=str, help='Path to the output file')
    parser.add_argument('-f', '--format', choices=['txt', 'csv'], default='txt', help='Output format')
    args = parser.parse_args()
    main(args.image, args.output, args.format)
