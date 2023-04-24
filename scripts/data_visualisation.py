"""This file contain methods to generate visualisation of twitter data"""

import json
from collections import Counter

import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from langcodes import *
from wordcloud import WordCloud, STOPWORDS


def plot_verified_proportion(df, column_name, row, col, keywords, export=False, export_to=''):
    """Plots proportion of verified useres using the keyword"""
    fig, axs = plt.subplots(row, col, figsize=(10, 5))

    axis = [[i, j] for j in range(col) for i in range(row)]

    for i in range(len(keywords)):
        data = df.loc[df[column_name].str.contains(keywords[i], case=False), 'verified'].value_counts()
        axs[axis[i][0], axis[i][1]].pie(data, labels=data.index, autopct='%.0f%%', shadow=True,
                                        textprops={'size': 'smaller'}, )
        axs[axis[i][0], axis[i][1]].set_title(keywords[i][:15])
    plt.suptitle(f'verified user proportion based on {column_name}'.upper())
    plt.tight_layout()
    if export:
        plt.savefig(f'{export_to}{column_name}_verified.png', bbox_inches='tight', dpi=300)
    plt.show()


def plot_timeseries(df, keywords, column_name, export=False, export_to=''):
    """Plots a timeseries plot of tweets based on the frequency of keywords provided"""

    keywords = list(keywords.keys())

    df['created_at'] = pd.to_datetime(df['created_at'])

    fig = go.Figure()

    for keyword in keywords:
        data = df.loc[df[column_name].str.contains(keyword, case=False), ['created_at', 'hashtags',
                                                                          'context_annotations']].resample('W',
                                                                                                           on='created_at')[
            column_name].count()
        fig.add_trace(go.Bar(x=data.index,
                             y=data.values,
                             name=keyword,
                             ))

    fig.update_layout(
        title=column_name.upper(),
        xaxis_tickfont_size=14,
        yaxis=dict(
            title='tweets count',
            titlefont_size=16,
            tickfont_size=14,
        ),
        legend=dict(
            x=1.0,
            y=1.0,
            bgcolor='rgba(255, 255, 255, 0)',
            bordercolor='rgba(255, 255, 255, 0)'
        ),
        barmode='stack',
        hovermode="x")

    if export:
        fig.to_html(full_html=False, include_plotlyjs='cdn')
        fig.write_html(f"{export_to}{column_name}.html", full_html=False, include_plotlyjs='cdn')
    fig.show()


def plot_wordcloud(df, column_name, max_words=50, stop_words=None, collocations=False, export_to=''):
    """This function generates a wordcloud for given column name"""

    if stop_words is None:
        stop_words = []
    df.loc[df.loc[:, column_name] == False, 'context_annotations'] = ''

    text = ",".join(hashtag for hashtag in df[column_name])
    text = text.lower()

    # Create stopword list:
    stopwords = set(STOPWORDS)
    stopwords.update(stop_words)

    # Generate a word cloud image
    wordcloud = WordCloud(stopwords=stopwords, background_color="white", collocations=collocations,
                          max_words=max_words).generate(text)

    # Display the generated image:
    # the matplotlib way:
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.savefig(f'{export_to}{column_name}_wordcloud.png', bbox_inches='tight', dpi=300)
    plt.show()


def plot_language_chart(df, n_lang=None, export=False, export_to=''):
    """Plots a pie chart of languages used in the twitter data set"""
    lang = df['lang'].value_counts()
    if n_lang is None:
        n_lang = len(lang)
    lang = lang[:n_lang]
    # Change language code to language name
    lang.index = [Language.make(language=standardize_tag(l)).display_name() for l in lang.index]

    fig = px.pie(lang, values=lang.values, names=lang.index)
    fig.update_traces(textposition='inside')
    fig.update_layout(title='language of tweets downloaded'.upper(), uniformtext_minsize=12, uniformtext_mode='hide',
                      hovermode='x')
    fig.add_annotation(
        text="Note- qht: Tweets with hashtags only | qam: Tweets with mentions only | qme: Tweets with media links",
        xref="x domain", yref="y domain",
        x=0.0, y=-0.2, showarrow=False)

    if export:
        fig.to_html(full_html=False, include_plotlyjs='cdn')
        fig.write_html(f"{export_to}languages.html", full_html=False, include_plotlyjs='cdn')
    fig.show()


def get_top_tweets(df):
    """Prints top tweets in the data set"""
    columns = ['retweet_count', 'reply_count', 'like_count', 'quote_count', 'impression_count', ]
    d = {}
    for col in columns:
        d[col] = df.sort_values(by=col, ascending=False)[['text', col, 'username']][:1]

    print(
        f"Following is the most retweeted tweet authored by {d['retweet_count']['username'].item()} with retweet "
        f"count of {d['retweet_count']['retweet_count'].item()}\n {d['retweet_count']['text'].item()}")

    print(
        f"\n\n Following is the most liked tweet authored by {d['like_count']['username'].item()} with like count of {d['like_count']['like_count'].item()}\n {d['like_count']['text'].item()}")

    print(
        f"\n\n Following is the most replied tweet authored by {d['reply_count']['username'].item()} with reply "
        f"count of {d['reply_count']['reply_count'].item()}\n {d['reply_count']['text'].item()}")

    print(
        f"\n\n Following is the most quoted tweet authored by {d['quote_count']['username'].item()} with quote "
        f"count of {d['quote_count']['quote_count'].item()}\n {d['quote_count']['text'].item()}")

    print(
        f"\n\n Following is the tweet with most impressions authored by {d['impression_count']['username'].item()} with impression count of {d['impression_count']['impression_count'].item()}\n {d['impression_count']['text'].item()}")


def get_relevant_hashtags(df, relevant_context, export_to=''):
    """Plots and prints hashtags used in the listed relevant contexts"""
    # Identify the hashtags used by these contexts
    relevant_hashtags = []
    for context in relevant_context:
        data = list(df.loc[df['context_annotations'].str.contains(context, case=False), 'hashtags'])
        relevant_hashtags.append(data)

    relevant_hashtags = ','.join(map(str, relevant_hashtags)).strip("[']").replace("'", "").strip(' ').split(',')

    relevant_hashtags = list(filter(None, relevant_hashtags))
    relevant_hashtags = Counter(relevant_hashtags)

    relevant_hashtags = dict(relevant_hashtags.most_common(10))

    print(f"{relevant_hashtags}\n\n\n")
    fig, ax = plt.subplots(1, 1, figsize=(10, 5))
    ax.pie(relevant_hashtags.values(), labels=relevant_hashtags.keys(), autopct='%.0f%%', shadow=False,
           textprops={'size': 'smaller'}, )
    plt.suptitle(f'Hashtags used in tweets having relevant context annotations'.upper())
    plt.tight_layout()
    plt.savefig(f'{export_to}most_relevant_hashtags.png', bbox_inches='tight', dpi=300)
    plt.show()


def get_count(df, column_name):
    """Returns a counter of hashtags or context annotations in the twitter dataset"""
    # Create a list of hashtags
    elements = df[column_name].str.split(',').explode().str.lower().to_list()
    # remove white space
    elements = [element.strip().lower() for element in elements]
    # Remove empty strings
    elements = list(filter(None, elements))
    # Count the occurrence of hashtags
    elements = Counter(elements)
    return elements


def read_json(file_name):
    """This function reads the json file and returns a pandas DataFrame"""
    # Opening JSON file
    file = open(file_name)
    # returns JSON object as a dictionary
    data = json.load(file)
    # Closing files
    file.close()
    # convert to a pandas DataFrame
    data = pd.DataFrame.from_dict(data)
    return data


def get_popular_users(tweets, user_count=50):
    "Returns a unique list of popular users based on followers"
    popular_users = \
        tweets.sort_values(by='followers_count', ascending=False).drop_duplicates(subset='username', inplace=False)[
            'username'].to_list()[:user_count]
    return popular_users
