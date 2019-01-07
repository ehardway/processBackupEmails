import glob

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
                read_data = f.read()
                print(read_data)
                f.closed

        def get_match_and_next_line(self,pattern):
            self.pattern = pattern

list_of_email_files = email_files.get_list_of_files("/tmp/save/email_*")

parse_emails = parse_shadow_backup_emails(list_of_email_files)
parse_emails.get_subjects()


