from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import json
import boto3
import time


class TweetStreamListener(StreamListener):
    # on success
    def on_data(self, data):
        tweet = json.loads(data)
        try:
            if 'text' in tweet.keys():
                message_lst = [str(tweet['id']),
                       str(tweet['user']['name']),
                       str(tweet['user']['screen_name']),
                       tweet['text'].replace('\n',' ').replace('\r',' '),
                       str(tweet['user']['followers_count']),
                       str(tweet['user']['location']),
                       str(tweet['geo']),
                       str(tweet['created_at']),
                       '\n'
                       ]
                message = '\t'.join(message_lst)
                print(message)
                firehose_client.put_record(
                    DeliveryStreamName=delivery_stream_name,
                    Record={
                        'Data': message
                    }
                )
        except (AttributeError, Exception) as e:
            print(e)
        return True

    def on_error(self, status):
        print (status)


if __name__ == '__main__':
    # create kinesis client connection
    session = boto3.Session()
    firehose_client = session.client('firehose', region_name='us-east-1')

    # Set kinesis data stream name
    delivery_stream_name = 'twitter_travel_datastream'
    # delivery_stream_name='arn:aws:kinesis:us-east-1:344180328559:stream/twitter_travel_datastream'

    # Set twitter credentials
    consumer_key = 'FvnHVR2CZ4acy8qrug0rTgLdk'
    consumer_secret = 'HXjZzZTYAoZ0YzlSJEeCLMZtWL3whuOXbevMO8XrzM3VeoC8LN'
    access_token = '717153459380871168-CATUtXNNEup7zEeiYyhgJ27JSvvaE2s'
    access_token_secret = 'zVPQZL5zCwFiDq3C4nMFJFumKzO24xbDbgfdgTMqcd5gh'

    # set twitter keys/tokens
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    while True:
        try:
            print('Twitter streaming...')

            # create instance of the tweet stream listener
            listener = TweetStreamListener()

            # create instance of the tweepy stream
            stream = Stream(auth, listener)

            # search twitter for the keyword
            stream.filter(track=['travel'], languages=['en'], stall_warnings=True)
        except Exception as e:
            print(e)
            print('Disconnected...')
            time.sleep(5)
            continue


