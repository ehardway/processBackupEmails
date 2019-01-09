import re
from datetime import datetime
import json
import glob
import os


class email_files:
    @staticmethod
    def get_list_of_files(pattern):
        return glob.glob(pattern)


class parseShadowBackupEmails:
    subjects = []
    split_subjects = []
    active_email_dictionary = {}
    dictionary_file = 'email_dictionary.json'
    master_email_dictionary = {}
    change_count = 0
    backup_code_1120 = []
    backup_code_1121 = []

    def __init__(self, directory):
        self.list_of_email_files = email_files.get_list_of_files(directory)

    def check_for_shadow_email(self):
        for email in self.list_of_email_files:
            with open(email) as f:
                if 'ShadowProtectSvc' not in f.read():
                    self.list_of_email_files.remove(email)

    def get_subjects(self):
        self.check_for_shadow_email()
        for email in self.list_of_email_files:
            with open(email) as f:
                file_data = f.readlines()
                self.get_match_and_next_line("^Subject:", file_data)
                f.closed
                os.remove(email)
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
                'email_time': str(self.get_email_time(split_subject[-1].strip()))
            }
            return subject_dictionary

    def build_unique_active_dictionary(self):
        split_subjects = list(filter(None.__ne__, self.split_subjects))
        for subject in split_subjects:
            key = subject['company'] + subject['server'] +  subject['client']
            if key not in self.active_email_dictionary:
                self.active_email_dictionary[key] = subject
            elif key in self.active_email_dictionary:
                datetime_object_in_dict = datetime.strptime(self.active_email_dictionary[key]['email_time'],
                                                            '%b %d %H:%M:%S %Y')
                datetime_object = datetime.strptime(subject['email_time'], '%b %d %H:%M:%S %Y')
                if datetime_object > datetime_object_in_dict:
                    self.active_email_dictionary[key] = subject
        self.initialize_dictionary()

    def compare_master_and_active_dictionaries(self):
        for key, email_data in self.active_email_dictionary.items():
            if key not in self.master_email_dictionary:
                self.master_email_dictionary[key] = email_data
                self.change_count += 1
            elif key in self.master_email_dictionary:
                datetime_object_in_master_dict = datetime.strptime(self.master_email_dictionary[key]['email_time'],
                                                                   '%b %d %H:%M:%S %Y')
                datetime_object = datetime.strptime(email_data['email_time'], '%b %d %H:%M:%S %Y')
                if datetime_object > datetime_object_in_master_dict:
                    self.master_email_dictionary[key] = email_data
                    self.change_count += 1
        if self.change_count > 0:
            print("Something Change Updating Dictionary on disk")
            self.save_json(self.master_email_dictionary, self.dictionary_file)
    #        print(len(self.master_email_dictionary.keys()))
    #        print(len(self.active_email_dictionary.keys()))

    def generate_html_table(self):
        self.sort_master_dictionary()
        # Need to come up with unknown status
        # also need to add a threshold somewhere

    def sort_master_dictionary(self):
        self.backup_code_1120 = []
        self.backup_code_1121 = []
        for key, data in sorted(self.master_email_dictionary.items()):
            if data['backup_code'] == "1120":
                self.backup_code_1120.append(data)
            elif data['backup_code'] == "1121":
                self.backup_code_1121.append(data)


    def load_master_dictionary(self):
        if os.path.isfile(self.dictionary_file):
            self.master_email_dictionary = self.load_json(self.dictionary_file)

    def initialize_dictionary(self):
        if not os.path.isfile(self.dictionary_file):
            print("Initializing Dictionary on Disk")
            self.save_json(self.active_email_dictionary, self.dictionary_file)

    @staticmethod
    def save_json(data, file_name):
        with open(file_name, 'w') as fp:
            json.dump(data, fp)

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
        email_time = email_time_list[-4] + ' ' + email_time_list[-3] + ' ' + email_time_list[-2] + ' ' + \
                     email_time_list[-1]
        return email_time
