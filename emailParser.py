
from parse_shadow_backup_emails import *

parse_emails = parseShadowBackupEmails("/tmp/save/*")

subjects = parse_emails.get_subjects()

parse_emails.split_subject(subjects)

parse_emails.build_unique_active_dictionary()

parse_emails.load_master_dictionary()

parse_emails.compare_master_and_active_dictionaries()

parse_emails.generate_html_table()



