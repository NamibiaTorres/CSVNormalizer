import pandas as pd
from datetime import datetime
from pytz import timezone
import io
import sys


a_file = 'sample.csv'

def read_stdin_as_dataframe():
	'''
	Invalid characters will be replaced with the Unicode Replacement
	Character.
	If that replacement makes data invalid (for example,
	because it turns a date field into something unparseable),
	a warning will be printed to `stderr`
	and the row will be dropped from output

	Pandas is used because it handles address commas

	Return:
	Pandas dataframe
	'''
	raw_data = sys.stdin.detach().read()
	decoded_data = raw_data.decode('utf-8', 'replace')
	data_frame = pd.read_csv(io.StringIO(decoded_data), encoding='utf-8')

	return data_frame

def parse_timestamp(timestamp_str):
	'''
	Format timestamp column to ISO-8601
	The timestamp column is in US/Pacific and will be
	converted to US/Eastern

	Assumptions:
	The input document is in UTF-8
	Any times that are missing timezone information are in US/Pacific.
	Sample data may include timevariants that need to be handled: 10/20/19 1:00:00 AM

	Return:
	Iso-formatted timestamp w/ eastern timezone
	'''
	eastern = timezone('US/Eastern')
	pacific = timezone('US/Pacific')
	timestamp = datetime.strptime(timestamp_str, '%m/%d/%y %I:%M:%S %p')
	timestamp_pacific = pacific.localize(timestamp)
	timestamp_eastern = timestamp_pacific.astimezone(eastern)
	timestamp_iso = timestamp_eastern.isoformat()

	return timestamp_iso

def format_zipcodes(zipcode):
	'''
	Format ZIP codes as 5 digits.
	If there are less than 5 digits, add 0 as the prefix.

	Return:
	5-digit zipcodes
	'''

	return "%05i" % zipcode

def fails_cleansiness_checks(headers, row):
	'''
	When a character is invalid, it wll be replaced with
	the Unicode Replacement Character.
	If that replacement makes data invalid (for example,
	because it turns a date field into something unparseable),
	print a warning to `stderr` and drop the row from your output.

	Note:
	u"\uFFFD" is the python encoding for the unicode replacement character
	'''
	for header, value in zip(headers, row):
		if isinstance(value, str) and header != 'Notes' and u"\uFFFD" in value:
			return True
	return False

def convert_names_colmn_to_uppercase(fullname):
	'''
	Convert names in names column to upper case

	Given:
	There will be non-English names

	Return:
	Upper case names
	'''
	return fullname.upper()

def parse_address(address):
	'''
	Address column is passed in as is
	Take into account commas within quoted strings as part of addresses
	Wrap address in quotes

	Exceptions:
	except unicode validation

	Return:
	Address
	'''
	return ('"' + address + '"') if ',' in address else address

def parse_notes(notes):
	'''
	No transformations needed
	The notes column is free form text input by the enduser

	Return:
	Notes, and replace invalid utf-8 chars with valid unicode characters
	'''
	return notes

def parse_duration(duration_str):
    '''
    The columns `FooDuration` and `BarDuration` are in HH:MM:SS.MS
    format (where MS is milliseconds)

    Return:
    Converted duration strings in floating point seconds format.
    '''

    hhmmss_str, millsec_str = duration_str.split('.')
    hours, minutes, seconds = [int(x) for x in hhmmss_str.split(':')]
    duration = hours * 3600 + minutes * 60 + seconds + int(millsec_str) / 1000
    return "%.3f" % duration

def parse_total_duration(*args):
    '''
    The TotalDuration column has garbage data
    The value of the rows TotalDuration are replaced with the sum
    of the FooDuration and BarDuration columns
    '''
    total_duration = 0
    for duration in args:
        total_duration += float(parse_duration(duration))
    return "%.3f" % total_duration

def main():
	'''
	Converts the csv and prints out stdin CSV to the stdout
	It also prints out headers and iterates through each row in file
	'''
	contents = read_stdin_as_dataframe()

	# Get all headers:
	headers = list(contents)
	print(*headers, sep=',')

	# With the index iterate through each row:
	for index, row in contents.iterrows():
		if fails_cleansiness_checks(headers, row):
			sys.stderr.write("WARNING: Bad unicode outside of the notes column")
			continue

		out_row = list(row)
		out_row[headers.index('Timestamp')] = parse_timestamp(row['Timestamp'])
		out_row[headers.index('ZIP')] = format_zipcodes(row['ZIP'])
		out_row[headers.index('FullName')] =  convert_names_colmn_to_uppercase(row['FullName'])
		out_row[headers.index('Address')] = parse_address(row['Address'])
		out_row[headers.index('Notes')] = parse_notes(row['Notes'])
		out_row[headers.index('BarDuration')] = parse_duration(row['BarDuration'])
		out_row[headers.index('FooDuration')] = parse_duration(row['FooDuration'])
		out_row[headers.index('TotalDuration')] = parse_total_duration(out_row[headers.index('BarDuration')], out_row[headers.index('FooDuration')])
		print(*out_row, sep=',')

if __name__ == "__main__":
    main()
