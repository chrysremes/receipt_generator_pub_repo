import locale
import datetime
import re
import logging
from unidecode import unidecode
from fpdf import FPDF
from logging_and_debugging import get_log_filename

# constants for static strings
LOCAL = "MyCity-State"
HEADER = "My Name\nMy Job\nMy Subscription number"
FOOTER = "_______________________________________\nMy Full Name\nCPF: 000.000.000-00"

class Receipt():

    def __init__(self, name:str, cpf:str|int, value:float, date_services:list|tuple, sig_date:str=None) -> None:
        logging.info('Running __init__ for Receipt() instance.')
        self.name = name
        self.cpf = cpf
        self.value = value
        self.local = LOCAL
        self.date_services = date_services
        self.sig_date = sig_date


    def generate_br_date(self, custom_date:str = None)->str:
        """
        This function receives a date from DataFrame with default formatting and
        convert it to the format used on the Receipt. Notice that portuguese format is adopted.
        Example: 
        2020/12/21 is first transformed into 21/dez/2020, and then into '21 de dezembro de 2020'.
        Finally, if no data is given (None), then use 'today' date.
        """
        
        # sets the use of portuguese date format with utf-8
        locale.setlocale(locale.LC_ALL, 'pt_pt.UTF-8')

        # transform into 'dd/Mes/aaaa'
        if custom_date == None:
            # if no date was provided, use today
            date = datetime.date.today().strftime("%d/%m/%Y")
            date_br = datetime.datetime.strptime(date, '%d/%m/%Y').strftime('%d/%B/%Y')
            
        else:
            date_br = datetime.datetime.strptime(custom_date, "%d/%m/%Y").strftime('%d/%B/%Y')

        # return data transformed into 'dd de Mes de aaaa'
        return date_br.replace("/"," de ")

    def format_list_of_dates_br(self, dates_list:list|tuple)->list:

        logging.info('Running method format_list_of_dates_br.')

        # check for data consistence
        if not isinstance(dates_list,list|tuple):
            logging.error('Error: Invalid dates_list. dates_list is not list|tuple.')
            raise Exception(f"Datas {str(dates_list)} não é uma lista|tupla. Converter adequadamente.")

        # convert all dates from default to 'dd de Mes de aaaa' format
        datas_ast = []
        for data in dates_list:
            data_br = self.generate_br_date(data)
            datas_ast.append(data_br)

        return datas_ast
    
    def check_and_clean_cpf(self, cpf_xlsx:str)->str:
        """
        This function checks for CPF consistency and also format it in a proper standard.
        CPF is output in the format 'yyy.yyy.yyy-yy', once it has been validated.
        """

        logging.info('Running method check_and_clean_cpf.')

        # check for data consistence
        if not isinstance(cpf_xlsx,str):
            logging.error('Error: Invalid CPF. CPF is not a string.')
            raise Exception(f"CPF {str(cpf_xlsx)} não é uma string. Converter CPF para string.")

        # transform any cpf format to numbers-only
        cpf_numeros = re.sub("[^0-9]", "", cpf_xlsx)

        # check if cpf has 11 digits
        if not len(cpf_numeros)==11:
            logging.error('Error: Invalid CPF. CPF has not 11 digits.')
            raise Exception(f"CPF {str(cpf_numeros)} contém {str(len(cpf_numeros))} ao invés de 11 digitos. Verificar a entrada do CPF.")

        # once cpf is validated, now format/return it correctly as yyy.yyy.yyy-yy
        logging.info('CPF seems to be valid. Formatting and returning it now.')

        return "{}.{}.{}-{}".format(cpf_numeros[0:3],cpf_numeros[3:6],cpf_numeros[6:9],cpf_numeros[9:11])
    
    def format_value(self, valor:int)->str:
        """
        Replaces '.' (period) by ',' (comma) as a decimal separator for specific data on the DF (valor).
        """

        logging.info('Running method format_value - replace dot by comma.')
        
        return '{0:.2f}'.format(valor).replace('.',',')
    
    def generate_main_string(self)->tuple:
        """
        This function will generate a tuple of strings that will fill the pdf receipt.
        """

        logging.info('Running method generate_main_string.')

        self.cpf = self.check_and_clean_cpf(self.cpf)
        self.value = self.format_value(self.value)
        self.date_services = self.format_list_of_dates_br(self.date_services)
        self.sig_date = self.generate_br_date(self.sig_date)
        signature_local_and_date = self.local+", "+self.sig_date+"."

        full_string = f'''
        Recebi de {self.name}, inscrito(a) no CPF sob o n. {self.cpf}, a importância de R$ {self.value} referente aos serviços de atendimento psicológico, ocorrido(s) na modalidade online na(s) seguinte(s) data(s):
        '''
        
        # check how many columns are needed and initialize them all with empty string ''
        full_dates = []
        n_of_columns = (len(self.date_services) // 3) + 1
        for idx in range(0,n_of_columns):
            full_dates.insert(idx,'')
        
        # make a matrix of strings containing formated dates, in proper columns (col) and lines (line)
        count_line = 0
        col = 0
        logging.info(f'We are writting on col = {col}, row = {count_line} for the dates-string.')
        for data in self.date_services:
            full_dates[col] = full_dates[col]+data+';\n'
            count_line = count_line+1
            if (count_line >= 3):
                count_line = 0
                col = col+1
        logging.info(f'We finished writting on col = {col}, row = {count_line} for the dates-string.')
        
        # return properly formated strings in a tuple
        return (full_string, full_dates, signature_local_and_date)

    def generate_filename(self, name:str)->str:
        """
        Generates an appropriate filename, containing only alphanumeric chars.
        """
        logging.info('Running method generate_filename.')
        
        # unidecode removes accents, and re.sub first replaces " " by "_", and then removes all remaining non-alphanumeric
        pdf_sub_filename = re.sub(' ', '_', unidecode(name))
        pdf_sub_filename = re.sub('[^a-zA-Z0-9_ \n\.]', '', pdf_sub_filename)

        logging.info(f'pdf_sub_filename = {pdf_sub_filename}.')
        
        #return pdf filename
        return ("recibo_"+pdf_sub_filename+".pdf")

    def generate_pdf(self)->None:
        """
        Generates pdf files by using FPDF lib.
        Strings that fill the pdf file are previously treated by appropriate methods.
        """

        logging.info('Running method generate_pdf.')

        main_string = self.generate_main_string()
        
        pdf = FPDF(orientation='L',unit='mm',format='A4')

        logging.info('Setting Margins, Page and Font.')
        pdf.set_margins(left=20,top=20,right=20)
        pdf.add_page()
        pdf.set_font('Times', '', 18)

        logging.info('Printing the HEADER and RECIBO.')
        pdf.multi_cell(w=0, h=8, txt=HEADER, align='C')
        pdf.ln(10)

        pdf.set_font('Times', 'B', 22)
        pdf.cell(w=0, h=8, txt="RECIBO", align='C')
        pdf.ln(24)

        logging.info('Printing the "main string".')
        pdf.set_font('Times', '', 16)
        pdf.multi_cell(w=0, h=8, txt=main_string[0], align='J')

        logging.info('Printing the DATES in their columns.')
        idx = 0
        current_y = pdf.get_y()-8
        for main_str_cols in main_string[1]:
            pdf.set_xy(x=40+80*idx,y=current_y)
            pdf.multi_cell(w=0, h=8, txt=main_str_cols, align='J')
            idx = idx +1

        logging.info('Printing the Location+Date for main string and FOOTER.')
        pdf.set_y(current_y+32)
        pdf.cell(w=0, h=10, txt=main_string[2], align='C')
        pdf.ln(30)

        pdf.multi_cell(w=0, h=8, txt=FOOTER, align='C')
        
        logging.info('Generate PDF filename.')
        pdf_filename = self.generate_filename(self.name)

        logging.info('Output final PDF file.')
        pdf.output(pdf_filename)
