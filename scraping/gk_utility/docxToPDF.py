# https://michalzalecki.com/converting-docx-to-pdf-using-python/
import sys
import subprocess
import re
import os
# import PyPDF2

# # path of the watermark pdf
# watermark_pdf_path = "~/gktoday/watermark.pdf"
# watermark_pdf_path = os.path.expanduser(watermark_pdf_path)


# def add_watermark(source_pdf_path):

#     src_file = open(source_pdf_path, 'rb')
#     src_file_reader = PyPDF2.PdfFileReader(src_file)
#     watermark_pdf = PyPDF2.PdfFileReader(open(watermark_pdf_path, 'rb'))

#     watermark_page = watermark_pdf.getPage(0)

#     # create a new empty PDF
#     result_pdf = PyPDF2.PdfFileWriter()

#     for num in range(1, src_file_reader.numPages):
#         page_obj = src_file_reader.getPage(num)
#         page_obj.mergePage(watermark_page)
#         result_pdf.addPage(page_obj)
    
#     src_file.close()
#     output = open(source_pdf_path, 'wb')
#     result_pdf.write(output)
#     output.close()

def convert_to(folder, source, timeout=None):
    args = [libreoffice_exec(), '--headless', '--convert-to', 'pdf', '--outdir', folder, source]
    process = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
    filename = re.search('-> (.*?) using filter', process.stdout.decode())

    if filename is None:
        raise LibreOfficeError(process.stdout.decode())
        
    else:
        # add_watermark(folder + name + ".pdf")
        return "Successfully converted docx file.\nSaved at: " + filename.group(1)


def libreoffice_exec():
    # TODO: Provide support for more platforms

    if sys.platform == 'darwin':
        return '/Applications/LibreOffice.app/Contents/MacOS/soffice'
    if sys.platform == 'win32':
        return 'C:/Program Files/LibreOffice/program/soffice'
    return 'libreoffice'


class LibreOfficeError(Exception):
    def __init__(self, output):
        self.output = output


if __name__ == '__main__':
    print('Converted to ' + convert_to(sys.argv[1], sys.argv[2]))
    # print(convert_to("./", "./test.docx"))
