import os
import fileinput

# Logging utility to handle URLs with log files
# Saves progress of iteration with logging methods


# TODO: refactor to not use fileinput lib. Use normal python filehandling and manually do backup file


class URLScrapingLogHandler:
    row_str = "{i}\t{status}\t{url}\n"

    def __init__(self, folder, urls, index_list=None, start_new=False):
        warnings.warn("DO NOT USE print() while the URLScrapingLogHandler is in use!")
        self.all_file = os.path.join(folder, 'all_urls.log')
        self.outstanding_file = os.path.join(folder, 'outstanding_urls.log')
        self.skipped_file = os.path.join(folder, 'skipped_urls.log')
        self.outstanding_file_handler = None
        
        if not start_new:   # auto start new if log files are not found
            start_new = self.check_start_new(folder)

        if start_new:
            assert urls is not None, "No urls found, urls must not be None!"
            with open(self.all_file, 'w+') as all_:
                with open(self.outstanding_file, 'w+') as out_:
                    if index_list is not None:
                        urls_index_list = [(i, url,) for i, url in zip(index_list, urls)]
                    else:
                        urls_index_list = [(i+1, url,) for i, url in enumerate(urls)]
                    for i, url in urls_index_list:
                        all_.write(self.row_str.format(i=i, status="OUTSTANDING", url=url))
                        out_.write(self.row_str.format(i=i, status="OUTSTANDING", url=url))
        else:
            # get last line in outstanding_file
            last_outstanding_row = 0
            with fileinput.input(self.outstanding_file) as f:
                try:
                    for line in f:
                        next(f)  # skip all lines
                except StopIteration:
                    last_outstanding_row = f.lineno()
            # copy remaining to outstanding_file
            with open(self.outstanding_file, "a+") as out_:
                with open(self.all_file, "r+") as all_:
                    for _ in range(0, last_outstanding_row):
                        next(all_)  # skip lines
                    for line in all_:
                        out_.write(line)

        open(self.skipped_file, "w+").close()  # clear file
        self.outstanding_file_handler = fileinput.input(self.outstanding_file, inplace=True)

    @staticmethod
    def check_start_new(folder):
        return True if not os.path.isfile(os.path.join(folder, 'outstanding_urls.log')) else False

    def iterate_urls(self):
        for line in self.outstanding_file_handler:
            tokens = line.strip().split("\t")
            yield tuple(tokens)

    def log_DONE(self, tokens):
        i, status, url = tokens
        print(self.row_str.format(i=i, status="DONE", url=url), end="")

    def log_SKIPPED(self, tokens):
        i, status, url = tokens
        print(self.row_str.format(i=i, status="SKIPPED", url=url), end="")
        with open(self.skipped_file, 'a+') as skipped_:
            skipped_.write(self.row_str.format(i=i, status="SKIPPED", url=url))

    @staticmethod
    def iterate_log_file(log_file):
        with open(log_file, "r") as f:
            for line in f:
                tokens = line.strip().split("\t")
                yield tuple(tokens)

    def close(self):
        self.outstanding_file_handler.close()

    def __del__(self):
        self.close()
