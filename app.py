import os
import re

from PyPDF2 import PdfReader
import fitz
from PIL import Image
import io

import pytesseract as tess


# Function to classify a page
def classify_page(text):

    for class_name, keywords in classes.items():
        for keyword in keywords:
            # Check if page have some keyword
            if re.search(r"\b{}\b".format(keyword), text):
                return class_name, keyword

    # if in pdf is scanned image, and we can't get a correct text(because the picture has too low quality)
    # or we couldn't find the keyword
    # we classify the page as "Unclassified" class
    return "Unclassified"


def extract_image(page_num, pdf_path):
    pdf = fitz.open(pdf_path)
    page = pdf[page_num]
    images = page.get_images()
    image = images[0]
    info_img = pdf.extract_image(image[0])
    image_data = info_img["image"]
    img = Image.open(io.BytesIO(image_data))
    extension = info_img["ext"]
    name_img = f"image.{extension}"
    img.save(open(name_img, "wb"))

    return get_text_from_image(name_img)


def get_text_from_image(name):
    tess_cmd_path = "C:/Program Files/Tesseract-OCR/tesseract.exe"
    tess.pytesseract.tesseract_cmd = tess_cmd_path
    myconfig = "--psm 12 --oem 3"

    img = Image.open(name)
    text = tess.image_to_string(img, config=myconfig)

    return classify_page(text)


# Define keywords for each class
classes = {
    'RFA': ['Request for Authorization', 'RFA', 'UR', 'Utilization Review', 'Peer Review', 'DWC', 'Doctor 1st report',
            'Doctor First Report', 'DWC FORM', '5021'],
    'Medical Records': ['Progress Notes', 'Medical records', 'Objective', 'Notes', 'Exam', 'Findings', 'PR2'],
    'IMR': ['IMR', 'IME', 'QME'],
    'Fax': ['Fax', 'Fax Form']
}

folder = "files"

files = os.listdir(folder)

for file in files:

    file_path = os.path.join(folder, file)

    with open(file_path, 'rb') as f:
        pdf = PdfReader(f)

        for page_num in range(len(pdf.pages)):

            page_text = pdf.pages[page_num].extract_text()

            # If was received an empty text, use methods to get text from scanned image in pdf file
            if page_text == '':
                item = extract_image(page_num, file_path)
            else:
                item = classify_page(page_text)

            if item == "Unclassified":
                print(f"Page {page_num + 1} of {file} is classified as: {item}")
            else:
                page_class = item[0]
                page_keyword = item[1]

                explanation = f" because it has a keyword: {page_keyword}"

                print(f"Page {page_num + 1} of {file} is classified as: {page_class}" + explanation)
