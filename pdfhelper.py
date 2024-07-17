import os
import shutil
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib import utils
import barcode
from barcode.writer import ImageWriter
import sys

try:
    wd = sys._MEIPASS
except AttributeError:
    wd = os.getcwd()


# Function to create barcode image
def generate_barcode(code, temp_dir):
    EAN = barcode.get_barcode_class("ean13")
    ean = EAN(code, writer=ImageWriter())
    filename = ean.save(os.path.join(temp_dir, f"barcode_{code}"))
    return filename


# Function to add image to canvas
def add_image(c, path, x, y, width, height_reduction=0.3):
    img = utils.ImageReader(path)
    iw, ih = img.getSize()
    aspect = ih / float(iw)
    height = width * aspect * (1 - height_reduction)
    c.drawImage(path, x, y - height, width, height, mask="auto")
    return height


# Main function to generate the PDF
def generate_barcode_labels_pdf(data, output_filename="barcode_labels.pdf"):
    # Create a temporary directory for barcode images
    temp_dir = wd + "/temp"
    os.makedirs(temp_dir, exist_ok=True)
    print("temp_dir", temp_dir)

    try:
        c = canvas.Canvas(output_filename, pagesize=A4)
        width, height = A4

        # Constants
        x_offset = 10 * mm
        y_offset = 3 * mm  # Decreased y_offset to reduce gap between rows
        cell_width = (width - 4 * x_offset) / 3
        cell_height = 35 * mm  # Adjusted cell_height to reduce the height of each cell

        current_x = x_offset
        current_y = height - y_offset - cell_height

        # Loop over the data and create labels
        for i, (id, name, price, code, extra) in enumerate(data):
            # Calculate column and row
            col = i % 3
            row = i // 3

            # Adjust y position if we are starting a new row
            if col == 0 and i != 0:
                current_y -= cell_height + y_offset

            # Center align calculations
            x = current_x + col * (cell_width + x_offset)
            center_x = x + cell_width / 2

            y = current_y

            # Add price
            c.setFont("Helvetica", 12)
            price_text = f"Price: £{price}"
            text_width = c.stringWidth(price_text, "Helvetica", 12)
            c.drawString(center_x - text_width / 2, y, price_text)

            # Add name
            c.setFont("Helvetica", 10)
            name_text = name
            text_width = c.stringWidth(name_text, "Helvetica", 10)
            c.drawString(center_x - text_width / 2, y - 12, name_text)

            # Add barcode
            barcode_path = generate_barcode(code, temp_dir)
            barcode_height = add_image(
                c, barcode_path, x + cell_width * 0.15, y - 24, cell_width * 0.7, 0.3
            )

            # Check if we need to start a new page
            if current_y <= y_offset:
                c.showPage()
                current_y = (
                    height - y_offset - cell_height
                )  # Reset current_y for the new page

        c.save()
    except Exception as e:
        print(e)

    finally:
        # Clean up temporary directory
        # shutil.rmtree(temp_dir)
        pass


# # Data
# data_string = [
#     ("1", "CM Cut Coconut Frozen 400g", "2.39", "8906157550042", "0"),
#     ("2", "PF Red Split Lentil 1Kg", "3.1", "749565640787", "0"),
#     ("3", "Example Product 1", "1.99", "1234567890123", "0"),
#     ("4", "Example Product 2", "4.5", "9876543210987", "0"),
#     ("5", "Another Product", "3.75", "4567890123456", "0"),
#     ("6", "New Product", "2.15", "6543210987654", "0"),
#     ("7", "Test Product", "6.99", "7890123456789", "0"),
#     ("8", "Last Product", "0.99", "2345678901234", "0"),
#     ("9", "Final Product", "5.25", "8901234567890", "0"),
#     ("10", "Special Product", "3.49", "5432109876543", "0"),
#     ("11", "Unique Product", "7.89", "3210987654321", "0"),
#     ("12", "Great Product", "1.79", "0123456789012", "0"),
#     ("13", "Amazing Product", "4.29", "8765432109876", "0"),
#     ("14", "Excellent Product", "2.99", "2109876543210", "0"),
#     ("15", "Fantastic Product", "6.49", "7654321098765", "0"),
#     ("16", "Super Product", "0.49", "1098765432109", "0"),
#     ("17", "Ultra Product", "8.99", "6543210987654", "0"),
#     ("18", "Mega Product", "3.99", "2109876543210", "0"),
#     ("19", "Hyper Product", "5.99", "8765432109876", "0"),
#     ("20", "Majestic Product", "1.99", "5432109876543", "0"),
#     ("21", "Supreme Product", "7.49", "8901234567890", "0"),
#     ("22", "Deluxe Product", "2.49", "2345678901234", "0"),
#     ("23", "Premium Product", "4.99", "7890123456789", "0"),
#     ("24", "Luxury Product", "6.99", "6543210987654", "0"),
#     ("25", "Quality Product", "3.49", "2109876543210", "0"),
#     ("26", "Value Product", "1.99", "8765432109876", "0"),
#     ("27", "Economy Product", "0.99", "1098765432109", "0"),
#     ("28", "Budget Product", "5.99", "6543210987654", "0"),
#     ("29", "Saver Product", "2.99", "2109876543210", "0"),
#     ("30", "Bargain Product", "4.99", "8765432109876", "0"),
#     ("31", "Deal Product", "3.99", "5432109876543", "0"),
#     ("32", "Steal Product", "1.99", "8901234567890", "0"),
#     ("33", "Offer Product", "6.99", "2345678901234", "0"),
#     ("34", "Promo Product", "2.99", "7890123456789", "0"),
#     ("35", "Discount Product", "4.99", "6543210987654", "0"),
#     ("36", "Clearance Product", "3.99", "2109876543210", "0"),
#     ("37", "Sale Product", "1.99", "8765432109876", "0"),
#     ("38", "Reduced Product", "0.99", "1098765432109", "0"),
#     ("39", "Markdown Product", "5.99", "6543210987654", "0"),
#     ("40", "Special Offer Product", "2.99", "2109876543210", "0"),
#     ("41", "Limited Product", "4.99", "8765432109876", "0"),
#     ("42", "Rare Product", "3.99", "5432109876543", "0"),
#     ("43", "Unique Product", "1.99", "8901234567890", "0"),
#     ("44", "Collectible Product", "6.99", "2345678901234", "0"),
# ]

# # Call the function to generate the PDF
# generate_barcode_labels_pdf(data_string)
