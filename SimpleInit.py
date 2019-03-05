import json
import os
import sys

# GLOBAL VARIABLES
simply_encode = 0
overwrite_json = 0
new_file = 0
output_filename = 'char_inits.json' # default output file name
default_infile = "si_input.txt" # default input file name

# FUNCTIONS
def print_manual():
	manual = '''Command line flags:
	-e:	Simply encode the read input file into the json format as a save
		file. Does not prompt user for any addition or removal of
		characters.
	-o:	Overwrite the current save file with whatever input is included in
		the input file.
	-id:	Print the program description for "SimpleInit.py".
	-n:	Creates a new, blank input file. Cannot be run with -o.
	-d:	Removes ALL save files. Use with caution.
	man:	Print the manual.

Initiative Tracker Commands:
	q:	Quit the initiative tracker. Does not remove slain characters from
		the save file.
	kill:	Removes a character from the initiative order, but does not remove
		that character from the save file.
	save:	Overwrites the save file with the current initiative order.
	"":	Simply hitting return will continue to the next character's turn.
'''
	print( manual )

def print_descriptor():
	description = '''Haven't written the description yet.
'''
	print( description )

def print_char_list( char_list ):
	print( "All characters: " )
	for char in char_list:
		print( "\t%s\t-\t%s" % ( str( char_list[char] ), str( char ) ) )

def sort_char_dict( char_dict ):
	sorted_char_dict = {}
	cur_max = 0
	cur_char = ''
	while len( sorted_char_dict ) != len( char_dict ):
		for char in char_dict:
			if char not in sorted_char_dict and int( char_dict[char] ) >= cur_max:
				cur_max = int( char_dict[char] )
				cur_char = char
		sorted_char_dict[ cur_char ] = char_dict[cur_char]
		cur_char = ''
		cur_max = 0
	return sorted_char_dict

def json_recovery( fd ):
	char_dict = json.load( fd )
	return char_dict

def get_chars_from_file( fd ):
	ret_dict = {}
	for line in fd:
		line = line.split()
		if len( line ) == 0:
			break
		elif len( line ) != 2:
			print( "  Error: invalid input line argument length: %d" % len( line ) )
			print( "    Args: %s" % str( line ) )
			continue
		else:
			ret_dict[line[0]] = line[1]
	return ret_dict

def add_chars_from_file( ret_dict, fd ):
	for line in fd:
		line = line.split()
		if len( line ) == 0:
			break
		elif len( line ) != 2:
			print( "  Error: invalid input line argument length: %d" % len( line ) )
			print( "    Args: %s" % str( line ) )
			continue
		else:
			ret_dict[line[0]] = line[1]
	return ret_dict

def clean_json( filename ):
	os.remove( filename )

# MAIN
if len( sys.argv ) > 1: # reads command line arguments and sets flags
	args = sys.argv[1:]
	if '-d' in args:
		for filename in os.listdir( os.getcwd() ):
			if filename.endswith( '.json' ):
				os.remove( filename )
		print( "All save files removed." )
		exit()
	if '-e' in args:
		simply_encode = 1
	if '-o' in args:
		if '-n' not in args:
			overwrite_json = 1
		else:
			print( "  Error: incompatible flags." )
			exit()
	if 'man' in args:
		print_manual()
		exit()
	if '-id' in args:
		print_descriptor()
		exit()
	if '-n' in args:
		if '-o' not in args:
			new_file = 1
			file = open( default_infile, 'w' )
			file.close()
		else:
			print( "  Error: incompatible flags." )
			exit()

chars = {} # to be dictionary of characters later
try:
	f = open( default_infile )
	line_in = f.readline().split()
	if len( line_in ) != 0:
		if len( line_in ) == 2 and line_in[0] == '#':
			# new output file name is as specified (.json)
			output_filename = line_in[1] + ".json"
			# if we aren't overwriting the json and the file exists:
			if not overwrite_json and \
				os.path.isfile( os.path.join( os.getcwd(), output_filename ) ):
				f.close() # close old file, 
				f = open( output_filename ) # open the .json file
				chars = json_recovery( f ) # don't remember why this is its own fn
			else: # the file doesn't exist, or we are overwriting the json
				chars = get_chars_from_file( f ) # standard read
		elif not overwrite_json and \
			( os.path.isfile( os.path.join( os.getcwd(), output_filename ) ) ):
			f.close() # close old file,
			f = open( output_filename ) # open the .json file
			chars = json_recovery( f )
		else:
			chars[ line_in[0] ] = line_in[1] # makes sure not to forget first line if no '#'
			chars = add_chars_from_file( chars, f ) # read and append
		f.close()
	else:
		chars = {}
		
except FileNotFoundError:
	print( 'No input file "%s".' % ( default_infile ) )
	exit()

with open( output_filename, 'w' ) as filename:
	# saves current progress to output
	json.dump( chars, filename )

print_char_list( chars ) # so user can see what was added

add_chars = ''
if not simply_encode: # don't prompt add in simply_encode mode
	add_chars = input( "Add a character? (y/n): " )
if add_chars == 'y':
	while True:
		add_whom = input( "Enter name and initiative: " )
		if add_whom == '':
			break
		add_whom = add_whom.split()
		if len( add_whom ) != 2:
			print( "  Error: invalid input line argument length: %d" % len( add_whom ) )
			print( "    Args: %s" % str( add_whom ) )
			continue
		chars[ add_whom[0] ] = add_whom[1]
	print_char_list( chars ) # so user can see what was added

delete_chars = ''
if not simply_encode: # don't prompt for remove on simply_encode mode
	delete_chars = input( "Remove a character? (y/n): " )
if delete_chars == 'y':
	while True:
		delete_whom = input( "Enter name to remove: " )
		if delete_whom == '':
			break
		try:
			del chars[delete_whom]
		except KeyError:
			print( "Not a valid character name." )

	print_char_list( chars ) # show user result after removals
	with open( output_filename, 'w' ) as filename:
		json.dump( chars, filename ) # save progress

chars = sort_char_dict( chars ) # sort the dictionary
print( "Sorting..." )
print_char_list( chars ) # show user result
with open( output_filename, 'w' ) as filename:
	json.dump( chars, filename ) # save progress

if simply_encode: # if simple encode mode, don't show tracker
	exit()

# ADD INITIATIVE TRACKER