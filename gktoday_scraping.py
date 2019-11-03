import requests
import json
import os
from datetime import datetime
import docx
from ast import literal_eval
import docxToPDF
import re
import logging
from datetime import datetime as dt


## GLOBALS ##
# Log file path
LOG_PATH = '~/gktoday/log/'
LOG_PATH = os.path.expanduser(LOG_PATH)
# PATHS for saving docx,pdf files
quiz_folder = "~/gktoday/res/quiz/"
docx_folder = "docx/"
pdf_folder = "pdf/"
# TO expand the "~/ path"
quiz_folder = os.path.expanduser(quiz_folder)
# GKToday APIs
all_quiz_URL = 'https://www.gktoday.in/wp-json/wp/v2/quizByCategory/18'
quiz_url = 'https://www.gktoday.in/wp-json/wp/v2/quiz/'         # append id of the specific quiz
all_files_metadata = {}


logging.basicConfig(filename=LOG_PATH+"scraping.log", level=logging.DEBUG)


def insert_char(string, index, num):
    return string[:index] + str(num) + '.' + string[index:]

def make_directories():
    # to create the folder for docx and pdf files if they doesn't exist already
    try:
        os.makedirs(quiz_folder + "docx/", exist_ok=True)
        os.makedirs(quiz_folder + "pdf/", exist_ok=True)
        os.makedirs(LOG_PATH, exist_ok=True)
        return 1
    except:
        print("Error while making docx, pdf directories.")
        return 0

def write_metadata(data):
    try:
        os.makedirs(quiz_folder, exist_ok=True)
        f = open(quiz_folder+"quiz_metadata.txt", "w")
        f.write(data)
        f.close()

    except:
        print("Error occured in write_metadata() at", dt.now())
        logging.exception("Error while writing to \"quiz_metadata.txt\" in write_metadata()")
        raise

def convert_to_pdf(docx_file_name, docx_path):
    try:
        docxToPDF.convert_to(quiz_folder + "pdf/", docx_path)

    except:
        print("Error occured in convert_to_pdf() at", dt.now())
        logging.exception('Error In convert_to_pdf()')
        raise

# string cleanup / remove errors caused by ' or \" or \'
def l_eval(string):
    try:
        return literal_eval("'%s'" %"".join(string.splitlines()))
    except SyntaxError:
        string = string.replace("'",r"\'")
        return literal_eval("'%s'" %"".join(string.splitlines()))

# Regex to extract Year and Month from the String
def get_year_month(name):
    try:
        year_re = r'\d{4}'
        month_re = r'\b[a-zA-Z]*\b ?$'
        yr = re.findall(year_re,name)[0]
        mth = re.findall(month_re,name)[0]
        mth = mth.rstrip()
        return yr,mth

    except:
        print("Error occured in get_year_month() at", dt.now())
        logging.exception('Error In get_year_month()')
        raise

# get all quiz metadata from server and store required details in all_files_metadata dictonary
def get_quiz_metadata_from_server():

    try:
        # fetch the JSON file containing all details of monthly Quiz
        r = requests.get(all_quiz_URL)
        all_quiz_json = json.loads(r.content.decode())

        # retrieve the Name and Id of Each Month's Quiz 
        count = 0
        for quiz_json in all_quiz_json:
            count += 1
            name = quiz_json['quiz_name'].replace('Current Affairs - ','')

            year,month = get_year_month(name)

            name = year+"-"+month   #remove whitespace fom name
            name = insert_char(name, 0, count)  # add number to the name

            pdf_file_path = quiz_folder + "pdf/" + name + ".pdf"

            # add current quiz details to the all_files_metadata dictionary
            if(not (year in all_files_metadata)):
                all_files_metadata[year] = {}
            all_files_metadata[year][month] = { "id":quiz_json['id'], "file_name" : name, "file_path" : pdf_file_path }

        # Write files metadata to txt file
        write_metadata(json.dumps(all_files_metadata))

    except:
        print("Error occured in get_quiz_metadata_from_server() at", dt.now())
        logging.exception('Error In get_quiz_metadata_from_server()')
        raise

# fetch all monthly quiz from server
def get_quiz_from_server():

    try:

        if(make_directories()): # if there is no error while creating the directories
            dict_map = {'1': '(a)', '2': '(b)', '3': '(c)', '4': '(d)'}
            for _year,_year_val in all_files_metadata.items():
                for _month,_month_val in _year_val.items(): 
                    _id = _month_val['id']
                    _name = _month_val['file_name']
                    doc = docx.Document()   # open document
                    quiz_url_cur = quiz_url + _id
                    # print(_id, "-", _month)   # this for checking progress of the script. not necessary during the cronjob
                    res = requests.get(quiz_url_cur)
                    all_ques = json.loads(res.content.decode())
                    question_counter = 0
                    for que in all_ques:
                        question_counter += 1
                        # cleaning data
                        ques    = l_eval(que['question'])
                        opt1    = l_eval(que['option1'])
                        opt2    = l_eval(que['option2'])
                        opt3    = l_eval(que['option3'])
                        opt4    = l_eval(que['option4'])
                        ans_exp = l_eval(que['ans_explanation'])

                        # Write Current Question to the Document
                        p = doc.add_paragraph('')
                        p.add_run('Question ' + str(question_counter) + ': ').bold = True
                        p.add_run(ques + '\n' + '(a) ' + opt1 + '\n' + '(b) ' + opt2 + '\n' + '(c) ' + opt3 + '\n' + '(d) ' + opt4 + '\n')
                        p.add_run( 'Answer: ' + dict_map[que['answer']] + '\n' + 'Answer Explanation: ').bold = True
                        p.add_run(ans_exp).italic = True
                        p.add_run('\n\n')


                    docx_file_name = _name + '.docx'
                    docx_path = quiz_folder + "docx/" + docx_file_name
                    # save the docx file at the path specified by docx_path

                    doc.save(docx_path)
                    convert_to_pdf(docx_file_name,docx_path)
    except:
        print("Error occured in get_quiz_from_server() at", dt.now())
        logging.exception('Error In get_quiz_from_server()')
        raise

if(__name__ == "__main__"):
    try:
        get_quiz_metadata_from_server()
        get_quiz_from_server()
        print(dt.now())
        print("scraping successfull!")

    except:
        print("Error occured in __main__ at", dt.now())
        logging.exception('\n\nError In __main__')
        raise