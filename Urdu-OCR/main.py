import pytesseract
from PIL import Image
import argparse
import os

def main():
    parser = argparse.ArgumentParser(description='Extract text from image using OCR')
    parser.add_argument('--image_path', type=str, required=True, help='Path to the input image')
    parser.add_argument('--lang', type=str, default='nawadraat_urdu', help='Language model to use (default: nawadraat_urdu)')
    
    args = parser.parse_args()
    
    img = Image.open(args.image_path)
    text = pytesseract.image_to_string(img, lang=args.lang)
    
    os.makedirs('output_images', exist_ok=True)
    
    base_name = os.path.basename(args.image_path)
    txt_name = os.path.splitext(base_name)[0] + '.txt'
    output_path = os.path.join('output_images', txt_name)
    
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(text)
    
    print(text)

if __name__ == '__main__':
    main()



