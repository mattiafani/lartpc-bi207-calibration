import os
import fitz  # PyMuPDF
from PIL import Image

# Define the input folder containing PDFs and output GIF file path
input_folder = './gif_images/strips'
output_gif_path = './gif_images/strips.gif'
# input_folder = './gif_images/charge'
# output_gif_path = 'gif_images/charge.gif'
# input_folder = './gif_images/coincidence'
# output_gif_path = './gif_images/coincidence.gif'
# input_folder = './gif_images/cluster'
# output_gif_path = './gif_images/cluster.gif'
# input_folder = './gif_images/cluster_2023'
# output_gif_path = './gif_images/cluster_2023.gif'

# Create a list to store image file paths
image_paths = []

# Loop through each PDF file in the folder
for filename in os.listdir(input_folder):
    if filename.endswith('.pdf'):
        pdf_path = os.path.join(input_folder, filename)

        # Open the PDF file
        pdf_document = fitz.open(pdf_path)

        # Convert each page of the PDF to an image
        for page_num in range(pdf_document.page_count):
            page = pdf_document.load_page(page_num)
            pix = page.get_pixmap()
            image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            # Define the image file path and add it to the list
            image_path = os.path.splitext(filename)[0] + f'_page{page_num + 1}.png'
            image_paths.append(image_path)

            # Save the image
            image.save(image_path)

        # Close the PDF document
        pdf_document.close()

# Sort the image file paths alphabetically
image_paths.sort()

# Create a GIF from the sorted image files
images = [Image.open(image_path) for image_path in image_paths]
images[0].save(output_gif_path, save_all=True, append_images=images[1:], duration=500, loop=0)

# Clean up: remove the intermediate image files
for image_path in image_paths:
    os.remove(image_path)

print(f'GIF created and saved as "{output_gif_path}"')
