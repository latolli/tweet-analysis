import tweepy
import configparser
from os.path import exists
import csv

#initialize api, not needed if using client
def authentication():
    #read configs
    config = configparser.ConfigParser()
    config.read('config.ini')

    api_key = config['twitter']['api_key']
    api_key_secret = config['twitter']['api_key_secret']
    access_token = config['twitter']['access_token']
    access_token_secret = config['twitter']['access_token_secret']

    # authentication
    auth = tweepy.OAuthHandler(api_key, api_key_secret)
    auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(auth)
    return api

def search_tweets(client, api, num_tweets, hashtag, data_dict, index):
    field_names = ['ID', 'Tweet_ID', 'UserID', 'Username', 'Time', 'Language', 'Text', 'Hashtags','Geo', 'Retweets', 'Replies', 'Likes']
    print("Searching tweets...")

    for tweet in tweepy.Paginator(client.search_recent_tweets, query=hashtag, 
                              tweet_fields=['created_at', 'author_id', 'text', 'lang', 'geo', 'public_metrics', 'conversation_id'], max_results=100).flatten(limit=num_tweets):
        
        #check all hashtags, if none, skip the tweet
        all_hashtags = find_hashtags(str(tweet.text))
        if all_hashtags == 0:
            continue
        tweet_text = str(tweet.text)
        if tweet_text.startswith("RT"):
            continue

        status  = api.get_status(tweet.conversation_id)

        #if the tweet has hashtags, add it to the data
        data_dict.append({'ID': index,
                        'Tweet_ID': tweet.conversation_id,
                        'UserID': tweet.author_id,
                        'Username': status.user.name,
                        'Time': tweet.created_at,
                        'Language': tweet.lang,
                        'Text': str(tweet.text),
                        'Hashtags': find_hashtags(str(tweet.text)),
                        'Geo': tweet.geo,
                        'Retweets': tweet.public_metrics['retweet_count'],
                        'Replies': tweet.public_metrics['reply_count'],
                        'Likes': status.favorite_count
                        })
        index += 1
        #print(index % 100)
        if index % 100 == 0:
            print("Saving 100 new datapoints")
            write_to_csv(data_dict, field_names)
    return data_dict, index

#function for searching tweets
def search_hashtags(start_index, client, api, num_tweets, hashtag1):
    field_names = ['ID', 'Tweet_ID', 'UserID', 'Username', 'Time', 'Language', 'Text', 'Hashtags','Geo', 'Retweets', 'Replies', 'Likes']
    data_dict = []

    index = start_index

    data_dict, index = search_tweets(client, api, num_tweets, hashtag1, data_dict, index)
    
    #write data to csv file
    print("Generating csv file...")
    write_to_csv(data_dict, field_names)


#function for writing data to csv file
def write_to_csv(data_dict, field_names):
    '''Checks if csv file exists, if not creates one and writes data to it'''
    index_counter = 0
    while(True):
        if exists(f'tweetsdata_{index_counter:02d}.csv'):
            index_counter += 1
        else:
            break
    try:
        with open(f'tweetsdata_{index_counter:02d}.csv', 'w', newline='', encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=field_names)
            writer.writeheader()
            writer.writerows(data_dict)
        print("Data saved to tweets_data_", index_counter)
    except PermissionError:
        print('File opened by another program. Please close the file and try again.')
    except IOError:
        print("File write error. Check file permissions.")


#find all hashtag words from the text, if none, return 0
def find_hashtags(text):
    # initializing hashtag_list variable
    hashtags = []
     
    # splitting the text into words
    for word in text.split(): 
        # checking the first character of every word
        if word[0] == '#':
            # adding the word to the hashtag_list
            hashtags.append(word[1:].lower())

    if len(hashtags) < 1:
        hashtags = 0
    return hashtags


if __name__ == '__main__':
    #get api
    api = authentication()
    #initialize client for twitter api
    config = configparser.ConfigParser()
    config.read('config.ini')

    client = tweepy.Client(config['twitter']['bearer_token'])
    
    new_starting_index = 3400

    search_hashtags(new_starting_index, client, api, 5000, "#climatechange OR #climatecrisis OR #climateemergency OR #saveearth OR #climateaction OR #globalwarming OR #savetheplanet")
    print("DONE!")
    
