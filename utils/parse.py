import re
import os
from dotenv import load_dotenv
from PIL import Image
import pytesseract
def parse_bill_text(text):
      SKIP_KEYWORDS = [
          'subtotal', 'sub total', 'total', 'tax', 'service charge',
          'svc charge', 'discount', 'change', 'cash', 'card',
          'balance', 'amount due', 'grand total', 'tip', 'gratuity',
          'vat', 'gst', 'date', 'time', 'shop no', 'shop #',
          'home delivery', 'address', 'phone', 'tel', 'contact no',
          'order no', 'invoice', 'receipt no', 'table no', 'covers',
          'thank you', 'welcome'
      ]

      DATE_PATTERN = re.compile(r'\d{1,2}[/\-.]\d{1,2}[/\-.]\d{2,4}')
      TIME_PATTERN = re.compile(r'\d{1,2}:\d{2}(:\d{2})?\s*(am|pm|AM|PM)?')

      items = {}
      lines = text.splitlines()
      for line in lines:
            line = line.strip()
            if not line:
                  continue

            line_lower = line.lower()

            if any(keyword in line_lower for keyword in SKIP_KEYWORDS):
                  continue

            if DATE_PATTERN.search(line) or TIME_PATTERN.search(line):
                  continue

            dish_match = re.search(
                r'([A-Za-z][A-Za-z0-9 ]*?)\s*[:;\-–—()\[\]\\|\'`/]*\s*(?=\d{1,3}(?:,\d{3})*(?:\.\d+)?|\d{2,})',
                line
            )

            if dish_match:
                  dish = dish_match.group(1).strip().lower()

                  if len(dish) <= 3:
                        continue

                  number_matches = re.findall(r'\d{1,3}(?:,\d{3})*(?:\.\d+)?', line)
                  numbers = [float(num.replace(',', '')) for num in number_matches]
                  numbers = sorted(numbers)
                  if len(numbers) >= 2:
                        chosen_price = numbers[-2]
                  else:
                        chosen_price = numbers[0]

                  items[dish] = chosen_price

      return items