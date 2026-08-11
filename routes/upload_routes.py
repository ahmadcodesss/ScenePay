from flask import Blueprint, render_template, request, redirect, url_for, session
from PIL import Image
import pytesseract
from ..utils.parse import parse_bill_text

upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/group/<int:group_id>/upload_receipt', methods=["GET", "POST"])
def upload_receipt(group_id):
    if request.method == "POST":
        file = request.files.get("receipt_image")

        if file and file.filename:
            try:
                image = Image.open(file.stream)
                text = pytesseract.image_to_string(image)
                parsed_data = parse_bill_text(text)
                if parsed_data:
                    session['ocr_items'] = parsed_data
            except Exception as e:
                print("DEBUG: OCR failed:", repr(e))

        return redirect(url_for('main.manual_form', group_id=group_id))

    return render_template("upload.html", group_id=group_id)