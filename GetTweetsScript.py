
import tweepy
import datetime 
from twitter_authentication import bearer_token
from gmail_info import gmail_pass, gmail_user
import time
import pandas as pd
import os
import smtplib
import ssl


client = tweepy.Client(bearer_token, wait_on_rate_limit=True)


if os.path.isdir('data') == False:
    os.mkdir('data')


if os.path.isdir('logs') == False:
    os.mkdir('logs')


### BTC Train Set 2017 to 2020


data_set_name = 'btc_train'

start_str = '2017-01-14'
end_str =   '2020-01-01'

start = datetime.datetime.strptime(start_str, "%Y-%m-%d")
end =   datetime.datetime.strptime(end_str, "%Y-%m-%d")
diff = end-start

diff_list = str(diff).split(' ')
num_hours = int(diff_list[0]) * 24 + 1

date = start

date_list = []
for i in range(0, num_hours):
    date_str = date.strftime("%Y-%m-%dT%H:%M:%SZ")
    date_list.append(date_str)
    date += datetime.timedelta(hours=1)

start_date = date_list [0]
end_date = date_list[len(date_list) - 1]

try: 

    tweets_list = []

    count = 0

    for j in range(0, len(date_list) - 1):
        
        count = count + 1
        
        f= open('./logs/log_' + data_set_name + '.txt', 'a')
        f.write("\n") 
        f.write(date_list[j] + "\n")
        f.write(date_list[j+1] + "\n")
        f.close()

        for response in tweepy.Paginator(client.search_all_tweets, 
                                        query = '#btc OR #bitcoin OR #bitcointrading -is:retweet lang:en',
                                        user_fields = ['username', 'public_metrics', 'description', 'location'],
                                        tweet_fields = ['created_at', 'geo', 'public_metrics', 'text'],
                                        expansions = 'author_id',
                                        start_time = date_list [j],
                                        end_time = date_list [j+1],
                                        max_results=10,  
                                        limit=25):
            
            time.sleep(1)
            tweets_list.append(response)
            
        
        if count % 24 == 0:
            
            path = './data/'+ data_set_name + '__' + date_list[j][0:10] + '.csv'
            
            result = []
            user_dict = {}
            
            # Loop through each response object
            for response in tweets_list:
                # Take all of the users, and put them into a dictionary of dictionaries with the info we want to keep
                for user in response.includes['users']:
                    user_dict[user.id] = {'username': user.username, 
                                        'followers': user.public_metrics['followers_count'],
                                        'tweets': user.public_metrics['tweet_count'],
                                        'description': user.description,
                                        'location': user.location
                                        }
                for tweet in response.data:
                    # For each tweet, find the author's information
                    author_info = user_dict[tweet.author_id]
                    # Put all of the information we want to keep in a single dictionary for each tweet
                    result.append({'author_id': tweet.author_id, 
                                'username': author_info['username'],
                                'author_followers': author_info['followers'],
                                'author_tweets': author_info['tweets'],
                                'author_description': author_info['description'],
                                'author_location': author_info['location'],
                                'text': tweet.text,
                                'created_at': tweet.created_at,
                                'retweets': tweet.public_metrics['retweet_count'],
                                'replies': tweet.public_metrics['reply_count'],
                                'likes': tweet.public_metrics['like_count'],
                                'quote_count': tweet.public_metrics['quote_count']
                                })

            
            # Change this list of dictionaries into a dataframe
            df = pd.DataFrame(result)
            
            df.to_csv(path)
            
            f= open('./logs/log_' + data_set_name + '.txt', 'a')
            f.write("output to csv")
            f.close()
            
            tweets_list = []
            

    sent_from = gmail_user
    to = ['spencerd.king@gmail.com', 'sdk81722@uga.edu']
    subject = 'Old Tweet Gathering Is Done:' + data_set_name + ' !'
    body = 'The ' + data_set_name + ' set is downloaded and ready for use! \n\nData set date range: ' + start_date + ' to ' + end_date

    email_text = """\
    From: %s
    To: %s
    Subject: %s

    %s
    """ % (sent_from, ", ".join(to), subject, body)

    try:
        smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        smtp_server.login(gmail_user, gmail_pass)
        smtp_server.sendmail(sent_from, to, email_text)
        smtp_server.close()
        print ("Email sent successfully!")
    except Exception as ex:
        print ("Something went wrong….",ex)
        
 
except Exception as e:
    
    sent_from = gmail_user
    to = ['spencerd.king@gmail.com', 'sdk81722@uga.edu']
    subject = 'ERROR with Old Tweet Gathering: ' + data_set_name + '!'
    body = 'Error occured while downloading ' + data_set_name + ' set! \n\nError occured: ' + str(e) + '\n\nGo check it out when you get a chance!'

    email_text = """\
    From: %s
    To: %s
    Subject: %s

    %s
    """ % (sent_from, ", ".join(to), subject, body)

    try:
        smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        smtp_server.login(gmail_user, gmail_pass)
        smtp_server.sendmail(sent_from, to, email_text)
        smtp_server.close()
        print ("Email sent successfully!")
    except Exception as ex:
        print ("Something went wrong….",ex)



"""
### Notes

1. Set up email notifications if linode will let you
2. Find a way to run program in the background
    Most likely will have to just make it into a script and run in back ground with nohup ... &
    https://stackoverflow.com/questions/57664547/long-running-jupyter-notebook-lab
    
"""


