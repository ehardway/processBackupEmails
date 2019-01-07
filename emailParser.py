import glob

class email_files:

    @staticmethod
    def get_list_of_files(pattern):
        return glob.glob(pattern)


list_files = email_files.get_list_of_files("/tmp/save/email_*")
print(list_files)
