from PdfCropNew import *
import ghostscript
import locale
from PIL import Image
import os
import sys
import tempfile
from math import ceil
import cv2
import shutil


def pdf2jpeg(pdf_input_path, jpeg_output_path):
    args = ["pef2jpeg", # actual value doesn't matter
            "-dNOPAUSE",
            "-sDEVICE=jpeg",
            "-r720",
            "-sOutputFile=" + jpeg_output_path,
            pdf_input_path]

    encoding = locale.getpreferredencoding()
    args = [a.encode(encoding) for a in args]

    with ghostscript.Ghostscript(*args) as g:
        ghostscript.cleanup()


def add_margin(pil_img, top, right, bottom, left, color):
    width, height = pil_img.size
    new_width = width + right + left
    new_height = height + top + bottom
    result = Image.new(pil_img.mode, (new_width, new_height), color)
    result.paste(pil_img, (left, top))
    return result


def get_combined_page(img):
    if len(img) == 4:
        temp1 = cv2.addWeighted(img[0], 0.5, img[1], 0.5, 0)
        # temp1 *= 2
        temp2 = cv2.addWeighted(img[2], 0.5, img[3], 0.5, 0)
        # temp2 += 2
        c_page = cv2.addWeighted(temp1, 0.5, temp2, 0.5, 0)
        c_page *= 8

    elif len(img) == 3:
        temp1 = cv2.addWeighted(img[0], 0.5, img[1], 0.5, 0)
        c_page = cv2.addWeighted(temp1, 0.5, img[2], 0.5, 0)
        c_page *= 4

    elif len(img) == 2:
        c_page = cv2.addWeighted(img[0], 0.5, img[1], 0.5, 0)
        c_page *= 2

    else:
        c_page = img[0]

    return c_page


input_directory = sys.argv[1]

files = []
input_directory_path = os.path.join(os.getcwd(), input_directory)
# r=root, d=directories, f = files
for r, d, f in os.walk(input_directory_path):
    for file in f:
        if '.pdf' in file:
            files.append(os.path.join(r, file))

current_dir = os.getcwd()
output_directory = os.path.join(input_directory_path, "out")
if not os.path.exists(output_directory):
    os.mkdir(output_directory)
else:
    shutil.rmtree(output_directory)
    os.mkdir(output_directory)

if len(sys.argv) == 3:
    input1 = read_pdf(files[0])
    page = input1.getPage(0)
    cropped_page = crop_page(page, 0, 107, 0, 150)
    output = PdfFileWriter()
    output.addPage(cropped_page)

    os.chdir(tempfile.gettempdir())
    save_pdf("temp.pdf", output)

    pdf2jpeg("temp.pdf", "temp.jpeg")

    with Image.open("temp.jpeg") as im:
        color = (255, 255, 255)  # white

        corner = sys.argv[2]
        if corner == "tl":
            new_im = add_margin(im, 10, 2917, 4178, 0, color)
        elif corner == "tr":
            new_im = add_margin(im, 10, 0, 4178, 2917, color)
        elif corner == "bl":
            new_im = add_margin(im, 4178, 2917, 10, 0, color)
        elif corner == "br":
            new_im = add_margin(im, 4178, 0, 10, 2917, color)
        else:
            print("\n\nYou have entered Invalid corner to print\n\n")
        if os.path.exists("temp.pdf"):
            os.remove("temp.pdf")

        os.chdir(output_directory)
        new_im.save("out_{0}.jpeg".format(str(0)), quality=70)

    if os.path.exists("temp.jpeg"):
        os.remove("temp.jpeg")

else:
    for pg in range(ceil(len(files)/4)):
        count = 1
        for i in range(pg*4, min((pg+1)*4, len(files))):
            input1 = read_pdf(files[i])
            page = input1.getPage(0)
            cropped_page = crop_page(page, 0, 107, 0, 150)
            output = PdfFileWriter()
            output.addPage(cropped_page)

            os.chdir(tempfile.gettempdir())
            save_pdf("temp.pdf", output)

            pdf2jpeg("temp.pdf", "temp.jpeg")

            with Image.open("temp.jpeg") as im:
                color = (255, 255, 255)     # white

                # top-left
                if count == 1:
                    new_im = add_margin(im, 10, 2917, 4178, 0, color)
                # top-right
                elif count == 2:
                    new_im = add_margin(im, 10, 0, 4178, 2917, color)
                # bottom-left
                elif count == 3:
                    new_im = add_margin(im, 4178, 2917, 10, 0, color)
                # bottom-right
                elif count == 4:
                    new_im = add_margin(im, 4178, 0, 10, 2917, color)

                if os.path.exists("temp.pdf"):
                    os.remove("temp.pdf")

                os.chdir(output_directory)
                new_im.save("out_{0}.jpeg".format(str(count)), quality=70)

            if os.path.exists("temp.jpeg"):
                os.remove("temp.jpeg")

            count += 1

        os.chdir(output_directory)
        img = []
        for j in range(1, 5):
            if os.path.exists('out_' + str(j) + '.jpeg'):
                img.append(cv2.imread('out_' + str(j) + '.jpeg'))
                os.remove('out_' + str(j) + '.jpeg')

        combined_page = get_combined_page(img)

        cv2.imwrite("page_" + str(pg) + ".jpeg", combined_page)

print("\nSuccessful\n")
