import json
import os
from scraping import quiz_folder, magazine_folder, app_folder


quiz_folder = os.path.expanduser(quiz_folder)
magazine_folder = os.path.expanduser(magazine_folder)
app_folder = os.path.expanduser(app_folder)
app_metadata = {}


# app_metadata.json layout
'''
.
└───Magazine
│   └───2020
│   │   └───January
│   │   └───February
│   └───2019
│       └───December
│       └───November
│           └───file_path
│               └───c:/Users/username/gktoday/pdf/11. November, 2019.pdf
└───Quiz
│   └───Monthly Quiz PDF
│   │   └───2020
│   │   │   └───January
│   │   │   └───February
│   │   └───2019
│   │       └───November
│   │       └───December
│   └───15 Days Quiz PDF
│       └───2020
│       │   └───January
│       │   └───February
│       └───2019
│           └───December
│           └───November
'''


# write app_metadata to disk
def write_app_md_to_disk():
    app_md_path = app_folder + "app_metadata.json"
    os.makedirs(app_folder, exist_ok=True)
    app_file = open(app_md_path, 'w')
    app_file.write(json.dumps(app_metadata))
    app_file.close()


# copy relevant quiz data to app_metadata file
def copy_quiz_data(md_file):
    global app_metadata
    app_metadata['Quiz'] = {}
    md_file = md_file['current_affairs']
    for quiz_type, quiz_type_value in md_file.items():

        if quiz_type == "monthly":
            app_metadata['Quiz']['Monthly Quiz PDF'] = {}
            for year, year_value in quiz_type_value.items():
                app_metadata['Quiz']['Monthly Quiz PDF'][year] = {}
                for month, month_value in year_value.items():
                    app_metadata['Quiz']['Monthly Quiz PDF'][year][month] = month_value['pdf_file_path']

        elif quiz_type == "fortnight":
            app_metadata['Quiz']['15 Days Quiz PDF'] = {}
            for year, year_value in quiz_type_value.items():
                app_metadata['Quiz']['15 Days Quiz PDF'][year] = {}
                for month, month_value in year_value.items():
                    for dt, dt_value in month_value.items():
                        file_name = dt + "," + month
                        app_metadata['Quiz']['15 Days Quiz PDF'][year][file_name] = dt_value['pdf_file_path']

    write_app_md_to_disk()


# copy relevant magazine data to app_metadata file
def copy_magazine_data(md_file):
    app_metadata['Magazine'] = {}
    for year, year_value in md_file.items():
        app_metadata['Magazine'][year] = {}
        for month, month_value in year_value.items():
            file_name = month_value['file_name']
            app_metadata['Magazine'][year][file_name] = month_value['file_path']
    write_app_md_to_disk()


# this function will write relevant metadata from quiz & magazine metadata files
def init_app_metadata():

    quiz_md_path = quiz_folder + "all_files_metadata.json"
    magazine_md_path = magazine_folder + "all_files_metadata.json"

    quiz_file = open(quiz_md_path, 'r')
    quiz_md = json.loads(quiz_file.read())
    quiz_file.close()
    copy_quiz_data(quiz_md)

    magazine_file = open(magazine_md_path, 'r')
    magazine_md = json.loads(magazine_file.read())
    magazine_file.close()
    copy_magazine_data(magazine_md)

