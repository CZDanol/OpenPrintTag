# QR codes

## 1. Used standards
- [QR Code (ISO/IEC 18004:2024)](https://www.iso.org/standard/83389.html)
- [Base45 (RFC-9285)](https://datatracker.ietf.org/doc/rfc9285/)
- [Concise Binary Object Representation (CBOR)](https://cbor.io/)

Aside from the NFC tags, OpenPrintTag-compatible data can also be stored in QR codes.

1. The contents of the QR code are:
    1. (optional) User-specified URI, suffixed with `#`.
        1. *Note: The `#` suffix ensures that the OpenPrintTag data will be considered a fragment of the URI and will not be sent to the server.*
    1. The `OPTAG*` prefix.
        1. An OpenPrintTag QR reader SHALL check for the data starting  with the prefix. If the data doesn't start with the prefix, it SHALL search for the **last** occurrence of `#OPTAG*`.
    1. The CBOR-encoded payload of the **main section** of an [equivalent NFC OpenPrintTag](/nfc_data_format), encoded as **Base45**, immediately following the prefix.
        1. The OpenPrintTag QR code does **not** contain the meta or auxiliary regions.
            1. *Note: Auxiliary region is intended for dynamic data, which is irrelevant in the case of a QR code.*
            1. *Note: Meta region is not necessary without the possibility of the auxiliary region presence.*
        1. To maximize data density, the QR code representation of the binary data SHOULD be encoded using the QR alphanumeric mode.
2. The QR code SHOULD use at least the M error correction level.

## Examples


### Generating a QR code
To generate an OpenPrintTag QR code, you can use the `qr_generate` utility from the [specification git repository]({{repo}}/tree/main/utils). The utility accepts a data file in the same format as `rec_update`, following the [opt_json.schema.json]({{repo}}/tree/main/utils/schema/opt_json.schema.json).

{{ show_file("sample_data/data_to_fill.yaml") }}
{{ show_example(">qr_generate.py sample_data/data_to_fill.yaml --uri https://openprinttag.org -o $DOCS_OUT/qr.png") }}

<img src="qr.png" style="max-width: 256px;">

### Reading a QR code
To read an OpenPrintTag QR code, you can pass the scanned QR code data to the `rec_info` utility. The utility expects an OpenPrintTag binary data by default, so the correct [`config_qr.yaml`]({{repo}}/tree/main/config/config_qr.yaml) file needs to be provided to it using the `-c` or `--config-file` argument.

{{ show_example("zbarimg $DOCS_OUT/qr.png -q --raw | >rec_info.py --config-file=config_qr.yaml --show-all") }}
