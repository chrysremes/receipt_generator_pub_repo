import logging
import pandas as pd
import warnings
from datetime import datetime

COL_NAME_ATENDIMENTOS = "Data_Atendimentos"
COL_UNNAMED = "Unnamed:"

class ReceiptData():
    
    def __init__(self) -> None:
        logging.info('Running __init__ for ReceiptData() instance.')
        self.df = None
        self.atendimento_cols = None

    def read_xlsx(self, filename:str, sheet_name:str) -> None:
        """
        This function ingests all data from the xlsx file into a pandas DataFrame.
        Also, it organizes the columns with "atendimentos", since they can be of variable size.
        """
        
        # ignore warnings about Validation Cells that are on the spreadsheet
        warnings.simplefilter(action='ignore', category=UserWarning)
        try:
            # read xlsx into a dataframe
            self.df = pd.read_excel(filename,sheet_name=sheet_name,index_col=0,na_filter=True,engine="openpyxl")
        except:
            # raise an Error if unsucessful
            logging.error(f'ERROR: There was something wrong while reading the xlsx {filename} file.')
            raise Exception(f"ERROR: There was something wrong while reading the xlsx {filename} file.")
        
        # reset warnings so other warnings can be displayed
        warnings.resetwarnings()
        # reset indexes
        self.df = self.df.reset_index()

        # Get date columns related to "Atendimentos" (all named as in COL_NAME_ATENDIMENTOS or COL_UNNAMED)
        logging.info('Getting the atendimento_cols.')
        self.atendimento_cols = [col for col in list(self.df.columns) if COL_UNNAMED in col]
        self.atendimento_cols.insert(0,COL_NAME_ATENDIMENTOS)
    
    def convert_receipt_date(self, receipt_date:datetime)->str|None:
        """
        This verifies if a Signature/Receipt Date is set on Data.
        If set, then convert it to right format and use it.
        Else, then return it as "None" so later "today" can be used.
        """

        # Verify if signature/receipt date is null and treat it accordingly
        if (pd.isnull(receipt_date)):
            logging.info("Signature date is empty. Returning it as None so 'today' can be used.")
            receipt_date = None
        else:
            logging.info("Signature date is not empty. Converting to '%d/%m/%Y' format.")
            receipt_date = receipt_date.strftime('%d/%m/%Y')
        
        return receipt_date

    def convert_services_date(self, services_dates_raw:list)->list:
        """
        This get a raw list of dates (Atendimentos) and create a new list of treated dates.
        """

        services_dates = []
        for service_date in services_dates_raw:
            if (pd.isnull(service_date)):
                pass
            else:
                services_dates.append(service_date.strftime('%d/%m/%Y'))
        
        return services_dates
        
    