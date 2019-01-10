import re
from datetime import datetime
import json
import glob
import os
import pendulum


class email_files:
    @staticmethod
    def get_list_of_files(pattern):
        return glob.glob(pattern)


class parseShadowBackupEmails:
    subjects = []
    split_subjects = []
    active_email_dictionary = {}
    dictionary_file = '/tmp/email_dictionary.json'
    web_page_file = 'sp.html'
    master_email_dictionary = {}
    change_count = 0
    backup_code_1120 = []
    backup_code_1121 = []
    backup_code_unknown = []
    default_threshold = 48
    row_id = 0
    date_format = '%m-%d-%Y %H:%M:%S'
    max_parse_time = 'none'
    min_parse_time = 'none'

    def __init__(self, directory):
        self.list_of_email_files = email_files.get_list_of_files(directory)

    def check_for_shadow_email(self):
        list_of_shadow_emails = []
        for email in self.list_of_email_files:
            with open(email) as f:
                if 'ShadowProtectSvc' in f.read():
                    list_of_shadow_emails.append(email)
        return list_of_shadow_emails

    def get_subjects(self):
        list_of_email_files = self.check_for_shadow_email()
        for email in list_of_email_files:
            with open(email) as f:
                file_data = f.readlines()
                self.get_match_and_next_line("^Subject:", file_data)
                os.remove(email)
        return self.subjects

    def rename_web_page(self):
        os.rename(self.web_page_file,"/var/www/html/reports/" + self.web_page_file)

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
                'email_time': self.convert_utc_to_local(str(self.get_email_time(split_subject[-1].strip()))),
                'threshold': self.default_threshold
            }
            return subject_dictionary

    def convert_utc_to_local(self, email_time):
        dt = pendulum.from_format(email_time, 'MMM DD HH:mm:ss YYYY', tz='UTC')
        tz = pendulum.timezone('US/Eastern')
        in_est = tz.convert(dt)
        return in_est.strftime(self.date_format)

    def build_unique_active_dictionary(self):
        split_subjects = list(filter(None.__ne__, self.split_subjects))
        for subject in split_subjects:
            key = subject['company'] + subject['server'] + subject['client']
            if key not in self.active_email_dictionary:
                self.active_email_dictionary[key] = subject
            elif key in self.active_email_dictionary:
                datetime_object_in_dict = datetime.strptime(self.active_email_dictionary[key]['email_time'],
                                                            self.date_format)
                datetime_object = datetime.strptime(subject['email_time'], self.date_format)
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
                                                                   self.date_format)
                datetime_object = datetime.strptime(email_data['email_time'], self.date_format)
                if datetime_object > datetime_object_in_master_dict:
                    if self.master_email_dictionary[key]['threshold'] != email_data['threshold']:
                        email_data['threshold'] = self.master_email_dictionary[key]['threshold']
                    self.master_email_dictionary[key] = email_data
                    self.change_count += 1
        if self.change_count > 0:
            print("Something Change Updating Dictionary on disk")
            self.save_json(self.master_email_dictionary, self.dictionary_file)

    def generate_html_table(self):
        self.sort_master_dictionary_for_web_page()
        table = ''
        table += self.build_html_table_header()
        table += self.build_html_table_data('unknown', self.backup_code_unknown)
        table += self.build_html_table_data('critical', self.backup_code_1121)
        table += self.build_html_table_data('ok', self.backup_code_1120)
        table += self.build_html_table_footer()
        with open(self.web_page_file, "w") as text_file:
            text_file.write(table)

    def build_dashboard(self):
        table = ''
        table += "<table border=1>\n"
        table += "<tr>\n"
        table += "<th> OK </th>\n"
        table += "<th> UNKNOWN </th>\n"
        table += "<th> CRITICAL </th>\n"
        table += "<th> Total </th>\n"
        table += "</tr>\n"
        table += "<tr>\n"
        table += "<td align=center> " + str(len(self.backup_code_1120)) + "</td>\n"
        table += "<td bgcolor=orange align=center> " + str(len(self.backup_code_unknown)) + "</td>\n"
        table += "<td bgcolor=E64A34 align=center> " + str(len(self.backup_code_1121)) + "</td>\n"
        table += "<td align=center> " + str(
            len(self.backup_code_1121) + len(self.backup_code_1120) + len(self.backup_code_unknown)) + "</td>\n"
        table += "</tr></table>\n"
        return table

    def build_html_table_data(self, status, list_of_code):
        table_data = ''
        for data in list_of_code:
            self.row_id += 1
            table_data += self.build_table_row_data(self.row_id, status, data)
        return table_data

    @staticmethod
    def get_row_color(status):
        colors = {'unknown': 'orange', 'ok': 'white', 'critical': 'E64A34'}
        return colors[status]

    def build_table_row_data(self, row_id, status, row):
        table_row = ''
        table_row += "<tr bgcolor=" + self.get_row_color(status) + ">"
        table_row += "<td align=center>" + str(row_id) + "</td>"
        table_row += "<td align=center>" + status.upper() + "</td>"
        table_row += "<td align=center>" + row['company'] + "</td>"
        table_row += "<td align=center>" + row['client'] + "</td>"
        table_row += "<td align=center>" + row['email_time'] + "</td>"
        table_row += "<td align=center>" + row['backup_code'] + "</td>"
        table_row += "<td align=center>" + str(row['threshold']) + " Hours</td>"
        table_row += "</tr>\n"
        return table_row

    def build_html_table_header(self):
        current_time = pendulum.now('US/Eastern')
        header = ['id', 'status', 'company', 'client', 'last email', 'backup_code', 'threshold']
        table_head = ''
        table_head += "<html>\n"
        table_head += "<head>\n"
        table_head += "<title> Shadow Protect Backup Status </title>\n";
        table_head += "</head>\n"
        table_head += "Page generated at " + current_time.strftime(self.date_format) + "<br>"
        table_head += "Emails processed between " + self.min_parse_time.strftime(self.date_format) + ' and ' + self.max_parse_time.strftime(self.date_format) + "<br>"
        table_head += self.build_dashboard()
        table_head += "<table border=1>\n"
        table_head += "<tr>"
        for column in header:
            table_head += '<th>' + column.upper() + '</th>'
        table_head += "</tr>\n"
        return table_head

    def build_html_table_footer(self):
        footer = ''
        footer += "</table>"
        footer += "</html>"
        return footer

    def sort_master_dictionary_for_web_page(self):
        for key, data in sorted(self.master_email_dictionary.items()):
            self.get_parse_time(data['email_time'])
            now = pendulum.now('US/Eastern')
            threshold_time = now.subtract(hours=data['threshold'])
            alert_time_formatted = threshold_time.strftime(self.date_format)
            alert_time = datetime.strptime(alert_time_formatted, self.date_format)
            email_time = datetime.strptime(data['email_time'], self.date_format)
            if email_time < alert_time:
                self.backup_code_unknown.append(data)
            elif data['backup_code'] == "1120":
                self.backup_code_1120.append(data)
            elif data['backup_code'] == "1121":
                self.backup_code_1121.append(data)

    def get_parse_time(self, parse_time):
        if self.max_parse_time == 'none':
            self.max_parse_time = datetime.strptime(parse_time, self.date_format)
        elif datetime.strptime(parse_time, self.date_format) > self.max_parse_time:
            self.max_parse_time = datetime.strptime(parse_time, self.date_format)
        if self.min_parse_time == 'none':
            self.min_parse_time = datetime.strptime(parse_time, self.date_format)
        elif datetime.strptime(parse_time, self.date_format) < self.min_parse_time:
            self.min_parse_time = datetime.strptime(parse_time, self.date_format)

    def load_master_dictionary(self):
        if os.path.isfile(self.dictionary_file):
            self.master_email_dictionary = self.load_json(self.dictionary_file)

    def initialize_dictionary(self):
        if not os.path.isfile(self.dictionary_file):
            print("Initialized Dictionary on Disk")
            self.save_json(self.active_email_dictionary, self.dictionary_file)

    @staticmethod
    def save_json(data, file_name):
        with open(file_name, 'w') as fp:
            json.dump(data, fp)

    @staticmethod
    def load_json(file_name):
        try:
            with open(file_name, 'r') as fp:
                return json.load(fp)
        except:
            print("something went wrong")

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
