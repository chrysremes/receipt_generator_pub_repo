import logging
from logging_and_debugging import get_log_filename, remove_old_log_lines

def main()->None:
    """
    This is the main() function to generate receipts from excel data
    """

    # constants with the xlsx file name and sheet name
    XLSX_FILE = "Planilha_Cadastro_Recibos.xlsx"
    SHEET_NAME = "Recibos"
    
    print("Executando Gerador de Recibos")
    logging.info('=========================== STARTING NEW LOGGING. ===========================')
    logging.info('Started main() from "gerar_recibos_pdf.py"')

    from organize_data_class import ReceiptData
    from make_receipt_class import Receipt

    # make an instance of ReceiptData to read the xlsx file
    receipt_data = ReceiptData()
    receipt_data.read_xlsx(XLSX_FILE,SHEET_NAME)
    logging.info('File read method for xlsx has been executed.')
    
    # start to iterate through the read DataFrame, row by row via iterrows()
    for _, row in receipt_data.df.iterrows():

        # make suitable convertions on dates
        logging.info(f'######### STARTING NEW ITERATION : Receipt for {row["Nome"]}. #########')
        sig_date = receipt_data.convert_receipt_date(row['Data_Recibo'])
        services_dates = receipt_data.convert_services_date(row[receipt_data.atendimento_cols].to_list())
        logging.info('Data read finished.')

        #check if a receipt should be generated - 'S' (yes) or 'N' (no)
        if (row['Gerar_Recibo'] == 'S'):
            
            # make an instance of the Receipt with previously read data
            logging.info('generate_receipt_flag has been marked with "S".')
            my_receipt = Receipt(
                name=row['Nome'],
                cpf=row['CPF'],
                value=row['Valor_Total'],
                date_services=services_dates,
                sig_date=sig_date
            )

            # make the pdf with the Receipt method
            my_receipt.generate_pdf()
            logging.info('Method "generate_pdf()" has been executed.')

        elif (row['Gerar_Recibo'] == 'N'):
            
            # don't generate a receipt, just logging for debugging purposes
            logging.info('generate_receipt_flag has been marked with "N".')
        else:

            # incorrect data from xlsx: don't generate a receipt, and log an error
            logging.error('Invalid data on column "Gerar_Recibo" generated an unexpected response.')
        
        logging.info('--------- ENDING ITERATION. ----------')
    
    print("Execução bem sucedida!")
    logging.info('=============== END EXECUTION ==============')

if __name__ == '__main__':
    
    # get current py file name to generate log-file - and create the log file
    log_filename = get_log_filename(__file__)
    
    # remove old lines from log file
    remove_old_log_lines(log_filename)  

    # config current logging session
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',filename=log_filename, encoding='utf-8', level=logging.DEBUG)
    
    # call main() function
    main()