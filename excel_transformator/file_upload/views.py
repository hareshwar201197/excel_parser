
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render

from .models import Companies, Lob, Categories
import pandas as pd
import io
import xlsxwriter
import urllib.parse
import urllib.request


def file_cleaning(request):
    if request.method == 'POST':
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return JsonResponse({'status': 'error', 'message': 'No file uploaded'})

        try:
            # get the required columns
            required_columns = Lob.objects.all().first().lob
            insurers_list = list(Companies.objects.all().values())
            # Extract all the insurer names from the list
            insurers = [insurer['insurer'].lower() for insurer in insurers_list]

            # Load the uploaded Excel file
            excel_file = pd.ExcelFile(uploaded_file)
            extracted_data = []  # To store data from all sheets

            # Iterate for Excel sheet file
            for sheet_name in excel_file.sheet_names:
                data = excel_file.parse(sheet_name, header=1)
                if 'Unnamed: 0' in data.columns:
                    data = data.rename(columns={'Unnamed: 0': 'empty_col'})
                available_columns = [col for col in required_columns if col in data.columns]
                if not available_columns:
                    continue

                # Select only the first column and the required columns
                columns_to_select = ['empty_col'] + available_columns  # Assuming the first column is unnamed (could be adjusted if it's named)
                data = data[columns_to_select]

                # Filter rows where 'empty_col' matches any insurer in the insurers list
                insurers_data = data[data['empty_col'].str.lower().isin(insurers)]

                # Perform data cleaning
                insurers_data = insurers_data.dropna(how='all')  # Remove rows with all NaN values
                insurers_data = insurers_data.fillna('Unknown')  # Replace NaN with 'Unknown'

                # Convert DataFrame to a list of dictionaries
                cleaned_data = insurers_data.to_dict(orient='records')
                extracted_data.append(cleaned_data)
            excel_data = download_excel(extracted_data, insurers_list)
            filename = 'Output_file.xlsx'
            response = HttpResponse(content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename=' + urllib.parse.quote_plus(
                filename.encode('utf-8'),
                safe=':/'.encode('utf-8'))
            response.write(excel_data)
            return response
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    # If it's a GET request, render the upload form
    return render(request, 'upload_file.html')



def download_excel(extracted_data, insurers_list):
    headers = ["Year", "Month", "category", "clubbed_name", "Product", "Value"]
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    header_format = workbook.add_format({
        'bold': True,
        'color': 'black',
        'align': 'center',
        'valign': 'center',
        'font_size': 10,
        'border': 1
    })
    header_format.set_text_wrap()
    text_format = workbook.add_format({
        'font_size': 10,
        'bold': True,
        'border': 0,
        'align': 'left',
        'font_name': 'Arial'
    })
    text_format.set_text_wrap()
    worksheet = workbook.add_worksheet(name='OutputFile')

    data_list = excel_json_data(extracted_data, insurers_list)

    col_index = 0
    row_index = 0
    while col_index < len(headers):
        worksheet.write(row_index, col_index, headers[col_index], header_format)
        col_index = col_index + 1
    row_index = row_index + 1

    for data_dict in data_list:
        worksheet.write(row_index, 0, ' ', text_format)
        worksheet.write(row_index, 1, ' ', text_format)
        worksheet.write(row_index, 2, data_dict.get('category'), text_format)
        worksheet.write(row_index, 3, data_dict.get('clubbed_name'), text_format)
        worksheet.write(row_index, 4, data_dict.get('name'), text_format)
        worksheet.write(row_index, 5, ' ', text_format)
        row_index = row_index + 1
    workbook.close()
    return output.getvalue()


def excel_json_data(extracted_data, insurers_list):
    clubbed_names = list(map(lambda x: x['clubbed_name'], insurers_list))
    final_list = extracted_data[0] + extracted_data[1]
    categories = list(Categories.objects.filter(clubbed_name__in=clubbed_names).values())
    data_list = list()
    for extract_dict in final_list:
        data_dict = dict()
        for insurer_dict in insurers_list:
            if extract_dict.get('empty_col') in insurer_dict.values():
                data_dict.update({
                    'clubbed_name': insurer_dict.get('clubbed_name'),
                    'name': extract_dict.get('empty_col')
                })
        data_list.append(data_dict)
    for cat in data_list:
        for category in categories:
            if cat.get('clubbed_name') in category.values():
                cat.update({
                    'category': category.get('category')
                })
    sorted_data = sorted(data_list, key=lambda x: x['clubbed_name'])
    return sorted_data