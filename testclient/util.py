import qrcode


def forcestr(data):
    if isinstance(data, bytes):
        return data.decode("utf8")
    else:
        return str(data)


def qrcode_gen(data, version=1):
    white_block = "\033[0;37;47m  "
    black_block = "\033[0;37;40m  "
    new_line = "\033[0m\n"

    qr = qrcode.QRCode(version, error_correction=qrcode.ERROR_CORRECT_L)
    qr.add_data(data)
    qr.make()
    output = white_block * (qr.modules_count + 2) + new_line
    for mn in qr.modules:
        output += white_block
        for m in mn:
            if m:
                output += black_block
            else:
                output += white_block
        output += white_block + new_line
    output += white_block * (qr.modules_count + 2) + new_line
    return output
