import qrcode
import json
import os
from backend.config import Config

def generate_qr_code(data):
    if isinstance(data, dict):
        data = json.dumps(data)

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    os.makedirs(Config.QR_CODE_FOLDER, exist_ok=True)
    filename = f"qr_{data[:20].replace(':', '').replace('{', '').replace('}', '').replace('\"', '')}.png"
    filepath = os.path.join(Config.QR_CODE_FOLDER, filename)
    img.save(filepath)

    return filepath


def generate_qr_code_base64(data):
    import base64
    from io import BytesIO

    if isinstance(data, dict):
        data = json.dumps(data)

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()

    return f"data:image/png;base64,{img_str}"