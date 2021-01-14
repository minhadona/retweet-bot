#!/usr/bin/env python
# coding: utf-8

# ##    Bot by: @minhadona
#     First Release: 1 jan 2021 
#     big text letters font generator: https://fsymbols.com/generators/tarty/

# In[151]:


def main():
    
    checking = checks_if_necessary_folders_exist_otherwise_create_them()
    checking = checks_if_necessary_files_exist_otherwise_create_them()
    if not type(checking) is dict:
        print('checking: '+str(checking))
        raise TypeError('Error: necessary files cannot be created or validated')
        
    # ----------------------------------------------------------------------------------
    # ---------------- populating dictionary with API credentials from json ------------
    # ----------------------------------------------------------------------------------
    
    with open(useful_variables.credentials_json) as credentials_file:
        credentials = json.load(credentials_file)
        #logging('credential value: '+ str(credentials))
                             
    pymsgbox.alert('Starting bot!', 'Starting bot',timeout=5000)
    logging("░██████╗████████╗░█████╗░██████╗░████████╗██╗███╗░░██╗░██████╗░")
    logging("██╔════╝╚══██╔══╝██╔══██╗██╔══██╗╚══██╔══╝██║████╗░██║██╔════╝░")
    logging("╚█████╗░░░░██║░░░███████║██████╔╝░░░██║░░░██║██╔██╗██║██║░░██╗░")
    logging("░╚═══██╗░░░██║░░░██╔══██║██╔══██╗░░░██║░░░██║██║╚████║██║░░╚██╗")
    logging("██████╔╝░░░██║░░░██║░░██║██║░░██║░░░██║░░░██║██║░╚███║╚██████╔╝")
    logging("╚═════╝░░░░╚═╝░░░╚═╝░░╚═╝╚═╝░░╚═╝░░░╚═╝░░░╚═╝╚═╝░░╚══╝░╚═════╝░")
    
    try: 
        api = authenticating(credentials)
        
        with open(useful_variables.attributes_json) as json_file:
            dict_attributes_info = json.load(json_file)
            
        words = dict_attributes_info["words_to_search"]
        logging('these are the words we r gonna search: '+str(words))

        for searched_word in words:

            for tweet in tweepy.Cursor(api.search, q = searched_word).items(1100):

                dict_tweets_info = {
                "created_at": [],
                "tweet_ID": [],
                "user": [],
                "tweet_content": [],
                "place": [],
                "language": [],
                "source": [] 
            }

                with open(useful_variables.control_json) as json_file:
                    tweets_status = json.load(json_file)
                    if tweets_status["amount_of_tweets"] == 999 and tweets_status['current_date'] == date:
                        sys.exit('DAILY LIMIT REACHED, CANT RETWEET MORE THAN 1000 TWEETS')

                                       
                valid_tweet = validate_and_retweet_tweet(api,
                                                         tweet,
                                                         dict_tweets_info,
                                                         dict_attributes_info,
                                                         searched_word)

                if type(valid_tweet) is dict:
                    logging('VALID TWEET !!!!! Ok, we received a dict as return, we may export the results now')
                    export_infos_to_csv(valid_tweet)
                    write_json_and_updates_value(useful_variables.control_json,incrementa_contagem_de_falha=False)

                elif type(valid_tweet) is int:
                    logging('Tweet is not valid, analyzing return:: '+str(valid_tweet))
                    cases={
                        -1 : "didn't found the searched_word on tweet.text it self",
                        -2 : "invalid language (japanese, korean, arabic etc problems to recognize the searched word)",
                        -3 : "you have already retweeted this Tweet",
                        -4 : "RateLimitError",
                        -5 : "tweet was made by the bot's account, we can't retweet stuff made by us",
                        -6 : "tweet is not in desired language"
                    }
                    logging(cases.get(valid_tweet,"Invalid return"))
                    write_json_and_updates_value(useful_variables.control_json,
                                                 incrementa_contagem_de_falha=True)
                    continue

                else:
                    logging('Unexpected return for validate_and_retweet_tweet different than dict or int!! content: '+str(valid_tweet) +'type of return: '+str(type(valid_tweet)))
                    write_json_and_updates_value(useful_variables.control_json,
                                                 incrementa_contagem_de_falha=False)

                logging("Waiting 2 min to retrieve another tweet cuz we like safety")
                time.sleep(60*2) # sleep 2 min, so we dont reach the limit 100 tweets per hour
    
    except Exception as error:
        if 'status code = 401' in str(error):
            logging('INVALID CREDENTIALS, STOPPING BOT')
            pymsgbox.alert('INVALID CREDENTIALS on jsoOoooOOooOon!!!', 'Stopping bot',timeout=15000)
            want_to_insert_credentials = pymsgbox.confirm('Would you like to insert your credentials here? \n or... update credentials on \\bot_files\\controls\\credentials.json', 'INSERT CREDENTIALS?', ["Yes", "No, I'll update the json file"])
            if want_to_insert_credentials == 'Yes':
                receive_credentials_overwrite_credential_json()
                main()
        else:
            logging('Unkown error:' +str(error))
    

    logging('███████╗███╗░░██╗██████╗░  ░█████╗░███████╗  ██╗░░░░░░█████╗░██████╗░')
    logging('██╔════╝████╗░██║██╔══██╗  ██╔══██╗██╔════╝  ██║░░░░░██╔══██╗██╔══██╗')
    logging('█████╗░░██╔██╗██║██║░░██║  ██║░░██║█████╗░░  ██║░░░░░███████║██████╔╝')
    logging('██╔══╝░░██║╚████║██║░░██║  ██║░░██║██╔══╝░░  ██║░░░░░██╔══██║██╔═══╝░')
    logging('███████╗██║░╚███║██████╔╝  ╚█████╔╝██║░░░░░  ███████╗██║░░██║██║░░░░░')
    logging('╚══════╝╚═╝░░╚══╝╚═════╝░  ░╚════╝░╚═╝░░░░░  ╚══════╝╚═╝░░╚═╝╚═╝░░░░░')
    
    pymsgbox.alert('$$$$$$$$$$$$$$ \n END OF LAP\n $$$$$$$$$$$$$', 'End of times',timeout=40000)


# In[152]:


def authenticating(credential):
    logging('\n\nfunction>>>>>authenticating')
     
    """   
    █ █▄░█
    █ █░▀█    
    """
        # credential         • <dictionary>                 ○ its keys will be used to authenticate
        
    """
    █▀█ █░█ ▀█▀
    █▄█ █▄█ ░█░
    """
        # api                • <class 'tweepy.api.API'>     ○ authenticated api
   
    auth = tweepy.OAuthHandler(credential["api_key"], credential["api_secret"])
    auth.set_access_token(credential["access_token"], credential["access_token_secret"])

    api = tweepy.API(auth,wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    
    return api


# In[153]:


def validate_and_retweet_tweet(api, tweet, dict_tweets_info, dict_attributes_info, searched_word):
    logging('\n\nfunction>>>>>validate_and_retweet_tweet')
    
    """   
    █ █▄░█
    █ █░▀█    
    """
        # api                • <class 'tweepy.api.API'>    ○ authenticated api
        # tweet              • <tweet object>              ○ one single tweet object and its attributes 
        # dict_tweets_info   • <dictionary>                ○ empty, to be filled with informations from this tweet object
        # searched_word      • <string>                    ○ seeking term (will be used here to validate the inner content of the tweet) 
    
    """
    █▀█ █░█ ▀█▀
    █▄█ █▄█ ░█░
    """
        # -1           ○ didn't found the searched_word on tweet.text it self 
        # -2           ○ forbidden language (japanese, korean, arabic etc problems to recognize the searched word)
        # -3           ○ you have already retweeted this Tweet
        # -4           ○ RateLimitError
        # -5           ○ tweet was made by the bot's account, we can't retweet stuff made by us 
        # -6           ○ tweet is not in desired language
        # dict         ○ in a valid situation, returns a populated dictionary containing this tweet's data 

    try: 

        logging('appending infos retrieved to dictionary')
        dict_tweets_info['created_at'].append(str(tweet.created_at))
        dict_tweets_info['tweet_ID'].append(str(tweet.id))
        dict_tweets_info['user'].append(str(tweet.user.screen_name))
        dict_tweets_info['tweet_content'].append((tweet.text))
        dict_tweets_info['place'].append(str(tweet.place))
        dict_tweets_info['language'].append(str(tweet.lang))
        dict_tweets_info['source'].append(str(tweet.source_url).replace("http://twitter.com/download/",""))
    
        logging('----------------------------------------')
        logging('raw dict_tweets_info after appending: \n '+str(dict_tweets_info))
        logging('----------------------------------------')
        
    
    # ---------------------------------------------------------------------------------------------------------
    # --------------------------------- FILTERING BEFORE RETWEET ----------------------------------------------
    # ---------------------------------------------------------------------------------------------------------
    
        logging('validate_and_retweet_tweet(): better filtering BEFORE retweet')
        
        string_lang_content = "".join(dict_tweets_info['language'] )  # turns list into string to compare
        # -----------------------------------------------------------------------------------------------------
        # ---------------------------- checking if it's in one of the ENFORCED languages ----------------------
        # -----------------------------------------------------------------------------------------------------        
        if dict_attributes_info["restrict_tweets_to_these_languages"]:
            # only comes here if list is not empty! we have to enforce the languages on the list
            logging('these are the current enforced languages: '+str(dict_attributes_info["restrict_tweets_to_these_languages"]))
            if not string_lang_content in dict_attributes_info["restrict_tweets_to_these_languages"]:
                logging('tweet is not in enforced languages list, we wont retweet any other language!')
                return -6
            else: 
                logging('we have restrictions and we are ok, language of this tweet is: '+string_lang_content)        
        else:
            logging('RESTRICTION LIST IS EMPTY, WE DONT NEED TO ENFORCE ANY LANGUAGE')
        # -----------------------------------------------------------------------------------------------------
        # ---------------------------- checking if it's in one of the FORBIDDEN languages ---------------------
        # -----------------------------------------------------------------------------------------------------
        
        if string_lang_content in dict_attributes_info["forbidden_languages_to_retweet"]:
            logging('dumb robot, tweet is not in an understandable language so its content will be wrongly evaluated, we stop here')
            return -2
        else: 
            logging('not in any forbidden language! language is actually:'+string_lang_content)
            
        # -----------------------------------------------------------------------------------------------------
        # ---------------------------- checking if the searched word really is on tweet content ---------------
        # -----------------------------------------------------------------------------------------------------

        string_tweet_content = "".join(dict_tweets_info['tweet_content'] ) # turns list into string to compare
        if not searched_word in string_tweet_content.lower():
            logging('we havent found '+ searched_word + ' on tweet content')
            # NO WAY it's gonna retweet something that has NOT the word on the text
            return -1
        
        # -----------------------------------------------------------------------------------------------------
        # ------------------------- checking if this tweet's user is also the authenticated user --------------
        # -------------------------------- (so we dont retweet our own tweets) --------------------------------
        
        my_user_object = api.me()
        if str(my_user_object.screen_name) == str(tweet.user.screen_name):
            logging('you are @'+ str(my_user_object.screen_name))
            logging('this tweet was made by yourself using your bot profile or is an old RETWEET!! both cases we wont retweet it again')
            return -5
        else:
            logging('this user is not you! you: '+ str(my_user_object.screen_name) + ' VS the tweeter: '+ str(tweet.user.screen_name) +', that s great')
        
    # ---------------------------------------------------------------------------------------------------------
    # ---------------------------------- RETWEET ACTION ! -----------------------------------------------------
    # ---------------------------------------------------------------------------------------------------------
        logging('retweeting ←←←←←←←←←←←←←')
        api.retweet(tweet.id)
        logging('→→→→→→→→→→→→→ retweeted') # if an exception is raised during retweet method, we wont arrive here
        return dict_tweets_info
    
    except tweepy.TweepError as e: 
        if e.api_code == 327:
            logging('Exception Code 327: You have already retweeted this Tweet')
            return -3
        
    except tweepy.RateLimitError as e:
        logging('RateLimitError')
        logging('Unknown error: '+str(e))
        logging('according to internet, sleeping for 15 min should solve...')
        time.sleep(60 * 15)  # we saw rate limit is ignored after 15 min ??? ///not confirmed hypothesis///
        return -4


# In[154]:


def write_json_and_updates_value(path, incrementa_contagem_de_falha=False, inicializar = False):
    logging('\n\nfunction>>>>>write_json_and_updates_value')
    
    """   
    █ █▄░█
    █ █░▀█    
    """
        # path                           • <string>          ○ control json path
        # incrementa_contagem_de_falha   • <bool>            ○ boolean flag to update or not a specific key
        # inicializar                    • <bool>            ○ boolean flag to reset (set to 0) or not all the keys
    
    now = datetime.now()
    current_date = now.strftime("%d/%m/%Y")

    # try to read from file
    try:
        with open(path) as json_file:
            tweets_status = json.load(json_file)

    except Exception as e:
        print(str(e))

    # write on file
    # if our current date is the same, increase amount of tweets.
    # if our current date is different, amount is ZERO !!!!!!!!!!!!!!!!!!!!

    if inicializar or tweets_status['current_date'] != current_date: 
        logging('different dates, OR initializing, so we need to change the current_date value and also turn into 0 all the values')
        with open(path, 'w') as f:
            try:
                content = {"current_date": current_date,
                           "amount_of_tweets": 0,
                           "total_amount_including_failure":0}
                json.dump(content, f)

            except json.JSONDecodeError:
                logging('decode error but will try raw writing')
                f.write(contenting)
    else: 
        logging('same date!! so, just change the value of tweetts')
        if not incrementa_contagem_de_falha:
                logging('increases both keys , the including failure and the sucessed amounts')
                #vai incrementtar o total com falhas tb + o total dos sucessos
                tweets_status["amount_of_tweets"] = tweets_status["amount_of_tweets"]+1 
                tweets_status['total_amount_including_failure'] = tweets_status['total_amount_including_failure']+1
                with open(path, 'w') as f:
                    try:
                        json.dump(tweets_status, f)
                    except json.JSONDecodeError:
                        logging('decode error but will try raw writing')
                        f.write(contenting)
                    
        elif incrementa_contagem_de_falha:
                # vai incrementar SOMENTE chave com total de tweets, independente de ter falhado ou nao
                logging('INCREMENTANDO CHAVE DE CONTAGEM TOTAL DE TWEETS')
                     # increasing amount of the ones who failure 
                tweets_status['total_amount_including_failure'] = tweets_status['total_amount_including_failure']+1

                with open(path, 'w') as f:
                    try:
                        json.dump(tweets_status, f)

                    except json.JSONDecodeError:
                        logging('decode error but will try raw writing')
                        f.write(contenting)


# In[155]:


def export_infos_to_csv(valid_tweet):
    logging('\n\nfunction>>>>>exporting_infos_to_csv')
        
    """   
    █ █▄░█
    █ █░▀█    
    """
        # valid tweet        • <dictionary>          ○ dictionary holding all informations we retrieved from one specific tweet
    
    # -------------------------------------------------------------------------------------------------------------
    # ------------------------- fetch today's DATE in DD/MM/YYY format and turns into DD-MM-YYYY ------------------
    # -------------------------------------------------------------------------------------------------------------
    
    now = datetime.now()
    timestamp = now.strftime("%d/%m/%Y").replace("/","-").replace(':',"-").replace(',','--').replace(" ","")

    CSV_path = useful_variables.exported_data_folder+'\\dados_'+timestamp+'.csv'
    logging("today's CSV path: "+str(CSV_path))

    logging('valid_tweet : '+str(valid_tweet))

    # -------------------------------------------------------------------------------------------------------------
    # -------- to exclusively append tweet's informations, we CANT append dict directly, otherwise the function ---
    # ------------- will append header (dict keys) row + informations (dict values) row for EVERY tweet -----------
    # --------- so we turn the dict values into a list and we only append header if it's a new CSV (new day) ------
    # -------------------------------------------------------------------------------------------------------------
    
        # -----------------------------------------------------------------------------------------------------------
        # ---------------------------------- turning dict values into a list ----------------------------------------
        # -----------------------------------------------------------------------------------------------------------
        
    dict_values_in_list_version = []
    for key, value in valid_tweet.items():
        dict_values_in_list_version.append("".join(value))

        # -----------------------------------------------------------------------------------------------------------
        # -------- forcing Tweet ID to be written as string on sheet, so it doesnt truncate as scientific notation --
        # -----------------------------------------------------------------------------------------------------------
        
    dict_values_in_list_version[1] = '\''+dict_values_in_list_version[1]

    logging('dict_values_in_list_version: '+str(dict_values_in_list_version))

        # -----------------------------------------------------------------------------------------------------------
        # --------- if today's CSV already exists, we will append only this specific tweet's DETAILS to file --------
        # ----------------- elseways we append the header (creating a new file) -------------------------------------
        # ------------------- and THEN append current tweet's details normally --------------------------------------
        # -----------------------------------------------------------------------------------------------------------
    
    if not os.path.exists(CSV_path):
        logging('today s csv does not exist yet, creating it and appending header')
        header_csv = ['created_at','tweet_ID','user','tweet_content','place','language','source'] 
        with open(CSV_path, "a") as file:
            wr = csv.writer(file)
            wr.writerow(header_csv)
            
    with open(CSV_path, "a",encoding="utf-8", newline='') as file:
        logging('writing tweet details on CSV file')
        wr = csv.writer(file)
        wr.writerow(dict_values_in_list_version)


# In[156]:


def logging(text_to_log=""):
    
    # -----------------------------------------------------------------------------------------------------------
    # ------------------- converts into string the parameter we want to write on log file -----------------------
    # ------------------------- just in case we received another variable type ----------------------------------
    # -----------------------------------------------------------------------------------------------------------
    
    text_to_log = str(text_to_log)
    
    # -----------------------------------------------------------------------------------------------------------
    # --------------------------- fetchs timestamp to append within received text -------------------------------
    # ---------- fetchs current date to create new log file or append to the current one ------------------------
    # -----------------------------------------------------------------------------------------------------------

    now = datetime.now()
    date = now.strftime("%d/%m/%Y").replace("/","-")
    timestamp = now.strftime("%d/%m/%Y, %H:%M:%S")

        # -----------------------------------------------------------------------------------------------------
        # ---- retrieves directory where our robot is running and concatenate the path to the current day's ---
        # -----------------------------------------------------------------------------------------------------
    
    log_path = useful_variables.logs_folder+'\\log_'+date+'.txt'
    
        # -----------------------------------------------------------------------------------------------------
        # ----- appending to file of the day: timestamp + parameter's content ---------------------------------
        # -----------------------------------------------------------------------------------------------------

    with open(log_path, 'a+',encoding="utf-8") as log_file:
        log_file.write(timestamp+ ' - ' + text_to_log+'\n')
    
        # -----------------------------------------------------------------------------------------------------
        # ------ printing on console ----------------------------------------------------------------------------
        # -----------------------------------------------------------------------------------------------------
    print(timestamp+ ' - ' + text_to_log)


# In[157]:


def translate_special_text_to_ascii(original_text):
    translated_text = ''

    for character in original_text:
        if ord(character) >= 128:
            translated_text = translated_text + '"Chr(' + str(ord(character)) + ')"'
        else:
            translated_text = translated_text + character

    return translated_text


# In[158]:


def receive_credentials_overwrite_credential_json():                
    logging('\n\nfunction>>>>>receive_credentials_overwrite_credential_json')
    
    new_api_key = pymsgbox.prompt('Insert your API KEY', default='3x4mPL3-j13j2o38s09dsaf')
    new_api_secret = pymsgbox.prompt('Insert your API SECRET', default='3x4mPL3-j13j2o38s09dsaf')
    new_bearer_token = pymsgbox.prompt('Insert your BEARER TOKEN', default='3x4mPL3-j13j2o38s09dsaf')
    new_access_token = pymsgbox.prompt('Insert your ACCESS TOKEN', default='3x4mPL3-j13j2o38s09dsaf')
    new_access_token_secret = pymsgbox.prompt('Insert your ACCESS TOKEN SECRET', default='3x4mPL3-j13j2o38s09dsaf')
 
    with open(useful_variables.credentials_json, 'w') as f:
        try:
            content = {"api_key" : new_api_key,
                       "api_secret" : new_api_secret,
                       "bearer_token" : new_bearer_token,
                       "access_token" : new_access_token,
                       "access_token_secret" : new_access_token_secret}
            json.dump(content, f)

        except json.JSONDecodeError:
            logging('decode error but will try raw writing')
            f.write(contenting)


# In[159]:


def checks_if_necessary_folders_exist_otherwise_create_them():
    logging('\n\nfunction>>>>>checks_if_necessary_folders_exist_otherwise_create_them')
    # ----------------------------------------------------------------------------------------------
    # ---------------------  CREATES INTO SCRIPT DIRECTORY ALL NECESSARY FOLDERS  ------------------
    # ----------------------------------------------------------------------------------------------
    
    try:
        if not os.path.exists(useful_variables.logs_folder):
            pymsgbox.alert(text="Creating logs' folder", title='Setting bot up', button='OK',timeout=4500)
            os.makedirs(useful_variables.logs_folder)
            logging("Creating logs' folder")
        else:
            logging(str(useful_variables.logs_folder) + ' already exists')

        if not os.path.exists(useful_variables.controls_folder):
            pymsgbox.alert(text='Creating controls folder', title='Setting bot up', button='OK',timeout=4500)
            os.makedirs(useful_variables.controls_folder)
            logging("Creating controls folder")
        else:
            logging(str(useful_variables.controls_folder) + ' already exists')

        if not os.path.exists(useful_variables.exported_data_folder):
            pymsgbox.alert(text='Creating exported_data folder', title='Setting bot up', button='OK',timeout=4500)
            os.makedirs(useful_variables.exported_data_folder)
            logging("Creating exported_data folder")
        else:
            logging(str(useful_variables.exported_data_folder) + ' already exists')
    
    except Exception as error:
        logging('Unknown error: '+str(error))


# In[160]:


def checks_if_necessary_files_exist_otherwise_create_them():
    logging('\n\nfunction>>>>>checks_if_necessary_files_exist_otherwise_create_them')
    
    # -1    invalid attributes: some value on attributes dict is not list type ('a' :   ['LIST','LIST'])
    # -2    invalid attributes: exclude a language from retweeting and ask to retweet the same language is contraditory
    # dict  success to create and validate all json files

    # ------------------------------------------------------------------------------------------
    # ---------- checking if control json exists, otherwise we create it -------------------
    # ------------------------------------------------------------------------------------------
    control_json = useful_variables.control_json
    if not os.path.exists(control_json):
        logging("control json not found, gotta create it")
        write_json_and_updates_value(control_json,
                                     incrementa_contagem_de_falha = False,
                                     inicializar = True)
    else:
        logging(str(control_json) + ' already exists')

    # ------------------------------------------------------------------------------------------    
    # ---------- checking if credentials json exists, otherwise we create it -------------------
    # ------------------------------------------------------------------------------------------
    
    credentials_json = useful_variables.credentials_json
    if not os.path.exists(credentials_json):
        logging("credentials json not found, gotta create it using a template")
        
        with open(credentials_json, 'w') as f:
            try:
                content_template = {"api_key" : "examplen9masss23423553252ffffffe",
                           "api_secret" : "examplefa1asfsafsafsa32434fdfsfsdfddsfsfddfdfsfd",
                           "bearer_token" : "exampleAAAAAAAAAADFDSFGDDGGDAGDFHDFHBV424G4023fe032402320F242WER355W31tg21e454F4E4ER4Esfdsdfdfs",
                           "access_token" : "example13371788gfdfgdfgdfgd344544gdfgfdsj5jytjjy",
                           "access_token_secret" : "examplect42gdfhf5y66hsvbbgfhC91Rhfghgf45t4555552432324235"}
                json.dump(content_template, f)

            except json.JSONDecodeError:
                logging('decode error but will try raw writing')
                f.write(content_template)
                
    else:
        logging(str(credentials_json) + ' already exists')
        
    # ------------------------------------------------------------------------------------------    
    # ---------- checking if attributes json exists, otherwise we create it --------------------
    # ------------------------------------------------------------------------------------------
    
    attributes_json = useful_variables.attributes_json
    
    content_template = {"words_to_search" : ['zolpidem','ambien'],
                           "users_to_not_retweet" : ['user1','user2'],
                           "forbidden_languages_to_retweet" : ['ja','ko','und','fa','ar'],
                           "restrict_tweets_to_these_languages" : [] }
    
    if not os.path.exists(attributes_json):
        logging("credentials json not found, gotta create it using a valid template")
        
        with open(attributes_json, 'w') as f:
            try:
                
                json.dump(content_template, f)

            except json.JSONDecodeError:
                logging('decode error but will try raw writing')
                f.write(contenting)
                
            finally:
                return content_template
                
    else:
        # ---------------- if file exists already, we will validate any inconsistency ---------
        
        logging(str(attributes_json) + ' already exists, let s validate the dictionary')
        with open(useful_variables.attributes_json) as json_file:
            dict_attributes_info = json.load(json_file)
            
            # ----------- all values have to be LIST type -----------------------
            
            for key, value in dict_attributes_info.items():
                if not type(value) is list:
                    pymsgbox.alert('YOU VE CHANGED THE TYPE OF SOME VALUE ON JSON! \nPLEASE, DELETE THE FILE, restart the bot AND FOLLOW THE INITIAL TEMPLATE we will create! \nALL VALUES HAVE TO BE LIST TYPE! \n\nfile is on \\bot_files\\controls\\attributes.json', 'BOT CANNOT START WITH INVALID ATTRIBUTES')
                    logging('YOU VE CHANGED THE TYPE OF SOME VALUE ON JSON! PLEASE, DELETE IT AND FOLLOW THE INITIAL TEMPLATE')
                    return -1
            
            # ----------- cant have same value on _restrict and _forbiden -------
            
            for language in dict_attributes_info['restrict_tweets_to_these_languages']:
                if language in dict_attributes_info['forbidden_languages_to_retweet']:
                    pymsgbox.alert('you cant ask us to only retweet things in the same language you WANT TO PROHIBIT retweeting! \nPLEASE UPDATE JSON FILE ON \\bot_files\\controls\\attributes.json and try again','what?')
                    logging('you cant ask us to only retweet things in the same language you WANT TO PROHIBIT retweeting')
                    return -2
                
        return content_template


# In[161]:


import import_ipynb
import useful_variables
import tweepy
import time
from datetime import date, datetime 
import os
import pymsgbox 
import pandas as pd
import json
import sys
import csv

main()


# In[ ]:




