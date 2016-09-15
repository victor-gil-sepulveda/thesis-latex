#!/usr/bin/python

from optparse import OptionParser
import bibtexparser
from fuzzywuzzy import fuzz


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-a", dest="author")
    parser.add_option("--id", dest="id_details")
    
    (options, args) = parser.parse_args()
    
    bibfile =  args[0]
    
    bib_database = bibtexparser.loads(open(bibfile).read())
    
    if options.author is not None:
        possible_matches = []
        noauthor = 0
        for bib in bib_database.entries:
            
            if "author" in bib:
                similarities = [fuzz.ratio(part, options.author) for part in bib["author"].split()]
                similarities.append(fuzz.ratio(bib["author"], options.author))
                similarity = max(similarities)
                if similarity > 65:
                    possible_matches.append((similarity,bib))
            else:
                noauthor += 1
            
        print "%d entries without author"%noauthor
        for _, bib_match in sorted(possible_matches, reverse=True):
            print ("\cite{%s}"%bib_match["ID"]).ljust(35),"|", bib_match["author"][:15],"|", bib_match["title"][0:40]
    
    if options.id_details is not None:
        for bib in bib_database.entries:
            if bib["ID"] == options.id_details:
                print bib["ID"]
                print bib["author"]
                print bib["title"]
    
    
