#!/usr/local/bin/python
import socket

from parse_shadow_backup_emails import *
from email_commands import *

parse_emails = parseShadowBackupEmails("/tmp/email_messages/*")

email_commands = EmailCommands("/tmp/email_messages/*")

email_commands.process_commands(parse_emails.master_email_dictionary, parse_emails.default_threshold,
                                parse_emails.date_format, parse_emails.dictionary_file)

parse_emails.generate_html_table()

if socket.gethostname() == 'localhost':
    parse_emails.rename_web_page()
