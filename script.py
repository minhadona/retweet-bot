#!/usr/bin/env python
# coding: utf-8

# In[95]:


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
        # api                • <class 'tweepy.api.API'>    ○ authenticated api
    
    auth = tweepy.OAuthHandler(credential["api_key"], credential["api_secret"])
    auth.set_access_token(credential["access_token"], credential["access_token_secret"])
    
    api = tweepy.API(auth,wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    
    print(type(api))
    return api


# In[96]:


def print_and_retweet_tweet(api,tweet,dict_tweets_info,searched_word):
    logging('\n\nfunction>>>>>print_and_retweet_tweet')
    
    """   
    █ █▄░█
    █ █░▀█    
    """
        # api                • <class 'tweepy.api.API'>    ○ authenticated api
        # tweet              • <tweet object>              ○ one single tweet object and its attributes 
        # dict_tweets_info   • <dictionary>                ○ empty, to be filled with informations from this tweet object
        # searched_word      • <string>                    ○ seeking term (will be used here to validate the inner of tweet content) 
    
    """
    █▀█ █░█ ▀█▀
    █▄█ █▄█ ░█░
    """
        # -1           ○ didn't found the searched_word on tweet.text it self (maybe )
        # -2           ○ japanese or korean
        # -3           ○ you have already retweeted this Tweet
        # -4           ○ RateLimitError
        # -5           ○ you are the owner of this tweet
        # -6           ○ tweet was made by the bot's account, we can't retweet stuff made by us 
        # dict         ○ in a valid situation, returns a populated dictionary containing this tweet's data 

    try: 
        logging('appending infos to dictionary')
        dict_tweets_info['created_at'].append(str(tweet.created_at))
        dict_tweets_info['tweet_ID'].append(str(tweet.id))
        dict_tweets_info['user'].append(str(tweet.user.screen_name))
        dict_tweets_info['tweet_content'].append((tweet.text))
        dict_tweets_info['place'].append(str(tweet.place))
        dict_tweets_info['language'].append(str(tweet.lang))
        dict_tweets_info['source'].append(str(tweet.source_url).replace("http://twitter.com/download/",""))
    
        logging('----------------------------------------')
        logging('collected informations')
        logging('----------------------------------------')
 
        logging('dict_tweets_info: \n '+str(dict_tweets_info))
        logging('----------------------------------------\n\n\n\n')
        
        # ----- starting filters ------
        
        logging('print_and_retweet_tweet(): better filtering BEFORE retweet')
        string_tweet_content = "".join(dict_tweets_info['tweet_content'] )
        if not searched_word in string_tweet_content.lower():
            logging('NAO ACHOU NA STRING A PALAVRA BUSCADA: '+ searched_word)
            # NO WAY it's gonna retweet something that has NOT 'zolpidem on it'
            return -1

        string_lang_content = "".join(dict_tweets_info['language'] )
        if string_lang_content in ['ja','ko']:
            logging('japones ou coreano')
            # NO WAY it's gonna retweet something that is in japanese or korean
            return -2
        else:
            logging('teoricamente nao esta em japones nem coreano, está em: '+string_lang_content )
        
        my_user_object = api.me()
        if str(my_user_object.screen_name) == str(tweet.user.screen_name):
            logging('this tweet was made by yourself using your bot profile !!we wont retweet it')
            return -6
        else:
            logging('this user is not you! you: '+ str(my_user_object.screen_name) + ' the tweeter: '+ str(tweet.user.screen_name) +', that s great')
        
        logging('retweeting ←←←←←←←←←←←←←')
        api.retweet(tweet.id)
        logging('→→→→→→→→→→→→→ retweeted')
        return dict_tweets_info
    
    except tweepy.TweepError as e: 
        if e.api_code == 327:
            logging('You have already retweeted this Tweet')
            return -3
        
    except tweepy.RateLimitError as e:
        logging('Excedeu limite por tempo?')
        logging('erro: '+str(e))
        logging('DORMINDO POR QUINZE MINUTOS')
        time.sleep(60 * 15)  # we supposedly saw a rate limit that is ignored after 15 min ??? so we should wait 15 min to retry 
        return -4


# In[97]:


def write_json_and_updates_value(path,incrementa_contagem_de_falha=False,inicializar = False):
    logging('\n\nfunction>>>>>write_json_and_updates_value')
    
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


# In[98]:


def export_infos_to_csv(valid_tweet):
    logging('\n\nfunction>>>>>exporting_infos_to_csv')
    
    now = datetime.now()
    current_directory = os.getcwd()  
    timestamp = now.strftime("%d/%m/%Y").replace("/","-").replace(':',"-").replace(',','--').replace(" ","")

    CSV_path = current_directory+'\\arquivos_bot\\dados_exportados\\dados_'+timestamp+'.csv'
    logging('log path: '+str(CSV_path))

    logging('dict_tweets_info : '+str(valid_tweet))

    # pegando os valores do dicionario e jogando em lista pq senao ele da apend no dicionario inteiro, linha de key e depois linha de value PRA CADA tweet
    lista_valores_atuais = []
    for key, value in valid_tweet.items():
        lista_valores_atuais.append("".join(value))

    # forcing Tweet ID to be written as string, so it doesnt truncate as scientific notation
    lista_valores_atuais[1] = '\''+lista_valores_atuais[1]

    logging('LISTA_VALORES_ATUAIS: '+str(lista_valores_atuais))

    # se arquivo do dia já existe, vai dar append apenas no conteúdo daquele tweet, caso contrário, 
    # vai criar o arquivo e vai dar append
    # no header e depois no tweet 

    if not os.path.exists(CSV_path):
        logging('today s csv does not exist yet, creating it and appending header')
        header_csv = ['created_at','tweet_ID','user','tweet_content','place','language','source'] 
        with open(CSV_path, "a") as file:
            wr = csv.writer(file)
            wr.writerow(header_csv)
            
    with open(CSV_path, "a",encoding="utf-8", newline='') as file:
        logging('writing lista_valores_atuais anyways')
        wr = csv.writer(file)
        wr.writerow(lista_valores_atuais)

    # df = pd.DataFrame(lista_valores_atuais) # turning into data frame
    # df.to_csv(path_or_buf = CSV_path, mode='a',index=False, cols = header_csv)


# In[99]:


def logging(text_to_log=""):
    
    # converte parâmetro que ele quer escrever no log em string, caso tenha sido enviado em outro formato
    text_to_log = str(text_to_log)
    
    # prepara data e timestamp pra dar append no arquivo de log (ou escrever um novo) + timestamp no conteúdo do arquivo
    now = datetime.now()
    date = now.strftime("%d/%m/%Y").replace("/","-")
    timestamp = now.strftime("%d/%m/%Y, %H:%M:%S")
    
    # busca diretório onde o robô está rodando e formata o path pro log do dia corrente
    current_directory = os.getcwd()  
    log_path = current_directory+'\\arquivos_bot\\logs\\log_'+date+'.txt'

    # se arquivo do dia já existir, só escreve nele o timestamp + conteúdo do parámetro
    # caso contrário, cria o arquivo de log daquele dia 
    with open(log_path, 'a+',encoding="utf-8") as log_file:
        log_file.write(timestamp+ ' - ' + text_to_log+'\n')
    
    # além de escrever no arquivo, printa no jupyter
    print(timestamp+ ' - ' + text_to_log)


# In[100]:


def translate_special_text_to_ascii(original_text):
    translated_text = ''

    for character in original_text:
        if ord(character) >= 128:
            translated_text = translated_text + '"Chr(' + str(ord(character)) + ')"'
        else:
            translated_text = translated_text + character

    return translated_text


# In[101]:


def main():
    
    # ----------------------------------------------------------------------------------------------------------
    # ---------------------  CRIA PASTAS QUE O ROBÔ VAI USAR NO DIRETÓRIO DO SCRIPT  ---------------------------
    # ----------------------------------------------------------------------------------------------------------
    # ------------------------- e json de controle também, caso nada disso exista ------------------------------
    # ----------------------------------------------------------------------------------------------------------
    
    current_directory = os.getcwd()
    if not os.path.exists(current_directory+'\\arquivos_bot\\logs'):
        pymsgbox.alert(text='Criando pasta de logs', title='Preparando bot', button='OK',timeout=4500)
        os.makedirs(current_directory+'\\arquivos_bot\\logs')
        logging("Preparando ambiente")
        logging("Criando pasta de logs")
    
    if not os.path.exists(current_directory+'\\arquivos_bot\\controle'):
        pymsgbox.alert(text='Criando pasta de controle', title='Preparando bot', button='OK',timeout=4500)
        os.makedirs(current_directory+'\\arquivos_bot\\controle')
        logging("Criando pasta de controle")

    if not os.path.exists(current_directory+'\\arquivos_bot\\dados_exportados'):
        pymsgbox.alert(text='Criando pasta de dados exportados', title='Preparando bot', button='OK',timeout=4500)
        os.makedirs(current_directory+'\\arquivos_bot\\dados_exportados')
        logging("Criando pasta de dados exportados")
    
    
    # checking if control json exists, otherwise we create it
    if not os.path.exists(current_directory+'\\arquivos_bot\\controle\\amount_of_tweets_from_today.json'):
        logging("arquivo json não encontrado")
        now = datetime.now()
        date = now.strftime("%d/%m/%Y")
        write_json_and_updates_value(current_directory+'\\arquivos_bot\\controle\\amount_of_tweets_from_today.json',incrementa_contagem_de_falha=False,inicializar = True)
    
    
    pymsgbox.alert('Pastas necessárias para o robô conferidas, iniciando o bot', 'Starting bot',timeout=5000)
    logging("░██████╗████████╗░█████╗░██████╗░████████╗██╗███╗░░██╗░██████╗░")
    logging("██╔════╝╚══██╔══╝██╔══██╗██╔══██╗╚══██╔══╝██║████╗░██║██╔════╝░")
    logging("╚█████╗░░░░██║░░░███████║██████╔╝░░░██║░░░██║██╔██╗██║██║░░██╗░")
    logging("░╚═══██╗░░░██║░░░██╔══██║██╔══██╗░░░██║░░░██║██║╚████║██║░░╚██╗")
    logging("██████╔╝░░░██║░░░██║░░██║██║░░██║░░░██║░░░██║██║░╚███║╚██████╔╝")
    logging("╚═════╝░░░░╚═╝░░░╚═╝░░╚═╝╚═╝░░╚═╝░░░╚═╝░░░╚═╝╚═╝░░╚══╝░╚═════╝░")
    
    credential =  {
                    "api_key" : credentials.API_KEY,
                    "api_secret" : credentials.API_SECRET,
                    "bearer_token" : credentials.BEARER_TOKEN,
                    "access_token" : credentials.ACCESS_TOKEN,
                    "access_token_secret" : credentials.ACCESS_TOKEN_SECRET
                    }
    
    api = authenticating(credential)

    words = ['zolpidem','ambien']
    
    for searched_word in words:
        
        for tweet in tweepy.Cursor(api.search, q = searched_word ).items(1100):
            
            dict_tweets_info = {
            "created_at": [],
            "tweet_ID": [],
            "user": [],
            "tweet_content": [],
            "place": [],
            "language": [],
            "source": [] 
        }

            with open(current_directory+'\\arquivos_bot\\controle\\amount_of_tweets_from_today.json') as json_file:
                tweets_status = json.load(json_file)
                if tweets_status["amount_of_tweets"] == 999 and tweets_status['current_date'] == date:
                    sys.exit('DAILY LIMIT REACHED, CANT RETWEET MORE THAN 1000 TWEETS')

            valid_tweet = print_and_retweet_tweet(api,tweet,dict_tweets_info,searched_word)

            if not valid_tweet is True: # retornou de -1 a -5
                logging('Tweet is not valid, return: '+str(valid_tweet))
                write_json_and_updates_value(current_directory+'\\arquivos_bot\\controle\\amount_of_tweets_from_today.json',incrementa_contagem_de_falha=True)
                continue

            if isinstance(valid_tweet,dict):
                logging('Ok, we received a dict as return, we may export the results now')
                export_infos_to_csv(valid_tweet)
                write_json_and_updates_value(current_directory+'\\arquivos_bot\\controle\\amount_of_tweets_from_today.json',incrementa_contagem_de_falha=False)
            else:
                logging('Unexpected return for print_and_retweet_tweet different than dict or false!! content: '+str(valid_tweet))
                write_json_and_updates_value(current_directory+'\\arquivos_bot\\controle\\amount_of_tweets_from_today.json',incrementa_contagem_de_falha=False)
            logging("Waiting 2 min for retrieve another tweet cuz we like safety")
            time.sleep(60*2) # sleep 2 min, so we dont reach the limit 100 tweets per hour
        
    
    logging('███████╗███╗░░██╗██████╗░  ░█████╗░███████╗  ██╗░░░░░░█████╗░██████╗░')
    logging('██╔════╝████╗░██║██╔══██╗  ██╔══██╗██╔════╝  ██║░░░░░██╔══██╗██╔══██╗')
    logging('█████╗░░██╔██╗██║██║░░██║  ██║░░██║█████╗░░  ██║░░░░░███████║██████╔╝')
    logging('██╔══╝░░██║╚████║██║░░██║  ██║░░██║██╔══╝░░  ██║░░░░░██╔══██║██╔═══╝░')
    logging('███████╗██║░╚███║██████╔╝  ╚█████╔╝██║░░░░░  ███████╗██║░░██║██║░░░░░')
    logging('╚══════╝╚═╝░░╚══╝╚═════╝░  ░╚════╝░╚═╝░░░░░  ╚══════╝╚═╝░░╚═╝╚═╝░░░░░')
    
    pymsgbox.alert('$$$$$$$$$$$$$$ \n FIM DA LAP\n $$$$$$$$$$$$$', 'End of times',timeout=40000)

    
    
    # bot by: @minhadona, jan.2021
    # big letters font generator: https://fsymbols.com/generators/tarty/
    


# In[102]:


import import_ipynb
import credentials
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




