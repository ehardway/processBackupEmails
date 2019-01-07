import glob
import re

class email_files:

    @staticmethod
    def get_list_of_files(pattern):
        return glob.glob(pattern)

class parse_shadow_backup_emails:

    subjects = []

    def __init__(self,list_of_email_files):
        list_of_email_files = list_of_email_files

    def get_subjects(self):
        for email in list_of_email_files:
            with open(email) as f:
                file_data = f.readlines()
                self.get_match_and_next_line("^Subject", file_data)
            f.closed

    def get_match_and_next_line(self, pattern, file_data):
        self.pattern = pattern
        self.file_data = file_data
        for line_number, line in enumerate(file_data):
            if re.search(pattern, line, re.I):
                subject = line.rstrip() + " " + file_data[line_number + 1].rstrip()
                self.subjects.append(subject)

    def show_all_subjects(self):
        print(self.subjects)

list_of_email_files = email_files.get_list_of_files("/tmp/save/email_*")

parse_emails = parse_shadow_backup_emails(list_of_email_files)
parse_emails.get_subjects()
parse_emails.show_all_subjects()


