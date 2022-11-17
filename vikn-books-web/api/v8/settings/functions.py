import string
import random
from django.http import HttpResponse
from decimal import Decimal
from django.db.models import Max
import xlwt
from brands import models
import datetime
from pytz import timezone
from io import BytesIO, StringIO
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.http import HttpResponse
from PyPDF2 import PdfFileMerger
import re
from xlwt import Workbook, XFStyle, Borders, Pattern, Font, easyxf, Alignment


def generate_serializer_errors(args):
    message = ""
    for key, values in args.items():
        error_message = ""
        for value in values:
            error_message += value + ","
        error_message = error_message[:-1]

        message += "%s : %s | " % (key, error_message)
    return message[:-3]


def get_auto_id(model, BranchID):
    SettingsID = 1
    max_value = None
    SettingsID = None
    # latest_auto_id =  model.objects.all().order_by("-CreatedDate")[:1]
    latest_auto_id = model.objects.all().aggregate(Max('SettingsID'))

    if model.objects.filter(BranchID=BranchID).exists():
        max_value = model.objects.filter(
            BranchID=BranchID).aggregate(Max('SettingsID'))

    if max_value:
        max_settingsId = max_value.get('SettingsID__max', 0)
        SettingsID = max_settingsId + 1
    else:
        SettingsID = 1

    return SettingsID


def create_or_update_user_type_settings(User, CompanyID, BranchID, GroupName, SettingsType, SettingsValue, UserType):
    today = datetime.datetime.now()
    Action = "A"
    if not models.UserTypeSettings.objects.filter(CompanyID=CompanyID, GroupName=GroupName, SettingsType=SettingsType, UserType=UserType).exists():
        models.UserTypeSettings.objects.create(
            UserType=UserType,
            CompanyID=CompanyID,
            GroupName=GroupName,
            SettingsType=SettingsType,
            SettingsValue=SettingsValue,
            BranchID=BranchID,
            CreatedDate=today,
            UpdatedDate=today,
            CreatedUserID=User,
            UpdatedUserID=User,
            Action=Action
        )
    elif not models.UserTypeSettings.objects.filter(CompanyID=CompanyID, GroupName=GroupName, SettingsType=SettingsType, UserType=UserType, SettingsValue=SettingsValue).exists():
        Action = "M"
        instance = models.UserTypeSettings.objects.get(
            CompanyID=CompanyID,
            BranchID=BranchID,
            GroupName=GroupName,
            SettingsType=SettingsType,
            UserType=UserType,
        )
        instance.SettingsValue = SettingsValue
        instance.UpdatedDate = today
        instance.UpdatedUserID = User
        instance.Action = Action
        instance.save()
    else:
        pass


def get_user_type_settings(CompanyID, BranchID, SettingsType, UserType):
    value = False
    if models.UserTypeSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType=SettingsType, UserType=UserType).exists():
        try:
            value = models.UserTypeSettings.objects.get(
                CompanyID=CompanyID, BranchID=BranchID, SettingsType=SettingsType, UserType=UserType).SettingsValue
        except:
            value = models.UserTypeSettings.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, SettingsType=SettingsType, UserType=UserType)[0].SettingsValue
        if value == "True":
            value = True
        elif value == "False":
            value = False
    return value


def render_to_pdf(template, context={},no_of_page=1):
    # style
    orientation = "portrait"
    papersize = "A4"
    margins = "0"
  
    header = "<!DOCTYPE html>\n<html>\n<head>"
    header += '<style>'
    header += '@page {size: %s %s; margin: %s}' % ( papersize, orientation, margins )
    header += '</style>' 
    header += "</head><body>"
    footer = "</body></html>"
    # style ends

    template = get_template(template)
    html  = template.render(context)
    result = BytesIO()
    pdf = pisa.pisaDocument(StringIO(header + html + footer), dest=result)
    # to generate multiple copies of pdf
    merger = PdfFileMerger()
    for i in range(no_of_page):
        merger.append(result)
    output = BytesIO()
    merger.write(output)
    # multiple copies ends here
    if not pdf.err:
        return HttpResponse(output.getvalue(), content_type='application/pdf')
    return None


def html_to_pdf_pisa(dbo, htmldata):
    """
    Converts HTML content to PDF and returns the PDF file data as bytes.
    NOTE: wkhtmltopdf is far superior, but this is a pure Python solution and it does work.
    """
    # Allow orientation and papersize to be set
    # with directives in the document source - eg: <!-- pdf orientation landscape, pdf papersize letter -->
    orientation = "portrait"
    # Sort out page size arguments
    papersize = "A4"
    # if htmldata.find("pdf orientation landscape") != -1: orientation = "landscape"
    # if htmldata.find("pdf orientation portrait") != -1: orientation = "portrait"
    # if htmldata.find("pdf papersize a5") != -1: papersize = "A5"
    # if htmldata.find("pdf papersize a4") != -1: papersize = "A4"
    # if htmldata.find("pdf papersize a3") != -1: papersize = "A3"
    # if htmldata.find("pdf papersize letter") != -1: papersize = "letter"
    # # Zoom - eg: <!-- pdf zoom 0.5 end -->
    # # Not supported in any meaningful way by pisa (not smart scaling)
    # # zm = regex_one("pdf zoom (.+?) end", htmldata)
    # # Margins, top/bottom/left/right eg: <!-- pdf margins 2cm 2cm 2cm 2cm end -->
    margins = "0"
  
    header = "<!DOCTYPE html>\n<html>\n<head>"
    header += '<style>'
    header += '@page {size: %s %s; margin: %s}' % ( papersize, orientation, margins )
    header += '</style>' 
    header += "</head><body>"
    footer = "</body></html>"
    # htmldata = htmldata.replace("font-size: xx-small", "font-size: 6pt")
    # htmldata = htmldata.replace("font-size: x-small", "font-size: 8pt")
    # htmldata = htmldata.replace("font-size: small", "font-size: 10pt")
    # htmldata = htmldata.replace("font-size: medium", "font-size: 14pt")
    # htmldata = htmldata.replace("font-size: large", "font-size: 18pt")
    # htmldata = htmldata.replace("font-size: x-large", "font-size: 24pt")
    # htmldata = htmldata.replace("font-size: xx-large", "font-size: 36pt")
    # Remove any img tags with signature:placeholder/user as the src
    htmldata = re.sub(r'<img.*?signature\:.*?\/>', '', htmldata)
    # Fix up any google QR codes where a protocol-less URI has been used
    htmldata = htmldata.replace("\"//chart.googleapis.com", "\"http://chart.googleapis.com")
    # Switch relative document uris to absolute service based calls
    # Do the conversion
    out = BytesIO()
    pdf = pisa.pisaDocument(StringIO(header + htmldata + footer), dest=out)
    if pdf.err:
        raise IOError(pdf.err)
    return out.getvalue() 


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_country_time(date,country="Saudi Arabia"):
    if country == 'India':
        invoice_time = date.astimezone(timezone('Asia/Kolkata'))
    elif country == 'Saudi Arabia':
        invoice_time = date.astimezone(timezone('Asia/Riyadh'))
    elif country == 'Kuwait':
        invoice_time = date.astimezone(timezone('Asia/Kolkata'))
    elif country == 'Oman':
        invoice_time = date.astimezone(timezone('Asia/Kolkata'))
    elif country == 'United Arab Emirates':
        invoice_time = date.astimezone(timezone('Asia/Kolkata'))
    elif country == 'Qatar':
        invoice_time = date.astimezone(timezone('Asia/Kolkata'))


    invoice_time = invoice_time.strftime('%I:%M %p')
    return invoice_time

