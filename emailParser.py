
from parse_shadow_backup_emails import *

parse_emails = parse_shadow_backup_emails("/tmp/save/*")

subjects = parse_emails.get_subjects()

parse_emails.split_subject(subjects)

parse_emails.build_unique_dictionary()

parse_emails.save_dictionary()


