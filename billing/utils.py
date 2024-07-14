# billing/utils.py
import logging
from io import BytesIO
from django.core.files.base import ContentFile
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from .models import Invoice

logger = logging.getLogger(__name__)

def generate_invoice_pdf(bill):
    try:
        invoice_html = render_to_string('billing/invoice_template.html', {'bill': bill})
        pdf = BytesIO()
        pisa_status = pisa.CreatePDF(invoice_html, dest=pdf)
        if pisa_status.err:
            logger.error(f"PDF generation error for Bill ID {bill.id}: {pisa_status.err}")
            return None
        pdf_content = pdf.getvalue()
        invoice = Invoice(user=bill.user, bill=bill)
        invoice.pdf.save(f'invoice_{bill.id}.pdf', ContentFile(pdf_content))
        invoice.save()
        return invoice
    except Exception as e:
        logger.error(f"Error generating PDF for Bill ID {bill.id}: {e}")
        return None
