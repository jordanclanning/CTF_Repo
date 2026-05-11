from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import PyPDF2

def create_meta_challenge(flag, output_path):
    c = canvas.Canvas(output_path, pagesize=letter)
    c.setTitle("Quarterly Report")
    c.setAuthor("Jordan. C. Lanning, M.I.T., M.P.A.")
    c.setSubject(ECE_5540_Project9)           # hidden here
    c.setKeywords("Cybersecurtiy,q3")  # or here, encoded
    c.drawString(100, 750, "Q3 Cyber Assessment - Nothing to see here.")
    c.save()
