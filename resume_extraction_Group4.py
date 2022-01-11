
import streamlit as st
import PyPDF2
import pandas as pd
import docx2txt
import os
import re
import nltk
import win32com.client as win32
import shutil, sys

from win32com.client import constants
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


@st.cache
def convert_df(df):
    return df.to_csv().encode('utf-8')


#converting doc file to docx
def saveAsDocx(path):
    try:
        #opening ms word
        word = win32.gencache.EnsureDispatch('Word.Application')
    except AttributeError:
        # Remove cache and try again.
        MODULE_LIST = [m.__name__ for m in sys.modules.values()]
        for module in MODULE_LIST:
            if re.match(r'win32com\.gen_py\..+', module):
                del sys.modules[module]
        shutil.rmtree(os.path.join(os.environ.get('LOCALAPPDATA'), 'Temp', 'gen_py'))

    
    #opening ms word
    #word = win32.gencache.EnsureDispatch('Word.Application')
               
    doc = word.Documents.Open(path)
    doc.Activate()
    
    
    #rename path with docx
    new_file_abs = os.path.abspath(path)
    new_file_abs = re.sub(r'\.\w+$','.docx',new_file_abs)
    
    #save & close
    word.ActiveDocument.SaveAs(
        new_file_abs, FileFormat=constants.wdFormatXMLDocument
    )
    doc.Close(False)
    #print('done')
    
def readFromPdfFile(pdfreader):
    no_pages = pdfreader.getNumPages()
    corpus = ''
    for i in range(0, no_pages):
        page = pdfreader.getPage(i)
        corpus += page.extractText()
        
    return corpus

#will remove any empty spaces, replaces tab, strips
def process_data(extracted_data_pdf):
    listData = extracted_data_pdf.split('\n')
    #st.write(len(listData))
    #forming a new list by removing empty strings from listData list
    listingData = []

    for i in listData:
        if len(i): #is true when string is empty(contains no whitespace)
            if i.isspace(): #is true when contains only whitespaces or tabs
                continue
            else:
                listingData.append(i)

    #st.write(len(listingData))
    #listingData

    new_list_data = []
    for item in listingData:
        new_list_data.append(item.replace('\t','') and item.strip())
    
    #removing spaces
    listingData = [x.strip() for x in listingData]
    listingData = [x.replace('\t','') for x in listingData]
    #st.write(len(listingData))
    return listingData


def readFromDocxFile(docxFileName):
    doc = docx2txt.process(docxFileName)
    return doc

#def readFromDocFile(docFileName):
    #doc = txt.process(docFileName)
    #return doc


#converting doc file to docx
def saveAsDocx(path):
    try:
        #opening ms word
        word = win32.gencache.EnsureDispatch('Word.Application')
    except AttributeError:
        # Remove cache and try again.
        MODULE_LIST = [m.__name__ for m in sys.modules.values()]
        for module in MODULE_LIST:
            if re.match(r'win32com\.gen_py\..+', module):
                del sys.modules[module]
        shutil.rmtree(os.path.join(os.environ.get('LOCALAPPDATA'), 'Temp', 'gen_py'))
                
    doc = word.Documents.Open(path)
    doc.Activate()
        
    #rename path with docx
    new_file_abs = os.path.abspath(path)
    new_file_abs = re.sub(r'\.\w+$','.docx',new_file_abs)
    
    #save & close
    word.ActiveDocument.SaveAs(
        new_file_abs, FileFormat=constants.wdFormatXMLDocument
    )
    doc.Close(False)

def removeMultipleSpaces(input_str):
    return re.sub(r'\s+',' ',input_str) # replaces more than 2 spaces with 1 space

# removes text inside brackets including brackets
def removeBrackets(input_str):
    return re.sub(r'\([^()]*\)','',input_str)

#extracting name
restricted_words = ['peoplesoft','admin','administrator','personal','resume','sql','developer','workday',
                        'consultant','page', 'curriculum','hyderabad','classification','internal'
                        ]

def extract_names(data_list):
    #print(data_list)
    for word in restricted_words:
        for item in data_list: 
            each_item_list = item.lower()
            if word in each_item_list:
                #print("@@@@",word)
                #print(each_item_list)
                #if each_item_list:
                data_list.remove(item)
            else:
                continue
            
    #print(data_list)
    return data_list
    

#extracting phone no.
PHONE_REG = re.compile(r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]')
def extract_phone_number(resume_text):
    phone = re.findall(PHONE_REG, resume_text)
    #print(phone)
    phone_list = []
    
    if phone:
        for num in phone:
            if len(num) >= 8 and len(num) < 11:
                phone_list.append(num)
    
    return phone_list

#extracting email
EMAIL_REG = re.compile(r'[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+')
    
def extract_emails(resume_text):
    return re.findall(EMAIL_REG, resume_text)

#extracting years of experience
def extract_yearsofexperience():
    experience_list = []
    for i in range(0,len(df)):
        each_row_text = df.loc[i]['Filtered Text'].lower()
        #will check for experience +(year||years||4-digits)
        if re.search(r"\bexperience\b",each_row_text) and (re.search(r"\byear\b",each_row_text) or re.search(r"\byears\b",each_row_text) or re.search(r"\[0-9]{4}",each_row_text)):
            experience_list.append(df.loc[i]['Filtered Text'])
        else:
            pass
                
    return (experience_list)
        
#extracting numbers from years of experience
def extract_numbers(list_years):
    exp_num_list = []
    for exp_w in list_years:
        match = re.search(r'(\d+\.?\d*)', exp_w)
        exp_num_list.append(match.group(0))
        
    return exp_num_list

#extraction of education
#should be small letters
RESERVED_WORDS = ['institute','btech','b.tech','bachelor','bachelors','b-tech','b. tech','mtech','m.tech',
        'm. tech','m-tech', 'technical education','graduate','school','college','engineering','polytechnic','be'
        'university','s.s.c','ssc','hsc','h.s.c','mca','m.c.a.','m.ca.','bca','b.c.a','master', 'board', 'b.e',
        'secondary board','12th standard','10th standard','mba','m.b.a.','business administration'
    ]
def extract_education():
    # we search each row for reserved words
    education = set()
    for i in range(0,len(df)):
        for word in RESERVED_WORDS:
            each_row_text = df.loc[i]['Filtered Text'].lower()
            if re.search(r"\b"+(word)+r"\b",each_row_text):
                education.add(df.loc[i]['Filtered Text'])
            else:
                pass
    return education


# this list was defined to handle values like windosw7/8/10
# coz such values were not coming in ngrams only windows7 was getting extracted
skills_db_complete = [
    'version 8.48','people tools 8.57', 'peoplesoft hrms', 'weblogic10.3','oracle tuxedo 10.3','portal 9.0',
    'oracle weblogic 10.3','windows server 2012','oracle 12cr1','version 8.48','peopletools8.54','tuxedo 10.3',
    'web logic 10.3','oracle enterprise linux 5.4', 'oracle 10gr2','version 8.48', 'ms-sql server 2008r2','windows 2007', 
    'weblogic8.1','tuxedo 10.3.6','tuxedo 8.1','people tools 8.57','peoplesoft applications 8.9','peopletools 8.55',
    'people tools 8.56','redhat enterprise linux','windows server 2012 r2','web logic 8.1','peoplesoft financials v 8.9',
    'pt8.54','windows 7','sql server 2016','sql server 2012', 'oracle 11g', 'sql server 2008','sql server 2014',
    'windows 2008 server', 'windows7', 'windows xp','eib inbound','windows 8','etv','windows 2008', 'workday hcm'  
]
    
#this will match the entire word as it is
skills_db = [
    'sdlc concepts','white box testing','sql skills','php','sql','java','full stack','c','c++','java','html','css','css3',
    'xml','javascript','json','html5','responsive designs','bootstrap','reactjs','react.js','react js','react', 'json',
    'j query','jquery','react','js','redux','mongo database','mongodb','node.js','mysql','aws','azure','ajax','typescript',
    'angular 10','ms office','photoshop cs6','xhtml','dreamweaver cs6','responsive design','nest js','visual studio',
    'netbeans','windows','android apps','unix','linux','es6','sass','hooks','shell scripting','weblogic', 'tuxedo',
    'oracle','dba','peoplesoft applications','people tools', 'windows nt','peoplesoft hrms','fscm', 'crm', 'cs',
    'hcm', 'bea tuxedo 8.1', 'bea weblogic 8.1', 'rhel as4', 'oel 5.5', 'oel 6', 'windows 2003/2008r2',
    'peoplesoft hrms 9.0','peopletools 8.47,8.48, 8.50, 8.52','putty', 'sql', 'toad', 'beyond compare','oracle 10g/11g',
    'capi','stat','autosys','fscm and 9.22 version','peoplesoft people tools','8.55.06','8.55.22', '8.57',
    'odyssey dashboard', 'odyssey jira', 'service now', 'transporter','aws service tools', 'compute','storage',
    'networks', 'databases', 'monitoring','identity access management', 'server r2', 'solaris server',
    'linux red hat version', 'apache tomcat 7.0.39 and 7.0.52', 'reporting and ps tools', 'application designer',
    'data mover', 'delphix virtual database', 'configuration manager', 'change assistant', 'sqr', 'n-vision',
    'control-m scheduler', 'hp ppm', 'sql developer','centrify putty','configuration manager', 'ps query', 
    'xml publisher','pum images', 'oracle 11g', 'oracle 12','change assistant', 'integration broker',
    'application designer', 'configuration manager','peoplesoft update manager', 'pum', 'ses', 'data mover','hp-ux 11.31',
    'changeassistant', 'integrationbroker', 'applicationdesigner','configuration manager', 'peoplesoft update manager',
    'Red hat Enterprise Linux','app package', 'application engine', 'people code', 'sqr', 'bip', 'ps query',
    'peoplesoft application designer','oracle 11g','peoplesoft- erp', 'ps security', 'application package', 
    'process scheduler', 'workflow notification', 'file layout', 'data mover', 'xml publisher',
    'integration broker', 'component interface', 'web services', 'workflow notifications', 'awe', 'peoplecode',
    'fscm and hcm applications','sql server','db2','peoplesoft security','oracle sql developer',
    'java full stack development', 'ariba', 'power bi','t-sql','sql server reporting tools',
    'sql server integration services', 'sas', 'r', 'python','t-sql', 'aws rds', 'mariadb', 'sql server management studio',
    'razorsql', 'heidisql', 'rstudio', 'tableau', 'excel', 'sybase ase 15.7 server','ms-sql','oracle','devops',
    'pl/sql-oracle', 'pentaho data integration', 'linux','centos','ubuntu','vmware workstation',
    'putty','db solo','dell sonic global vpn client','spoon','winscp', 'pig','hive','sqoop','hbase','impla','scala',
    'core java','html','css','bootstrap','c-language', 'ssis','sql server analysis services', 
    'sql server reporting services', 'report builder','crm','ssms','ms visual studio 2013', 'ms office suite',
    'numpy','pandas','matplotlib','teradata', 'aws redshift','sql server management studio','ms sql server',
    'microsoft business intelligence tools','workday hcm', 'core connectors picof',
    'document transformation and workday studio', 'eib', 'workday web services', 'workday security','xml', 'sql', 
    'basic shell scripting', 'informatica 9 &10', 'talend', 'putty', 'appworx', 'maestro', 'winscp', 
    'reporting and integrations', 'xslt', 'mvel web services soap & rest', 'workday studio','core hr', 'benefits',
    'compensation', 'time tracking', 'absence management', 'studio', 'calculated fields', 'change deduction', 
    'reportwriting', 'integration', 'sup orgs', 'business object', 'workday', 'peoplesoft','workday advanced report writer', 'picof', 'workday web services','x-path','eib inbound',
    'soap', 'xsd', 'report writer', 'eib and workday studio', 'core connector', 'document transformation',
    'crystal reports11', 'xmlp', 'dt and studio', 'report writing', 'integrations','time tracking', 'absence management',
    'document transformer', 'birt& business objects','core hcm', 'workday reports','business processes', 'notifications',
    'alerts', 'security', 'integrations-eib', 'reports', 'calculated fields', 'business process', 'dt','basic studio',
    'birt', 'payroll','talent','recruiting','calc fields','ccw', 'ccb','wd-soap','wd-rest','staffing','domain security',
    'workday hcm and integrations', 'zenefits','workday report writer', 'oxygen', 'eclipse','lms','payment connectors', 
    'mvel web services soap & rest','app engine', 'ci.xml'        
]
    
def extract_skills(input_text):
    stop_words  = set(nltk.corpus.stopwords.words('english'))
    word_tokens = nltk.tokenize.word_tokenize(input_text)
    #print(word_tokens)
    
    #remove the stop words
    filtered_tokens = [w for w in word_tokens if w not in stop_words]
    #print(filtered_tokens)
    
    #remove the punctuation
    filtered_tokens = [w for w in word_tokens if w.isalpha()]
    #print(filtered_tokens)
    
    #generating bigrams & trigrams
    bigrams_trigrams = list(map(' '.join,nltk.everygrams(filtered_tokens,2,3)))
    #print(len(bigrams_trigrams))
    
    #create a list
    found_skills = []
    
    #search for each token in our skills db
    for token in filtered_tokens:
        if token.lower() in skills_db:
            found_skills.append(token)
            
    #search for each bigram and trigram in our skills db
    for ngram in bigrams_trigrams:
        if ngram.lower() in skills_db:
            found_skills.append(ngram)
            
    #searching in df for words from skills_db_complete
    #this code will handle values like these and pick them as whole windosw7/8/10
    for i in range(0,len(df)):
        for word in skills_db_complete:
            each_row_text = df.loc[i]['Text'].lower()
            if re.search(r"\b"+(word)+r"\b",each_row_text) and ((re.search(r"\\",each_row_text)) or (re.search(r",",each_row_text)) or (re.search(r"\|",each_row_text))):
                #this was done to remove long sentences having data like version 8.48/9/10/11/12
                #coz this will pick the entire sentence if it has version 8.48
                str_row_data = df.loc[i]['Text'].split()
                len_str_row_data = len(str_row_data)
                #print(len_str_row_data)
                if len_str_row_data < 3:
                    found_skills.append(df.loc[i]['Text'])
            else:
                continue
           
    return found_skills

#stopwords from nltk library
stop_words = stopwords.words('english')
#adding stop words like name & colon to remove while extracting name
stop_words.append('name')
stop_words.append(':')
stop_words.append('\uf041')
stop_words.append('-')

def highlight_duplicates(objTable):
    return ['background-color: green']*len(objTable) if objTable.Email else ['background-color: red']*len(objTable)
    
    

# table having data from resume
final_table = pd.DataFrame()

############################ execution of code starts from here

st.title('Resume Data')

uploaded_file =  st.sidebar.file_uploader('Upload Resume Here',type=['docx','doc','pdf'], accept_multiple_files=True)
#st.write(uploaded_file)

                                 
if uploaded_file is not None: 
    
    list_all_files = []    
    set_file_name  = set()
    for item in uploaded_file:
        #st.write(item)
        list_all_files.append(item.name)
        set_file_name.add(item.name)
                
    #converting to list
    list_unique_filenames  = list(set_file_name)
    #st.write(list_unique_filenames)
    
        
    name_list       = []
    phone_list      = []
    email_list      = []
    education_list  = []
    skill_list      = []
    experience_list = []
    filename_list   = []
    filename_wo_ext = []
    
    #st.write(list_unique_filenames)
    #st.write(uploaded_file)
        
    for item in uploaded_file:
        
        fileName = item.name  
        #st.write("file_uploader", fileName)
        
        #if item_unique_filename == fileName and insert_flag == False:
            
        fileName_ext = fileName.split('.')
        #this was done coz if more than 1 dot is present in the filename
        #then we need to take the last split as extension
        len_split_fileName = len(fileName_ext) 
        file_ext_index = len_split_fileName - 1
        
        if fileName_ext[file_ext_index] == 'pdf':
            #st.write(fileName)
            #extracting & processing data from pdf file
            #creating pdf filereader object
            pdf_reader = PyPDF2.PdfFileReader(item)
            extracted_data_pdf = readFromPdfFile(pdf_reader)
            #st.write(len(extracted_data_pdf))
            
            #creating list by splitting on basis of newline
            list_data = process_data(extracted_data_pdf)
            #st.write(list_data)
            
            #adding filename w/o extension
            filename_wo_ext.append(fileName.replace('.pdf',''))
            
        elif fileName_ext[file_ext_index] == 'docx':
            #st.write(fileName)
            #this will save the uploaded file in the same folder where the code file is present
            # ie resume_extraction.py
            with open(fileName, 'wb') as fdocx:
                fdocx.write(item.getbuffer())
                
            extracted_data_docx = readFromDocxFile(fileName)
            #st.write(extracted_data_docx)
            
            list_data = process_data(extracted_data_docx)
            #st.write(list_data)
            
            #adding filename w/o extension
            filename_wo_ext.append(fileName.replace('.docx',''))
            
        elif fileName_ext[file_ext_index] == 'doc':
            
            #st.write(fileName)
            #saves the uploaded doc file               
            with open(fileName, 'wb') as fdoc:
               fdoc.write(item.getbuffer())
               
            filePath = 'C:\\Users\\Admin.DESKTOP-ISGPM4M\\.spyder-py3\\'+fileName
            
            converted_docxFileName = fileName.replace('.doc','.docx')
            #this will convert the doc file to docx
            saveAsDocx(filePath)
            #will read from converted to docx file
            extracted_data_converted_docx = readFromDocxFile(converted_docxFileName)
            #st.write(extracted_data_converted_docx)
            
            list_data = process_data(extracted_data_converted_docx)
            #st.write(list_data)
            
            #adding filename w/o extension
            filename_wo_ext.append(fileName.replace('.doc',''))
            
        else:
            st.write('file format not acceptable\nOnly files with extension as doc,docx,pdf are acceptable')
            
        #saving list data extracted from resume in dataframe
        df = pd.DataFrame()
        df['Text'] = list_data
        
        #removal of stop words from dataframe
        df['Filtered Text'] = df['Text'].apply(lambda x: ' '.join([word.strip() for word in x.split() if word.lower() not in (stop_words)]))
        #st.write(df)
        
        #removing multiple spaces in dataframe
        df['Filtered Text'] = df['Filtered Text'].apply(removeMultipleSpaces)
        df['Filtered Text'] = df['Filtered Text'].str.strip()
        #st.write(df)
        ##################### extraction of name ###################################
        
        #converting df first 3 rows into a list
        #coz name is present only in first 3 rows
        resume_data_list = []
        for i in range(0,3):
            data = df.iloc[i]['Filtered Text']
            resume_data_list.append(data)
            
        #resume_data_list      
        names = extract_names(resume_data_list)
        
        names[0] = names[0].replace('Name', '')
        names[0] = names[0].replace('NAME', '')
        names[0] = names[0].replace('-', '')
        names[0] = names[0].replace(':', '')
        names[0] = names[0].replace('1', '')
        names[0] = names[0].strip()                
        
         #will add the first element of name to the namelist
        if names:
            appendFlag = False
            for nm in names:
                if nm and appendFlag == False:
                    #this was done for pdf file special case
                    #where name was coming in 3rd row
                    nm = nm.replace('Name:','')
                    name_list.append(nm)
                    appendFlag = True
                else:
                    pass
        else:
            name_list.append('None')
        
        resume_text = ' '.join(df['Filtered Text'])
        ############################# Extraction of contact no ######################
    
        phone_number = extract_phone_number(resume_text)
        #st.write(phone_number)
        if len(phone_number):
            only_phone_list = []
            for num in phone_number:
                #print("@@@@@@@@@",num)
                if re.search(r'^\d{10}$', num):
                    only_phone_list.append(num)
                else:
                    pass 
            
            if len(only_phone_list):
                phone_str = ', '.join(only_phone_list)
                phone_list.append(phone_str)
            else:
                phone_list.append('None')
        else:
            phone_list.append('None') 
            
        ######################### extraction of email ############################
        
        emails = extract_emails(resume_text)
        
        if emails:
            email_str = ', '.join(emails)
            email_list.append(email_str)
        else:
            email_list.append('None')
            
        ####################### Extraction of Education ##########################
        
        education_information = extract_education()
        if len(education_information):
            list_educational_info =  list(education_information) #converting to list
            str_education_info = ', '.join(list_educational_info) #converting to string
            education_list.append(str_education_info)
        else:
            education_list.append('None')
        
        ############################# extraction of skills ########################   
    
        skills_set = extract_skills(resume_text)
        #st.write(skills_set)
        
        # this will remove duplicate case insensitive words like peoplesoft, Peoplesoft
        set_skill_set = set({v.casefold(): v for v in skills_set}.values())
        #st.write(set_skill_set)
        
        #converting the set to string and adding to final_table
        final_skill_set = ", ".join(set_skill_set)
    
        if final_skill_set:
            skill_list.append(final_skill_set)
        else:
            skill_list.append(None)
            
        ####################### extracting work experience ##############
        
        #extracts entire sentence containing experience
        list_exp_years = extract_yearsofexperience()
        #st.write(list_exp_years)
        
        #extracting numbers from years of experience sentence
        if len(list_exp_years):
            list_numbers_exp = extract_numbers(list_exp_years)
            #st.write(list_numbers_exp)
            
            #if multiple numbers for experience convert it to integer
            #take sum of multiple numbers eg 4 years of exp and 3 years of exp = 7 years of exp
            if(list_numbers_exp):
                #print(list_num_exp_int)
                list_num_exp_int = [float(i) for i in list_numbers_exp]
                #print("@@",list_num_exp_int)
                #print(sum(list_num_exp_int))
                experience_list.append(sum(list_num_exp_int))
            else:
                experience_list.append(0.0)
        else:    
            experience_list.append(0.0)
                    
    ############# final dataframe with resume data ########################
               
    final_table['Name']              = name_list
    final_table['Contact No']        = phone_list
    final_table['Email']             = email_list
    final_table['Education Details'] = education_list   
    final_table['Skills']            = skill_list
    final_table['Experience Years']  = experience_list
    final_table['Filename']          = filename_wo_ext
    
    
    if final_table.empty == False:
        st.success('Files Uploaded successfully')
                
        # will display float values with 2 decimal places    
        st.dataframe(final_table.style.format(subset=['Experience Years'], formatter="{:.2f}"))
        #st.dataframe(final_table)
                         
        #download for table data in csv format
        csv = convert_df(final_table)    
        st.download_button("Click Here to Download", csv, "resume_data.csv", "text/csv", key='download-csv') 
        
        duplicate = final_table[final_table.duplicated(keep = 'last')]
        if not duplicate.empty:
            st.info('Duplicate files')
            st.dataframe(duplicate)
        
else:
    pass
    
    
   
    
    
