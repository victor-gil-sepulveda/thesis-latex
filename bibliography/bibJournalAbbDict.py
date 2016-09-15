import urllib
import urllib2
import re
import bibtexparser
from bibtexparser.bparser import BibTexParser
import sys
from fuzzywuzzy import fuzz

"""
http://www.rci.rutgers.edu/~longhu/ChemJournalAbbreviation_Hu.htm
http://www.ncbi.nlm.nih.gov/nlmcatalog/?term=Proceedings+of+the+National+Academy+of+Sciences+%5BTitle%5D
http://cassi.cas.org/search.jsp
http://guides.lib.berkeley.edu/bioscience-journal-abbreviations/k-q
http://chemlab.truman.edu/chemlab_backup/labreports_files/journals.htm
https://www.ieee.org/documents/trans_journal_names.pdf
http://home.ncifcrf.gov/research/bja/journams_b.html
** BEST**
http://www.journalabbr.com/journal/journal-of-computational-and-theoretical-nanoscience.html
https://github.com/JabRef/reference-abbreviations/blob/master/journals/journal_abbreviations_mechanical.txt
https://raw.githubusercontent.com/mpharrigan/bibcheck/master/bibpy/abbreviations.json
"""

def look_in_tuple_dict(tuple_dict, first):
	possible_matches = []
	for a_tuple in tuple_dict:
		lwc_f = first.lower()
		dic_item_0_lwc = a_tuple[0].lower()
		dic_item_1_lwc = a_tuple[1].lower()

		if fuzz.ratio(lwc_f, dic_item_0_lwc) > 85 or fuzz.ratio(lwc_f, dic_item_1_lwc) > 85:
			possible_matches.append(a_tuple)
	return possible_matches
	
	
def check_if_decided(tuple_dict, first):
	for a_tuple in tuple_dict:
		lwc_f = first.lower()
		dic_item_0_lwc = a_tuple[0].lower()
		
		if lwc_f == dic_item_0_lwc:
			return a_tuple[1]
	return None

def yes_no(what):
	while True:
		ok = raw_input("%s(y/n): "%what)
		if ok == "y" or ok == "":
			return True
		if ok == "n":
			return False

def ask_number_or_pass(what, max_val):
	while True:
		num = raw_input("%s(number/n): "%what)
		if num == "n":
			return None
		else:		
			try:			
				index = int(num)						
				if index < max_val:
					return index
				else:
					print "Choose another index"
			except:
				pass		
				
def propper_abbr(abb, abb_dict):
	for a_tuple in abb_dict:
		if abb == a_tuple[1]:
			return True
	return False		


if __name__ == "__main__":
	#with open('thesis.bib') as bibtex_file:
	#  	bib_database = bibtexparser.load(bibtex_file)
	  	
	#with open('test.bib', 'w') as bibtex_file:
	#	bibtexparser.dump(bib_database, bibtex_file)
	
	parser = BibTexParser()
        parser.ignore_nonstandard_types = False
        bib_database = bibtexparser.loads(open("thesis.bib").read(), parser)

	# Fix abbreviations and store abbreviation dictionary
	abb_dict = []
	for line in open("abbreviations.dic"):
		parts = line.rstrip().split("|")
		if len(parts) == 2:
 			abb_dict.append(parts)
 			
	already_decided = []
	try:
		for line in open("abbreviation_decissions.dic","r"):
			parts = line.rstrip().split("|")
			if len(parts) == 2:
	 			already_decided.append(parts)
	except IOError:
		print "Decissions file not found." 
	
	decissions_file = open("abbreviation_decissions.dic", "a")

	total = len(bib_database.entries)
	current = 1	
	for bib in bib_database.entries:
		entry_type = bib["ENTRYTYPE"]
		
		if entry_type == "article" and "timestamp" in bib:
			del bib["timestamp"]
		
		if entry_type == "article" and "urldate" in bib:
			del bib["urldate"]
		
		if "keywords" in bib:
			del bib["keywords"]
		
		if "year" in bib:
			del bib["year"]
		
		if "abstract" in bib:
			del bib["abstract"]
						
		if "journal" in bib:
			print "----------------------------------------------"
			print "Working with:", bib["journal"], "(", current, "of", total, ")"
			print "----------------------------------------------"
			
			if not propper_abbr(bib["journal"], abb_dict):
				prior_decission = check_if_decided(already_decided, bib["journal"])
				if prior_decission is not None:
					print "You already took a decission on this one: %s -> %s"%(bib["journal"], prior_decission)
					bib["journal"] = prior_decission
				else:
					# lookup in dict
					possible_matches = look_in_tuple_dict(abb_dict, bib["journal"])
					if len(possible_matches) > 1 :
						print "I found this abbreviations for '%s':"%bib["journal"]
						for i, match in enumerate(possible_matches):
							print "\t",i,"-" , match[0]," || ", match[1]
						choice = ask_number_or_pass("Choose one", len(possible_matches))
						if choice is not None:
							already_decided.append((bib["journal"], possible_matches[choice][1]))
							decissions_file.write("%s|%s\n"%(bib["journal"], possible_matches[choice][1]))
							decissions_file.flush()
							bib["journal"] = possible_matches[choice]
						else:
							print "We will always keep this one as is"
							already_decided.append((bib["journal"], bib["journal"]))
							decissions_file.write("%s|%s\n"%(bib["journal"], bib["journal"]))
							decissions_file.flush()
				
					elif len(possible_matches) == 1:
						print "Found '%s' as '%s'."%(bib["journal"], possible_matches[0][1]) 
						if yes_no("Change?"):
							print "Ok, let's change it"
							already_decided.append((bib["journal"], possible_matches[0][1]))
							decissions_file.write("%s|%s\n"%(bib["journal"], possible_matches[0][1]))
							decissions_file.flush()
							bib["journal"] = possible_matches[0]
						else:
							print "We will always keep this one as is"
							already_decided.append((bib["journal"], bib["journal"]))
							decissions_file.write("%s|%s\n"%(bib["journal"], bib["journal"]))
							decissions_file.flush()
					else:
						print "No abbreviation was found for '%s'. Add new one to dictionary? (write it or enter)"%bib["journal"]
						abbrv = raw_input("New abbr.:")
						if abbrv != "":
							already_decided.append((bib["journal"], abbrv))
							decissions_file.write("%s|%s\n"%(bib["journal"], abbrv))
							decissions_file.flush()
							bib["journal"] = abbrv
			else:
				print "%s is already a propper journal abbreviation"%bib["journal"]
			
		current += 1
					
decissions_file.close()

#writer = bibtexparser.bwriter.BibTexWriter()
#with open('thesis_abb.bib', 'w') as bib_database:
#    bibfile.write(writer.write(bib_database))
    
with open('thesis_abb.bib', 'w') as bibtex_file:
	bibtexparser.dump(bib_database, bibtex_file)
