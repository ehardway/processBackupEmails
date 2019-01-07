import glob
import re


class email_files:

    @staticmethod
    def get_list_of_files(pattern):
        return glob.glob(pattern)


class parse_shadow_backup_emails:
    subjects = []

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
            if re.search(pattern, line):
                subject = line.rstrip() + " " + file_data[line_number + 1].rstrip()
                self.subjects.append(subject)


parse_emails = parse_shadow_backup_emails("/tmp/save/*")

subjects = parse_emails.get_subjects()

print(subjects)
