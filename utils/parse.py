import re
import os
from dotenv import load_dotenv
from PIL import Image
import pytesseract
def parse_bill_text(text):
      items = {}
      lines = text.splitlines()
      for line in lines:
            if not line.strip():
                  continue
            dish_match = re.search(
    r'([A-Za-z][A-Za-z0-9 ]*?)\s*[:;\-–—()\[\]\\|\'`/]*\s*(?=\d{1,3}(?:,\d{3})*(?:\.\d+)?|\d{2,})',
    line
)

            
            if dish_match:
                  dish = dish_match.group(1).strip().lower()
                  number_matches = re.findall(r'\d{1,3}(?:,\d{3})*(?:\.\d+)?', line)
                  numbers = [float(num.replace(',', '')) for num in number_matches]

                  print("numbers::::::")
                  print(numbers)
                  # numbers= [float(n) for n in numbers]
                  numbers = sorted(numbers)
                  if len(numbers) >= 2:
                        chosen_price = numbers[-2]
                  else:
                        chosen_price = numbers[0]

                  items[dish] = chosen_price
      
      return items
# load_dotenv()  # at top of your app
# pytesseract.pytesseract.tesseract_cmd = os.getenv("TESSERACT_CMD", "tesseract")
# text=pytesseract.image_to_string(r"C:\Users\DELL\Downloads\q.jpeg")
# dishes=parse_bill_text(text)

# print("\n"+text+"\n")
# for dish,price in dishes.items():
#    print(f"{dish}:{price}")
