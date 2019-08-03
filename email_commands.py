import re
import json
import glob
import os
import pendulum


class EmailFiles:
    @staticmethod
    def get_list_of_files(pattern):
        return glob.glob(pattern)


class EmailCommands:
    commands = []

    def __init__(self, directory):
        list_of_email_files = EmailFiles.get_list_of_files(directory)
        list_of_command_emails = self.check_for_command_email(list_of_email_files)
        self.commands = self.get_commands(list_of_command_emails)

    @staticmethod
    def check_for_command_email(list_of_email_files):
        command_emails = []
        for email in list_of_email_files:
            with open(email) as f:
                if 'Subject: COMMAND' in f.read():
                    command_emails.append(email)
        return command_emails

    @staticmethod
    def get_commands(list_of_command_emails):
        commands = []
        for email in list_of_command_emails:
            with open(email) as f:
                file_data = f.readlines()
                for line in file_data:
                    if re.search("^COMMAND", line):
                        commands.append(line)
#                    os.remove(email)
        return commands

    def process_commands(self, dictionary, default_threshold, default_date_format, dictionary_file):
        for command in self.commands:
            c = command.split('|')
            if len(c) >= 5:
                c_command = c[1].strip()
                c_company = c[2].strip()
                c_server = c[3].strip()
                c_client = c[4].strip()
                dictionary = self.update_dictionary(c_command, c_company, c_client, c_server, dictionary,
                                                    default_threshold,
                                                    default_date_format)
        self.save_json(dictionary, dictionary_file)

    @staticmethod
    def update_dictionary(command, company, client, server, dictionary, default_threshold, default_date_format):
        now = pendulum.now('US/Eastern')
        threshold_time = now.subtract(hours=default_threshold + 1)
        default_time = threshold_time.strftime(default_date_format)
        key = company + server + client
        if command.upper() == 'REMOVE':
            print(key)
            if key in dictionary.keys():
                del dictionary[key]
        elif command.upper() == 'ADD':
            if key not in dictionary.keys():
                dictionary[key] = {'server': client, 'client': client, 'company': company,
                                   'backup_code': '1120', 'email_time': default_time,
                                   'threshold': default_threshold}
        return dictionary

    @staticmethod
    def save_json(data, file_name):
        with open(file_name, 'w') as fp:
            json.dump(data, fp)

