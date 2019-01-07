import glob
import re
from datetime import datetime

class email_files:

    @staticmethod
    def get_list_of_files(pattern):
        return glob.glob(pattern)


class parse_shadow_backup_emails:
    subjects = []
    split_subjects = {}

    def __init__(self, directory):
        self.list_of_email_files = email_files.get_list_of_files(directory)

    def get_subjects(self):
        for email in self.list_of_email_files:
            with open(email) as f:
                file_data = f.readlines()
                self.get_match_and_next_line("^Subject:", file_data)
            f.closed
        return self.subjects

    def get_match_and_next_line(self, pattern, file_data):
        for line_number, line in enumerate(file_data):
            if re.search("^From", line) and line_number == 1:
                from_date = "| " + line
            if re.search(pattern, line):
                subject = line.rstrip() + " " + file_data[line_number + 1].rstrip() + " " + from_date.rstrip()
                self.subjects.append(subject)

    def split_subject(self, subjects):
        i = 0
        for subject in subjects:
            split_subject = subject.split('|')
            self.split_subjects[i] = self.create_dictionary(split_subject)
            i += 1
        return self.split_subjects

    def create_dictionary(self, split_subject):
        if len(split_subject) == 7:
            subject_dictionary = {
                'server': split_subject[0].strip().strip('Subject: '),
                'client': split_subject[1].strip(),
                'company': split_subject[2].strip(),
                'backup_code': self.get_backup_code(split_subject[5].strip()),
                'email_date': self.get_email_time(split_subject[-1].strip())
            }
            return subject_dictionary

    @staticmethod
    def get_backup_code(raw_code):
        backup_code = raw_code.split()
        return backup_code[1].strip("'")

    @staticmethod
    def get_email_time(raw_email_time):
        email_time_list = raw_email_time.split()
        email_time = email_time_list[-4] + ' ' + email_time_list[-3] + ' ' + email_time_list[-2] + ' ' + email_time_list[-1]
        datetime_object = datetime.strptime(email_time, '%b %d %H:%M:%S %Y')
        return datetime_object


parse_emails = parse_shadow_backup_emails("/tmp/save/*")

subjects = parse_emails.get_subjects()

split_subjects = parse_emails.split_subject(subjects)

print(split_subjects)
