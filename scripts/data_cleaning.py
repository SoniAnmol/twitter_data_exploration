"""This script cleans the data scraped from twitter"""
# import libraries
import json
import pandas as pd
from tqdm import tqdm


def read_json(file_name):
    """This function reads the json file"""
    # Opening JSON file
    file = open(file_name)
    # returns JSON object as a dictionary
    data = json.load(file)
    # Closing file
    file.close()
    return data


def extract_parameters(tweets):
    """This function extract the parameters for each tweet and store it in a separate column"""
    delimiter = ', '
    tweets['hashtags'] = ''
    tweets['annotations'] = ''
    tweets['urls'] = ''
    tweets['mentions_ids'] = ''
    tweets['mentions_usernames'] = ''
    tweets['referenced_type'] = ''

    # Iterate through tweets to unpack entities
    for index, tweet in tqdm(tweets.iterrows(), total=len(tweets)):
        # Look for hashtags in the tweet
        hashtags = tweet['entities']['hashtags']
        if hashtags:
            tweets.loc[index, 'hashtags'] = delimiter.join([hashtag['tag'] for hashtag in hashtags])

        # Look for entity annotation
        annotations = tweet['entities']['annotations']
        if annotations:
            tweets.loc[index, 'annotations'] = delimiter.join(
                [annotation['normalized_text'] for annotation in annotations])

        # Look for urls
        urls = tweet['entities']['urls']
        if urls:
            tweets.loc[index, 'urls'] = delimiter.join([url['expanded_url'] for url in urls])

        # Look for mentions
        mentions = tweet['entities']['mentions']
        if mentions:
            tweets.loc[index, 'mentions_ids'] = delimiter.join([mention['id'] for mention in mentions])
            tweets.loc[index, 'mentions_usernames'] = delimiter.join([mention['username'] for mention in mentions])

        # Check for referenced tweets
        referenced_tweets = tweet['referenced_tweets']
        if referenced_tweets:
            tweets.loc[index, 'referenced_type'] = delimiter.join(
                [referenced_tweet['type'] for referenced_tweet in referenced_tweets])
            tweets.loc[index, 'referenced_tweets'] = delimiter.join(
                [referenced_tweet['id'] for referenced_tweet in referenced_tweets])

        # Check for context annotations
        context_annotations = tweet['context_annotations']
        if context_annotations:
            annotation = [j['name'] for j in
                          [context_annotations[i]['entity'] for i in range(len(context_annotations))]]
            tweets.loc[index, 'context_annotations'] = delimiter.join(list(dict.fromkeys(annotation)))
        else:
            tweets.loc[index, 'context_annotations'] = False

    # Drop redundant column
    tweets = tweets.drop(columns=['entities'])

    return tweets


# select the location to perform cleaning operation
locations = ['australia', 'mumbai', 'northamerica', 'europe', 'texas']

# iterate over locations and save the cleaned for each location
for location in locations:
    # read files
    tweets = read_json(f'../data/sample/{location}/sample_tweets.json')
    users = read_json(f'../data/sample/{location}/sample_users.json')

    # convert dict to DataFrame
    tweets = pd.DataFrame.from_dict(tweets)
    users = pd.DataFrame.from_dict(users)

    # rename column names for coherence
    users.rename(columns={'id': 'author_id', 'public_metrics': 'author_metrics', 'created_at': 'account_created',
                          'entities': 'author_entities', 'location': 'account-location', 'url': 'author_url'},
                 inplace=True)

    # drop duplicates
    users.drop_duplicates(subset=['author_id'], keep='first', inplace=True)
    tweets.drop_duplicates(subset=['id'], keep='first', inplace=True)

    # merge tweets and user data
    df = pd.merge(left=tweets, right=users, on='author_id', right_index=False)

    # Extract public metrics of tweets
    df = pd.concat([df.drop(['public_metrics'], axis=1), df['public_metrics'].apply(pd.Series)], axis=1)

    # Extract public metrics of author
    df = pd.concat([df.drop(['author_metrics'], axis=1), df['author_metrics'].apply(pd.Series)], axis=1)

    # Extract tweet location details
    df = pd.concat([df.drop(['geo'], axis=1), df['geo'].apply(pd.Series)], axis=1)

    # Extract other parameters (entities, referenced tweets, etc.)
    df = extract_parameters(df)

    # Export the json
    df.to_json(f'../data/sample/cleaned/{location}_tweets.json')

    print(f"{len(df['conversation_id'].unique())} unique tweets and overall {len(df)} tweets cleaned for {location}")
