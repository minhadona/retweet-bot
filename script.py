#!/usr/bin/env python
# coding: utf-8

# ##    Bot by: @minhadona
#     First Release: 1 jan 2021 
#     big text letters font generator: https://fsymbols.com/generators/tarty/

# In[1]:


def main():
    checking_folders = checks_if_necessary_folders_exist_otherwise_create_them()
    checking_files = checks_if_necessary_files_exist_otherwise_create_them()
    
    # ----------------------------------------------------------------------------------
    # -------- giving chance to a first-time user to change the bot rules --------------
    # ----------------------------------------------------------------------------------
    
    if type(checking_files) is str or type(checking_folders) is list:
        logging(f'main(): checking return: {checking_files}')
        want_to_insert_rules = pymsgbox.confirm('HEY ! it looks like this is your first time here! Would you like to insert retweeting rules here?\nｙｏｕ　ｃａｎ　ａｌｗａｙｓ　ｕｐｄａｔｅ　ｔｈｅｍ　ｏｎ　bot_files/controls/attributes.json \nPLEASE, NOTICE THAT if you click NO (dont insert the rules now), bot will start by using the initial template! Check the json file NOW to see the standard assignments we will begin with', 'INSERT RULES NOW?', ["Yes", "No, keep standard attributes"])
        if want_to_insert_rules == 'Yes': 
            receive_information_overwrite_json(json="attributes")
            
    elif type(checking_folders) is str:
        logging(f'main(): checking return FOLDERS: {checking_folders}')
        raise TypeError('Error: necessary FOLDER structure cannot be created or validated')
    
    elif type(checking_files) is int:
        logging(f'main(): checking return FILES: {checking_files}')
        raise TypeError('Error: necessary FILES structure cannot be created or validated')
        
    elif type(checking_files) is dict:
        logging('main(): ok, all files were validated, we may start the bot!!!!')

    logging(render('begin of lap', font="slick", background='transparent'))
        
    credentials_json = useful_variables.credentials_json
    attributes_json = useful_variables.attributes_json
    control_json = useful_variables.control_json
    
    # ----------------------------------------------------------------------------------
    # ---------------- populating dictionary with API credentials from json ------------
    # ----------------------------------------------------------------------------------

    with open(credentials_json) as credentials_file:
        credentials = json.load(credentials_file)
        #logging('credential value: '+ str(credentials))
                             
    pymsgbox.alert("Starting bot!\n\nYou can see what we're doing by reading today's logs on bot_files//logs folder!", 'Starting bot',timeout=8000)
    

    try: 
    # ----------------------------------------------------------------------------------
    # ------------------- authenticating by using API credentials ----------------------
    # ----------------------------------------------------------------------------------
        api = authenticating(credentials) # even if authentication fails, twitter unfortunately still returns an api object
                                          # an exception is only raised on tweepy.Cursor, and to query our tweets 
                                          # we have an unavoidable rather long way to go through
                                          # we need to seek the attributes/rules we want BEFORE trying to request
                                          # that's why we have this huge code-block inside this 'try' statement :/
        
        with open(attributes_json) as json_file:
            dict_attributes_info = json.load(json_file)
            
        words = dict_attributes_info["words_to_search"]
        words_str = str(words).replace('[','').replace(']','').replace('\'',"") 
        logging(f"main(): these are the words we're gonna look for: {words_str}")
        pymsgbox.alert(f"these are the words we're gonna look for: {words_str}","YOUR WISH IS MY COMMAND",timeout= 6500)
        
    # -----------------------------------------------------------------------------------------------
    # ---- for every word from attributes.json, a while will retrieve N tweets (default is 1800) ----
    # -----------------------------------------------------------------------------------------------
    
        try:
            tweet_qtd_for_lap = int(dict_attributes_info["amount_of_tweets_to_retrieve_for_every_word"]) 
                # cast to int just in case someone put some " on json 
        except ValueError:
                # if a letter was inserted, we can't go on 
            logging(f'main(): amount of tweets is not convertible to integer, someone inserted a string value on our key...')
            liveshow('something went wrong reading HOW MANY tweets you want to retrieve per word in attributes.json, please be sure you inserted a NUMBER and not a letter on amount_of_tweets_to_retrieve_for_every_word key')
            raise Exception('if we dont know how many tweets to query, we cant start our bot, sorry')
            
        logging(f'main(): amount of tweets that will be retrieved for every word: {tweet_qtd_for_lap}')
        
        for searched_word in words: 
    
            for tweet in tweepy.Cursor(api.search, tweet_mode='extended', q = searched_word).items(tweet_qtd_for_lap):
    
                dict_tweets_info = {
                "created_at": [],
                "tweet_ID": [],
                "user": [],
                "tweet_content": [],
                "place": [],
                "language": [],
                "source": [] 
            }
            # --------------------------------------------------------------------------------------
            # ---------------- check if we transpassed our daily limit of retweeting ---------------
            # --------------------------------------------------------------------------------------
            
            logging('main(): checking if we reached our daily limit of successful retweets')
            with open(control_json) as json_file:
                tweets_status = json.load(json_file)
                
                today_date = datetime.now().strftime("%d/%m/%Y")
    
                if tweets_status["amount_of_tweets"] == 999 and tweets_status['current_date'] == today_date: 
                    pymsgbox.alert("WE CANT RETWEET ANYMORE, SAFE DAILY LIMIT IS 1000 RETWEETS",'s o r r y',timeout=8000)
                    logging('main(): we ve reached 1000 successefully retweets today, we re quiting')
                    raise Exception('DAILY LIMIT REACHED, CANT RETWEET MORE THAN 1000 TWEETS')
                else:
                    logging('main(): ok we re below the limits for successful retweets') 
                    logging(f'main(): we have successfully retweeted {tweets_status["amount_of_tweets"]} tweets until now')
                        
            # --------------------------------------------------------------------------------------
            # ------- check if tweet is within the rules (language restrictions, content etc) ------
            # --------------------------------------------------------------------------------------              
            
                valid_tweet = validate_and_retweet_tweet(api,
                                                         tweet,
                                                         dict_tweets_info,
                                                         dict_attributes_info,
                                                         searched_word)

            # --------------------------------------------------------------------------------------
            # ------- if tweet is valid, we export tweet's data to csv file of today ---------------
            # -------------------------------------------------------------------------------------- 
            
                if type(valid_tweet) is dict:
                    logging('main(): VALID TWEET !!!!! Ok, we may export our data now')
                    export_infos_to_csv(valid_tweet)
                    write_json_and_updates_value(control_json,
                                                 increment_success_amount = True)
                    
            # --------------------------------------------------------------------------------------
            # - if tweet is invalid, we log the reason and increment tweet counter (control json) --
            # -------------------------------------------------------------------------------------- 
            
                elif type(valid_tweet) is int:
                    logging(f'main(): Tweet is not valid, analyzing return:: {valid_tweet}')
                    cases={
                        -1 : "didn't found the searched_word on tweet.text it self",
                        -2 : "forbidden/invalid language (japanese, korean, arabic etc problems to recognize the searched word)",
                        -3 : "you have already retweeted this Tweet",
                        -4 : "RateLimitError",
                        -5 : "tweet was made by the bot's account, we can't retweet stuff made by us",
                        -6 : "tweet is not in desired language",
                        -7 : "tweet made by a forbidden-to-retweet user"
                    }
                    
                    logging(f'main(): {cases.get(valid_tweet,"Invalid return")}')
                    write_json_and_updates_value(control_json,
                                                 increment_success_amount = False)
                    continue

                else:
                    logging('main(): Unexpected return for validate_and_retweet_tweet different than dict or int!! content: '+str(valid_tweet) +'type of return: '+str(type(valid_tweet)))
                    write_json_and_updates_value(control_json,
                                                 increment_success_amount = False)

                logging("main(): Waiting 2 min to retrieve another tweet cuz we like safety")
                time.sleep(60*2) # sleep 2 min, so we dont reach the limit 100 tweets per hour
         
    except Exception as error:
                # this is the only way i found to handle this weird exception
        if 'status code = 401' in str(error) or 'status code = 400' in str(error):
            logging('main(): INVALID CREDENTIALS, STOPPING BOT')
            pymsgbox.alert('INVALID CREDENTIALS on JSON!!!', 'Stopping bot',timeout=15000)
            want_to_insert_credentials = pymsgbox.confirm('Would you like to insert your credentials here? \n or... update credentials on \\bot_files\\controls\\credentials.json', 'INSERT CREDENTIALS?', ["Yes", "No, I'll update the json file"])
            if want_to_insert_credentials == 'Yes':
                receive_information_overwrite_json(json="credentials")
                main()
        else:
            logging(f'main(): Unkown error: {error}')
    
    logging(render('end of lap', font="slick", background='transparent'))
    
    pymsgbox.alert('$$$$$$$$$$$$$$ \n END OF LAP\n $$$$$$$$$$$$$', 'End of times',timeout=40000)


# In[2]:


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
   
    auth = tweepy.OAuthHandler(credential["api_key"],
                               credential["api_secret"])
    
    auth.set_access_token(credential["access_token"],
                          credential["access_token_secret"])

    api = tweepy.API(auth,
                     wait_on_rate_limit=True,
                     wait_on_rate_limit_notify=True)
    
    logging(render(f'welcome,', font="slick", background='transparent'))
    logging(render(f'{str(api.me().screen_name)}!', font="block", background='transparent'))
    
    logging('\nfunction<<<<<authenticating\n\n')
    return api


# In[3]:


def validate_and_retweet_tweet(api, tweet, dict_tweets_info, dict_attributes_info, searched_word):
    logging('\n\nfunction>>>>>validate_and_retweet_tweet')
    
    """   
    █ █▄░█
    █ █░▀█    
    """
        # api                   • <class 'tweepy.api.API'>    ○ authenticated api
        # tweet                 • <tweet object>              ○ one single tweet object and its attributes 
        # dict_tweets_info      • <dictionary>                ○ empty, to be filled with informations from this tweet object
        # dict_attributes_info  • <dictionary>                ○ attributes setted up on json to rule validations for this bot
        # searched_word         • <string>                    ○ seeking term (will be used here to validate the inner content of the tweet) 
    
    """
    █▀█ █░█ ▀█▀
    █▄█ █▄█ ░█░
    """
        # -1           ○ didn't found the searched_word on tweet.text it self 
        # -2           ○ forbidden language (japanese, korean, arabic etc the ones we got problems to recognize the searched word)
        # -3           ○ you have already retweeted this Tweet
        # -4           ○ RateLimitError
        # -5           ○ tweet was made by the bot's account, we can't retweet stuff made by us 
        # -6           ○ tweet is not in desired language
        # -7           ○ tweet made by a forbidden-to-retweet user
        # dict         ○ in a valid situation, returns a populated dictionary containing this tweet's data after retweeting it

    try: 

        logging('appending infos retrieved to dictionary')
        dict_tweets_info['created_at'].append(str(tweet.created_at))
        dict_tweets_info['tweet_ID'].append(str(tweet.id))
        dict_tweets_info['user'].append(str(tweet.user.screen_name))
        dict_tweets_info['tweet_content'].append((tweet.full_text))
        dict_tweets_info['place'].append(str(tweet.place))
        dict_tweets_info['language'].append(str(tweet.lang))
        dict_tweets_info['source'].append(str(tweet.source_url).replace("http://twitter.com/download/",""))
    
        logging('----------------------------------------')
        logging(f'raw dict_tweets_info after appending: \n {dict_tweets_info}')
        logging('----------------------------------------')
        
    # ---------------------------------------------------------------------------------------------------------
    # --------------------------------- FILTERING BEFORE RETWEET ----------------------------------------------
    # ---------------------------------------------------------------------------------------------------------
    
        logging('validate_and_retweet_tweet(): filtering BEFORE retweet')
        
        # -----------------------------------------------------------------------------------------------------
        string_lang_content = "".join(dict_tweets_info['language'] )  # 𝐭𝐮𝐫𝐧𝐬 𝐥𝐢𝐬𝐭 𝐢𝐧𝐭𝐨 𝐬𝐭𝐫𝐢𝐧𝐠 𝐭𝐨 𝐜𝐨𝐦𝐩𝐚𝐫𝐞
        # -----------------------------------------------------------------------------------------------------
        
        # -----------------------------------------------------------------------------------------------------
        # ---------------------------- checking if it's in one of the ENFORCED languages ----------------------
        # -----------------------------------------------------------------------------------------------------        
        logging(':::: filtering :::: enforced languages')
        if dict_attributes_info["restrict_tweets_to_these_languages"]:
            # only comes here if list is not empty! we have to enforce the languages on the list
            logging(f'these are the current enforced languages: {dict_attributes_info["restrict_tweets_to_these_languages"]}')
            if not string_lang_content in dict_attributes_info["restrict_tweets_to_these_languages"]:
                logging('ENFORCED LANG not OK: this tweet is not in enforced languages list, we wont retweet any other language!')
                returning = -6
            else: 
                logging('ENFORCED LANG OK: this tweet is allowed by the enforced languages list: '+string_lang_content)        
        else:
            logging('ENFORCED LANG OK: RESTRICTION LIST IS EMPTY, WE DONT NEED TO ENFORCE ANY LANGUAGE')
        
        # -----------------------------------------------------------------------------------------------------
        # ---------------------------- checking if it's in one of the FORBIDDEN languages ---------------------
        # -----------------------------------------------------------------------------------------------------
        logging(':::: filtering :::: forbidden languages')
        if string_lang_content in dict_attributes_info["forbidden_languages_to_retweet"]:
            logging('FORBIDDEN LANG not OK: dumb robot, tweet is not in an understandable language so its content will be wrongly evaluated, we stop here')
            returning = -2
        else: 
            logging('FORBIDDEN LANG OK: tweet is not in any forbidden language! language is actually: '+string_lang_content)
            
        # -----------------------------------------------------------------------------------------------------
        # ---------------------------- checking if the searched word really is on tweet content ---------------
        # -----------------------------------------------------------------------------------------------------
        logging(':::: filtering :::: searched word on tweet text')
        string_tweet_content = "".join(dict_tweets_info['tweet_content'] ) # turns list into string to compare
        if not searched_word in string_tweet_content.lower():
            logging('SEARCHED WORD not OK: we havent found '+ searched_word + ' on tweet content')
            # NO WAY it's gonna retweet something that has NOT the word on the text
            returning = -1
        else:
            logging('SEARCHED WORD OK: we found the searched word on tweet content!')
        
        # -----------------------------------------------------------------------------------------------------
        user_of_this_tweet = str(tweet.user.screen_name)   # 𝐭𝐮𝐫𝐧𝐬 𝐬𝐜𝐫𝐞𝐞𝐧_𝐧𝐚𝐦𝐞 𝐚𝐭𝐭𝐫𝐢𝐛𝐮𝐭𝐞 𝐢𝐧𝐭𝐨 𝐬𝐭𝐫𝐢𝐧𝐠 𝐭𝐨 𝐜𝐨𝐦𝐩𝐚𝐫𝐞
        # -----------------------------------------------------------------------------------------------------
        
        # -----------------------------------------------------------------------------------------------------
        # ------------------------- checking if THIS tweet's user is among the forbidden users ---------------
        # -----------------------------------------------------------------------------------------------------
        logging(':::: filtering :::: forbidden users')
        if dict_attributes_info["users_to_not_retweet"]:
            # only comes here if list is not empty! we have to block retweets from these users on list
            logging('these are the current forbidden users to retweet: '+ str(dict_attributes_info["users_to_not_retweet"]))
            if str(tweet.user.screen_name) in dict_attributes_info["users_to_not_retweet"]:
                logging('FORBIDDEN USERS not OK: this tweet was made by a forbidden-to-retweet user')
                returning = -7
            else: 
                logging('FORBIDDEN USERS OK: we are allowed to retweet tweets from @'+ user_of_this_tweet)        
        else:
            logging('FORBIDDEN USERS OK: LIST IS EMPTY, WE DONT NEED TO IGNORE ANY USER')
        
        # -----------------------------------------------------------------------------------------------------
        # ------------------------- checking if THIS tweet's user is also the authenticated user --------------
        # -------------------------------- (so we dont retweet our 𝐨𝐰𝐧 tweets) -------------------------------
        # -----------------------------------------------------------------------------------------------------
        logging(":::: filtering :::: tweet's user vs authenticated one")
        my_user_object = api.me()
        if str(my_user_object.screen_name) == user_of_this_tweet:
            logging('you are @'+ str(my_user_object.screen_name))
            logging('OWN AUTHORSHIP not OK: this tweet was made by yourself using your bot profile or is an old RETWEET!! both cases we wont retweet it again')
            returning = -5
        else:
            logging('OWN AUTHORSHIP OK: this user is not you! you: '+ str(my_user_object.screen_name) + ' VS this user: '+ user_of_this_tweet +', that s great')
        
    # ---------------------------------------------------------------------------------------------------------
    # ---------------------------------- OK, RETWEET ACTION ! -------------------------------------------------
    # ---------------------------------------------------------------------------------------------------------
        logging('retweeting ←←←←←←←←←←←←←')
        api.retweet(tweet.id)
        logging('→→→→→→→→→→→→→ retweeted') # if an exception is raised during retweet method, we wont arrive here
        return dict_tweets_info
    
    except tweepy.TweepError as e: 
        if e.api_code == 327:
            logging('Exception Code 327: You have already retweeted this Tweet')
            returning = -3
        
    except tweepy.RateLimitError as e:
        logging('RateLimitError')
        logging('Unknown error: '+str(e))
        logging('according to internet, sleeping for 15 min should solve...')
        time.sleep(60 * 15)  # we saw rate limit is ignored after 15 min ??? ///not confirmed hypothesis///
        returning = -4
        
    logging('\nfunction<<<<<validate_and_retweet_tweet\n\n')    
    return returning


# In[4]:


def write_json_and_updates_value(path, increment_success_amount = False, initialize = False):
    logging('\n\nfunction>>>>>write_json_and_updates_value')
    
    """   
    █ █▄░█
    █ █░▀█    
    """
        # path                           • <string>          ○ control json path
        # increment_success_amount       • <bool>            ○ boolean flag to update or not a specific key
        # inicializar                    • <bool>            ○ boolean flag to reset (set to 0) or not all the keys
    
    now = datetime.now()
    current_date = now.strftime("%d/%m/%Y")

    # ---------------------------------------------------------------------------------------------------------
    # -------------------------------- trying to read from file -----------------------------------------------
    # ---------------------------------------------------------------------------------------------------------
    logging(f'write_json_and_updates_value(): loading json file into dictionary, so we can manipulate values')
    
    try:
        with open(path) as json_file:
            tweets_status = json.load(json_file)
            
    except IOError as io_e:
        if initialize:
            logging(f'write_json_and_updates_value(): file does not exist yet but we will create because we got the initialize parameter as true')
        else:
            logging(f'write_json_and_updates_value(): IO ERROR BUT WE WERE NOT SUPPOSED TO INITIALIZE THE FILE NOW: {io_e}')
                
    except Exception as e:
        logging(f'write_json_and_updates_value(): UNKOWN PROBLEMS WHEN TRYING TO READ JSON FILE: {e}')

    # ---------------------------------------------------------------------------------------------------------
    # ---------------------------------- writing on file ------------------------------------------------------
    # ------- if our current date is the same of the file, we increase amount of tweets -----------------------
    # ----- if different, amount of everything is ZERO because it's the first time running of today !!!! ------
    # ---------------------------------------------------------------------------------------------------------

    if initialize or tweets_status['current_date'] != current_date: 
        logging('write_json_and_updates_value(): different dates, OR initializing parameter says true, so we need to update the current_date and also reset all the values to 0 ')
        with open(path, 'w') as f:
            try:
                content = {"current_date": current_date,
                           "amount_of_tweets": 0,
                           "total_amount_including_failure":0}
                json.dump(content, f)

            except json.JSONDecodeError:
                logging('write_json_and_updates_value(): decode error but will try raw writing')
                f.write(contenting)
    else: 
        logging('write_json_and_updates_value(): same date of file, bot was online today!! so, just update the value of tweets')
        if increment_success_amount:
                logging('write_json_and_updates_value(): increases both keys - failure and success counter')
                # vai incrementtar o total com falhas tb + o total dos sucessos
                tweets_status["amount_of_tweets"] = tweets_status["amount_of_tweets"]+1 
                tweets_status['total_amount_including_failure'] = tweets_status['total_amount_including_failure']+1
                with open(path, 'w') as f:
                    try:
                        json.dump(tweets_status, f)
                    except json.JSONDecodeError:
                        logging('decode error but will try raw writing')
                        f.write(contenting)
                    
        elif not increment_success_amount: 
                logging('increasing amount of the ones who failure')
                     # increasing amount of the ones who failure 
                tweets_status['total_amount_including_failure'] = tweets_status['total_amount_including_failure']+1

                with open(path, 'w') as f:
                    try:
                        json.dump(tweets_status, f)

                    except json.JSONDecodeError:
                        logging('decode error but will try raw writing')
                        f.write(contenting)
                        
    logging('\nfunction<<<<<write_json_and_updates_value\n\n')
    return


# In[12]:


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
    logging(f"today's CSV path: {CSV_path}")

    logging(f'valid_tweet : {valid_tweet}')
    
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
        
                            # |-------------------------------------------------------|
                            # | ---------------- DATA NORMALIZATION ------------------|
                            # |-------------------------------------------------------|

        # -----------------------------------------------------------------------------------------------------------
        # -------- forcing Tweet ID to be written as string on sheet, so it doesnt truncate as scientific notation --
        # -----------------------------------------------------------------------------------------------------------
        
    dict_values_in_list_version[1] = '\''+dict_values_in_list_version[1]

        # -----------------------------------------------------------------------------------------------------------
        # ---- for some reason, a lot of tweets comes with a \n character, which unduly makes CSV skip lines --------
        # -----------------------------------------------------------------------------------------------------------
     
    for index, field in enumerate(dict_values_in_list_version):
        dict_values_in_list_version[index] = field.replace('\n',"")     
        # -----------------------------------------------------------------------------------------------------------
        # --------- when tweet is not made via app but via phone browser, the OS is not identifiable ----------------
        # -----------------------------------------------------------------------------------------------------------
        if 'mobile.twitter' in field:
            dict_values_in_list_version[index] = field.replace("https://mobile.twitter.com","mobile browser")
        
    logging(f'dict_values_in_list_version: {dict_values_in_list_version}')

        # -----------------------------------------------------------------------------------------------------------
        # --------- if today's CSV already exists, we will append only this specific tweet's DETAILS to file --------
        # ----------------- elseways we append the header (creating a new file) -------------------------------------
        # ------------------- and THEN append current tweet's details normally --------------------------------------
        # -----------------------------------------------------------------------------------------------------------
    
    if not os.path.exists(CSV_path):
        logging('today s csv does not exist yet, creating it and appending header')
        header_csv = ['created_at','tweet_ID','user','tweet_content','place','language','source'] 
        with open(CSV_path, "a", encoding="utf-8", newline='') as file:
            wr = csv.writer(file)
            wr.writerow(header_csv)
            
    with open(CSV_path, "a", encoding="utf-8", newline='') as file:
        logging('writing tweet details on CSV file')
        wr = csv.writer(file)
        wr.writerow(dict_values_in_list_version)
        
    logging('\nfunction>>>>>exporting_infos_to_csv\n\n')
    return


# In[6]:


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
    return


# In[7]:


def receive_information_overwrite_json(json):      
    logging('\n\nfunction>>>>>receive_information_overwrite_json')
    
    if json == "credentials":
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
            
            
    elif json == "attributes":       
            new_words_to_search = pymsgbox.prompt('Insert the words you want to retweet (separeted by COMMA only) \nExample: bla, blabla, blablabla', default='word1,word2,word3')
            logging('inputted new_words_to_search: '+ new_words_to_search)
            new_users_to_not_retweet = pymsgbox.prompt('Insert users you want to ban retweets from (separeted by COMMA only)\nExample: bla, blabla, blablabla', default='user1,user2,user3')
            logging('inputted new_users_to_not_retweet: '+ new_users_to_not_retweet)
            new_forbidden_languages_to_retweet = pymsgbox.prompt('Do you want to forbid some specific language ? Insert them by using its standard abbreviation\nExample: pt, en  in case you dont want to see tweets in portuguese and english\n\nIf you want to retweet all languages, please dont write anything', default = 'en,pt')
            logging('inputted new_forbidden_languages_to_retweet: '+ new_forbidden_languages_to_retweet)
            new_restrict_tweets_to_these_languages = pymsgbox.prompt('Do you want to restrict ALL tweets to one single language? (Or some specific ones) Insert them by using its standard abbreviation\nExample: ja,ko  in case you ONLY want to see japanese and korean tweets!\n\nIf you dont wanna restrict tweets to some specific language, please dont write anything', default = "ja")
            logging('inputted new_restrict_tweets_to_these_languages: '+ new_restrict_tweets_to_these_languages)
            
              
            content = {"words_to_search" : [],
                           "users_to_not_retweet" : [],
                           "forbidden_languages_to_retweet" : [],
                           "restrict_tweets_to_these_languages" : [] }
            
            if new_words_to_search in [""," "]:
                pass
            else:
                new_words_to_search = new_words_to_search.split(",")
                list_new_words_to_search = []
                for word in new_words_to_search:
                    word = word.strip()  # cut out spaces at the beginning and at the end of the word
                    list_new_words_to_search.append(word)
                logging('new_words_to_search to be written on json: '+str(list_new_words_to_search))
                content["words_to_search"] = list_new_words_to_search

            if new_users_to_not_retweet in [""," "]:
                pass
            else:
                new_users_to_not_retweet = new_users_to_not_retweet.split(",")
                list_users_to_not_retweet = []
                for word in new_users_to_not_retweet:
                    word = word.strip()  # cut out spaces at the beginning and at the end of the word
                    list_users_to_not_retweet.append(word)
                logging('new_users_to_not_retweet to be written on json: '+str(list_users_to_not_retweet))
                content["users_to_not_retweet"] = list_users_to_not_retweet
                
    
            if new_forbidden_languages_to_retweet in [""," "]:
                pass
            else: 
                new_forbidden_languages_to_retweet = new_forbidden_languages_to_retweet.split(',')
                list_new_forbidden_languages_to_retweet = []
                for word in new_forbidden_languages_to_retweet:
                    word = word.strip()  # cut out spaces at the beginning and at the end of the word
                    list_new_forbidden_languages_to_retweet.append(word)
                logging('new_forbidden_languages_to_retweet to be written on json: '+str(list_new_forbidden_languages_to_retweet))
                content["forbidden_languages_to_retweet"] = list_new_forbidden_languages_to_retweet
            
            if new_restrict_tweets_to_these_languages in [""," "]:
                pass
            else:
                new_restrict_tweets_to_these_languages = new_restrict_tweets_to_these_languages.split(',')
                list_new_restrict_tweets_to_these_languages = []
                for word in new_restrict_tweets_to_these_languages:
                    word = word.strip()  # cut out spaces at the beginning and at the end of the word
                    list_new_restrict_tweets_to_these_languages.append(word)
                logging('new_restrict_tweets_to_these_languages to be written on json: '+str(list_new_restrict_tweets_to_these_languages))
                content["restrict_tweets_to_these_languages"] = list_new_restrict_tweets_to_these_languages
                
            with open(useful_variables.attributes_json, 'w') as f:
                try:
                    for key, value in content.items():
                        json.dumps(content, f)

                except AttributeError:
                    logging('decode error but will try raw writing')
                    f.write(str(content).replace("'",'"'))
                    
    logging('\nfunction<<<<<receive_information_overwrite_json\n\n')
    return


# In[8]:


def liveshow(text="",title="Are we on air?",timeout=5000):

    # ----------------------------------------------------------------
    # live show Definition (n.): 
    #        "𝓁𝒾𝓋𝑒 𝒷𝓇𝑜𝒶𝒹𝒸𝒶𝓈𝓉, 𝒷𝓇𝑜𝒶𝒹𝒸𝒶𝓈𝓉 𝓉𝒽𝒶𝓉 𝒾𝓈 𝒶𝒾𝓇𝑒𝒹 𝒾𝓃 𝓇𝑒𝒶𝓁-𝓉𝒾𝓂𝑒 " 
    #                          https://www.dictionarist.com/live+show
    # ----------------------------------------------------------------

    logging(text)
    pymsgbox.alert(text = text,
                  title = title,
                  timeout = timeout)


# In[9]:


def checks_if_necessary_folders_exist_otherwise_create_them():
    # ----------------------------------------------------------------------------------------------
    # ---------------------  CREATES INTO SCRIPT DIRECTORY ALL NECESSARY FOLDERS  ------------------
    # ----------------------------------------------------------------------------------------------
    returning = 1 
    try:
        if not os.path.exists(useful_variables.logs_folder):
            pymsgbox.alert(text="Creating logs' folder", title='Setting bot up', button='OK',timeout=4500)
            os.makedirs(useful_variables.logs_folder)
            logging("Creating logs' folder")
            returning = ["probably first time"]
        else:
            liveshow(f'{useful_variables.logs_folder} already exists')

        if not os.path.exists(useful_variables.controls_folder):
            pymsgbox.alert(text='Creating controls folder', title='Setting bot up', button='OK',timeout=4500)
            os.makedirs(useful_variables.controls_folder)
            logging("Creating controls folder")
            returning = ["probably first time"]
        else:
            liveshow(f'{useful_variables.controls_folder} already exists')

        if not os.path.exists(useful_variables.exported_data_folder):
            pymsgbox.alert(text='Creating exported_data folder', title='Setting bot up', button='OK',timeout=4500)
            os.makedirs(useful_variables.exported_data_folder)
            logging("Creating exported_data folder")
            returning = ["probably first time"]
        else:
            liveshow(f'{useful_variables.exported_data_folder} already exists')

    except Exception as error:
        logging(f'Unknown error: {error}')
        returning = str(error)
    
    return returning


# In[10]:


def checks_if_necessary_files_exist_otherwise_create_them():
    logging('\n\nfunction>>>>>checks_if_necessary_files_exist_otherwise_create_them')
   
    """
    █▀█ █░█ ▀█▀
    █▄█ █▄█ ░█░
    """ 
    # -1     ○ invalid attributes: FOUND ATTRIBUTES FILE BUT some value on attributes dict is not list type ('a' : ['LIST','LIST'])
    # -2     ○ invalid attributes: FOUND ATTRIBUTES FILE BUT to exclude a language from retweeting and ask to retweet the same language is contraditory
    # string ○ json files DIDN'T exist, but we created the templates
    # dict   ○ json files exist and the validation for all json files successed
    
    returning = "we assume this is the first time running the bot "
    # ------------------------------------------------------------------------------------------
    # ---------- checking if control json exists, otherwise we create it -------------------
    # ------------------------------------------------------------------------------------------
    control_json = useful_variables.control_json
    if not os.path.exists(control_json):
        logging("control json not found, gotta create it")
        write_json_and_updates_value(control_json,
                                     increment_success_amount = False,
                                     initialize = True)
    else:
        logging(f'{control_json} already exists')

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
        logging(f'{credentials_json} already exists')
        
    # ------------------------------------------------------------------------------------------    
    # ---------- checking if attributes json exists, otherwise we create it --------------------
    # ------------------------------------------------------------------------------------------
    
    attributes_json = useful_variables.attributes_json
    
    content_template = {"words_to_search" : ['zolpidem','ambien'],
                        "users_to_not_retweet" : ['user1','user2'],
                        "forbidden_languages_to_retweet" : ['ja','ko','und','fa','ar'],
                        "restrict_tweets_to_these_languages" : [],
                        "amount_of_tweets_to_retrieve_for_every_word": 1800 }
    
    if not os.path.exists(attributes_json):
        logging("attributes json not found, gotta create it using a valid template")
        
        with open(attributes_json, 'w') as f:
            try:
                
                json.dump(content_template, f)

            except json.JSONDecodeError:
                logging('decode error but will try raw writing')
                f.write(content_template)
                
            finally:
                returning = "attributes json had to be created, probably this is the first time of this user"
                
    else:
        # -------------------------------------------------------------------------------------
        # ---------------- if file exists already, we will validate any inconsistency ---------
        # -------------------------------------------------------------------------------------
        
        logging(f'{attributes_json} already exists')
        logging('let s validate its content')
        with open(attributes_json) as json_file:
            returning = content_template
            dict_attributes_info = json.load(json_file)
            
            # ----------- all values have to be LIST type -----------------------
            
            for key, value in dict_attributes_info.items():
                if key == "amount_of_tweets_to_retrieve_for_every_word":
                    continue # this is the only key that has not to be list type 
                
                if not type(value) is list:
                    liveshow(f'YOU VE CHANGED THE TYPE OF SOME VALUE ON JSON! the value of {key} is not a list and it has to be!\nPLEASE, DELETE THE ATTRIBUTES.JSON FILE, restart the bot AND FOLLOW THE INITIAL TEMPLATE we will create! \n\n\nfile location: \\bot_files\\controls\\attributes.json\n\n', 'BOT CANNOT START WITH INVALID ATTRIBUTES')
                    logging(f'the invalid key is {key}, because {value} is not list type')
                    returning = -1
            
            # ----------- cant have same value on _restrict and _forbiden -------
            
            for language in dict_attributes_info['restrict_tweets_to_these_languages']:
                if language in dict_attributes_info['forbidden_languages_to_retweet']:
                    liveshow(f'you cant ask us to only retweet things in the same language you WANT TO PROHIBIT retweeting! you inserted {language} in both keys: restricting and forbidding!\nPLEASE UPDATE JSON FILE ON \\bot_files\\controls\\attributes.json and try again','what?')
                    returning = -2
                
            # ----------- cant have empty value on words_to_search -------------
            
            if not dict_attributes_info["words_to_search"]:
                liveshow("THIS IS A RETWEET BOT, if we have no words to look for, what do you want us to do? \nPlease update attributes.json inside of CONTROLS folder and set a list of words","Oh no",8000)
                returning = -3
                
    logging('\nfunction<<<<<checks_if_necessary_files_exist_otherwise_create_them\n\n')            
    return returning


# In[ ]:


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
from cfonts import render, say

main()


# In[ ]:




