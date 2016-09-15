#!/usr/bin/python

import os
import glob
from optparse import OptionParser

paper_supp_sources = {
	
	"pyproct_supplementary":"papers/pyProCT_supp",
	"pyrmsd_supplementary":"papers/pyRMSD_supp",
	"icnma_supplementary":"papers/icNMA_supp"

}

paper_pdfs = ["papers/pyProCT/pyproct.pdf", "papers/pyRMSD/pyrmsd.pdf", "papers/icNMA/icnma.pdf"]

def create_dir(directory):
	if not os.path.exists(directory):
    		os.makedirs(directory)

if __name__ == "__main__":
	BUILD_DIR = "build"
	IMAGES_DIR = "images"
	CONF_DIR = "conf"
	MAIN_LATEX_FILE = "thesis"	


	parser = OptionParser()
	parser.add_option("-t", action ="store_true", default= False,  dest="process_tex")
	parser.add_option("-i", action ="store_true", default= False,  dest="process_images")
	parser.add_option("-c", action ="store_true", default= False,  dest="clean")
	parser.add_option("-f", action ="store_true", default= False,  dest="full_compilation")
	(options, args) = parser.parse_args()



	# Create build directory
	create_dir(BUILD_DIR)

	if options.clean:
		os.system("rm %s"%(os.path.join(BUILD_DIR,"*")))
			
	if options.process_images:
		# Copy pdf images
		os.system("cp %s %s"%(os.path.join(IMAGES_DIR,"*.pdf"),BUILD_DIR))
		# Create pdf from svg
		svgs = glob.glob(os.path.join(IMAGES_DIR,"*.svg"))
		for svg_file in svgs:
			file_name = os.path.splitext(os.path.basename(svg_file))[0]
			# --export-latex removes texts :(	
			os.system("inkscape -D -z --file=%s --export-pdf=%s.pdf "%(svg_file,os.path.join(BUILD_DIR,file_name)))
	
		# Prepare paper stuff
		for paper in paper_supp_sources:
			tex_files = glob.glob(os.path.join(paper_supp_sources[paper],"*.tex"))
			for tex_file in tex_files:
				file_name = os.path.splitext(os.path.basename(tex_file))[0]	
				os.system("cp %s %s.tex"%(tex_file, os.path.join(BUILD_DIR,file_name)))
		
			svgs = glob.glob(os.path.join(paper_supp_sources[paper],IMAGES_DIR,"*.svg"))
			for svg_file in svgs:
				file_name = os.path.splitext(os.path.basename(svg_file))[0]	
				os.system("inkscape -D -z --file=%s --export-pdf=%s.pdf --export-latex"%(svg_file,os.path.join(BUILD_DIR,file_name)))
		
			pngs = glob.glob(os.path.join(paper_supp_sources[paper],IMAGES_DIR,"*.png"))
			for png_file in pngs:
				file_name = os.path.splitext(os.path.basename(png_file))[0]	
				os.system("cp %s %s"%(png_file, BUILD_DIR))
			
	if options.process_tex:
		# Copy tex files to build dir
		os.system("cp *.tex %s"%BUILD_DIR)
		os.system("cp tables/*.tex %s"%BUILD_DIR)
		os.system("cp abbreviations/*.tex %s"%BUILD_DIR)
		os.system("cp bibliography/*.bib %s"%BUILD_DIR)
		
		# Copy chapters
		os.system("cp chapters/*.tex %s"%BUILD_DIR)
		
		# Copy conf. tex files to build dir
		os.system("cp %s %s"%(os.path.join(CONF_DIR,"*.tex"),BUILD_DIR))
		
		# Prepare paper stuff
		for paper in paper_supp_sources:
			tex_files = glob.glob(os.path.join(paper_supp_sources[paper],"*.tex"))
			for tex_file in tex_files:
				file_name = os.path.splitext(os.path.basename(tex_file))[0]	
				os.system("cp %s %s.tex"%(tex_file, os.path.join(BUILD_DIR,file_name)))
		# Paper pdfs
		for paper in paper_pdfs:
			os.system("cp %s %s"%(paper, BUILD_DIR))
	
	# Compile
	current_dir = os.getcwd()
	os.chdir(BUILD_DIR)
	os.system("rm *.aux *.bbl *.toc")
	os.system("pdflatex %s"%MAIN_LATEX_FILE) # for references etc
	if options.full_compilation:
		os.system("biber %s"%MAIN_LATEX_FILE)
		os.system("pdflatex %s"%MAIN_LATEX_FILE)
		os.system("makeglossaries %s"%MAIN_LATEX_FILE)
		os.system("pdflatex %s"%MAIN_LATEX_FILE)
		os.system("cp %s.pdf %s"%(MAIN_LATEX_FILE,current_dir))
	os.chdir(current_dir)
	
