from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from PIL import Image
import pytesseract
from ..utils.parse import parse_bill_text

upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/group/<int:group_id>/upload_receipt', methods=["GET", "POST"])
def upload_receipt(group_id):
    if request.method == "POST":
        file = request.files.get("receipt_image")
        print("DEBUG: file =", file)

        if file and file.filename:
            print("DEBUG: filename =", file.filename)
            try:
                image = Image.open(file.stream)
                print("DEBUG: image opened, size =", image.size)
                text = pytesseract.image_to_string(image)
                print("DEBUG: extracted text =", repr(text))
                parsed_data = parse_bill_text(text)
                print("DEBUG: parsed_data =", parsed_data)

                if parsed_data:
                    session['ocr_items'] = parsed_data
                    flash(f"Found {len(parsed_data)} item(s) on your receipt. Assign them below.", "success")
                else:
                    flash("Couldn't find any items on that receipt. You can add them manually.", "error")
            except Exception as e:
                print("DEBUG: EXCEPTION:", repr(e))
                flash("Couldn't read that receipt automatically. You can still add items manually.", "error")
        else:
            print("DEBUG: no file or empty filename")
            flash("No file was selected.", "error")

        return redirect(url_for('main.manual_form', group_id=group_id))

    return render_template("upload.html", group_id=group_id)