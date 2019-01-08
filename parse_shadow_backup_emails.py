import re
from datetime import datetime
import json
import glob
import os

class email_files:
    @staticmethod
    def get_list_of_files(pattern):
        return glob.glob(pattern)

class parse_shadow_backup_emails:
    subjects = []
    split_subjects = []
    unique_subjects = {}
    dictionary_file = 'subjects.json'

    def __init__(self, directory):
        self.list_of_email_files = email_files.get_list_of_files(directory)

    def get_subjects(self):
        for email in self.list_of_email_files:
            with open(email) as f:
                file_data = f.readlines()
                self.get_match_and_next_line("^Subject:", file_data)
                f.closed
#            os.rename(email, "processed/" + email.replace("/tmp/save/", ''))
#            os.remove(email)
        return self.subjects

    def get_match_and_next_line(self, pattern, file_data):
        for line_number, line in enumerate(file_data):
            if re.search("^From", line) and line_number == 1:
                from_date = "| " + line
            if re.search(pattern, line):
                subject = line.rstrip() + " " + file_data[line_number + 1].rstrip() + " " + from_date.rstrip()
                self.subjects.append(subject)

    def split_subject(self, subjects):
        for subject in subjects:
            split_subject = subject.split('|')
            self.split_subjects.append(self.create_dictionary(split_subject))

    def create_dictionary(self, split_subject):
        if len(split_subject) == 7:
            subject_dictionary = {
                'server': str(split_subject[0].strip().replace('Subject: ', '')),
                'client': str(split_subject[1].strip()),
                'company': str(split_subject[2].strip()),
                'backup_code': str(self.get_backup_code(split_subject[5].strip())),
                'email_date': str(self.get_email_time(split_subject[-1].strip()))
            }
            return subject_dictionary

    def build_unique_dictionary(self):
        split_subjects = list(filter(None.__ne__, self.split_subjects))
        for subject in split_subjects:
            key = subject['server'] + '-' + subject['client'] + '-' + subject['company']
            if key not in self.unique_subjects:
                self.unique_subjects[key] = subject
            elif key in self.unique_subjects:
                print('duplicate ' + key + ' ' + subject['email_date'])
#        print(self.unique_subjects)


    def save_dictionary(self):
        if not os.path.isfile(self.dictionary_file):
            self.save_json(self.dictionary_file)

    def save_json(self, file_name):
        with open(file_name, 'w') as fp:
            json.dump(self.split_subjects, fp)

    @staticmethod
    def load_json(file_name):
        with open(file_name, 'r') as fp:
            return json.load(fp)

    @staticmethod
    def get_backup_code(raw_code):
        backup_code = raw_code.split()
        return backup_code[1].strip("'")

    @staticmethod
    def get_email_time(raw_email_time):
        email_time_list = raw_email_time.split()
        email_time = email_time_list[-4] + ' ' + email_time_list[-3] + ' ' + email_time_list[-2] + ' ' + email_time_list[-1]
        #        datetime_object = datetime.strptime(email_time, '%b %d %H:%M:%S %Y')
        return email_time
