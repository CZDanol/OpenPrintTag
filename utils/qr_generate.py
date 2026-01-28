# Reference implementation of initializing an "empty" Prusa Material NFC tag

import os
import sys
import types
from dataclasses import dataclass
from enum import Enum

import base45
import qrcode
import qrcode.util
import simple_parsing
import yaml
from fields import EncodeConfig, Fields
from qrcode.image.styledpil import StyledPilImage

default_config_file = os.path.join(os.path.dirname(__file__), "../data/config_qr.yaml")
default_embedded_image = os.path.join(os.path.dirname(__file__), "../images/qr_opt_logo.png")


class ErrorCorrection(Enum):
    L = qrcode.ERROR_CORRECT_L
    M = qrcode.ERROR_CORRECT_M
    Q = qrcode.ERROR_CORRECT_Q
    H = qrcode.ERROR_CORRECT_H


@dataclass
class Args:
    """Following command line arguments are accepted (you can also use the file as a module)"""

    # YAML file with the fields configuration
    config_file: str = simple_parsing.field(default=default_config_file, alias=["-c", "--config-file"])

    # Filename of the generated QR code
    # If not provided, the QR code data will only be output to the stdout
    out_filename: str | None = simple_parsing.field(default=None, alias=["-o", "--output"])

    # Error correction of the QR code
    error_correction: ErrorCorrection = simple_parsing.field(default=ErrorCorrection.H, alias=["-e", "--error-correction"])

    # Image to embed into the QR code
    embedded_image: str = simple_parsing.field(default=default_embedded_image, alias=["-i", "--image"])

    # If provided, prepends the OpenPrintTag data with an URL
    uri: str = simple_parsing.field(default="", alias=["-u", "--uri"])


def qr_generate(data: dict, args: Args):
    config_dir = os.path.dirname(args.config_file)
    with open(args.config_file, "r", encoding="utf-8") as f:
        config = types.SimpleNamespace(**yaml.safe_load(f))

    assert config.root == "qr", "qr_generate only supports QR config type"

    result = b""

    qr = qrcode.QRCode(
        error_correction=args.error_correction.value,
    )

    # Separate add_data calls are important, that way each segment can be encoded in an optimal mode
    if len(args.uri):
        uri_prefix = args.uri + "#"
        result += uri_prefix.encode()
        qr.add_data(uri_prefix)

    fields = Fields.from_file(os.path.join(config_dir, config.main_fields))
    opt_raw_data = fields.update(update_fields=data, config=EncodeConfig(indefinite_containers=False))

    # QR code does not support arbitrary binary data
    # Encode to Base45, which is optimal for QR code alphanumeric mode
    opt_data = b"OPTAG*" + base45.b45encode(opt_raw_data)

    result += opt_data
    qr.add_data(qrcode.util.QRData(opt_data, mode=qrcode.util.MODE_ALPHA_NUM))

    if args.out_filename:
        img = qr.make_image(
            image_factory=StyledPilImage,
            embedded_image_path=args.embedded_image if len(args.embedded_image) else None,
        )

        img.save(args.out_filename)

    return result


if __name__ == "__main__":
    parser = simple_parsing.ArgumentParser(
        prog="qr_generate",
        description="Takes a data YAML file and encodes them into the OpenPrintTag QR code format. The encoded data is printed to stdout and an image is generated.",
    )
    parser.add_argument("update_data", type=str, help="YAML file with the data. The fields should be in the 'data/main' YAML object.")
    parser.add_arguments(Args, dest="args")

    args = parser.parse_args()

    update_data = yaml.safe_load(open(args.update_data, "r", encoding="utf-8"))

    sys.stdout.buffer.write(qr_generate(update_data["data"]["main"], args.args))
