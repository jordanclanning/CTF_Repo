def create_js_challenge(flag, output_path):
    xor_key = 0x41
    encoded = [ord(c) ^ xor_key for c in flag]
    
    js_payload = f"""
    var key = {xor_key};
    var data = {encoded};
    var flag = '';
    for (var i = 0; i < data.length; i++) {{
        flag += String.fromCharCode(data[i] ^ key);
    }}
    // flag is stored in: flag
    """
    pdf_content = f"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R /OpenAction 4 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>
endobj
4 0 obj
<< /Type /Action /S /JavaScript /JS ({js_payload}) >>
endobj
xref
...
"""
    with open(output_path, 'w') as f:
        f.write(pdf_content)

create_js_challenge("CTF{PDF_decode_master}", "suspicious.pdf")
