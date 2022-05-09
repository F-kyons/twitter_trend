# coding:utf-8

'''特定のTwitterアカウントのツイートを4週間分取得する
アカウント毎にファイルを作成してツイート内容を書き出す
ツイートの取得開始は2022-04-21 21:00
'''

import os
import sys
import csv
from datetime import datetime,timezone
import tweepy
import pytz
import re
import pandas as pd
import streamlit as st

def auth_twitter(api_key, api_secret, access_key, access_secret):
    '''
    Twitterの認証
    '''
    auth = tweepy.OAuthHandler(api_key, api_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth)

    return api

def change_time_JST(u_time):
    '''
    UTCをJSTに変換する
    '''
    utc_time = datetime(u_time.year, u_time.month, u_time.day, u_time.hour, u_time.minute, u_time.second, tzinfo=timezone.utc)
    jst_time = utc_time.astimezone(pytz.timezone("Asia/Tokyo"))
    # str_time = jst_time.strftime("%Y-%m-%d %H:%M:%S")

    return jst_time

def get_term_by_tweet(tweets):
    '''
    取得したツイートの期間(秒数)を取得する
    '''
    term_time = change_time_JST(tweets[0].created_at) - change_time_JST(tweets[-1].created_at)


    return term_time.total_seconds()

@st.cache
def write_topic_to_csv(topic_list):
    '''トピックリストをファイルに書き出す'''
    with open('./apps/data/topic_data/topic_list.csv', 'w', encoding="utf8") as f:
        writer = csv.writer(f)
        writer.writerow(topic_list)
        print(f'トピックリストに{topic_list[-1]}を追加しました')


def show_account_table(box,topic):
    '''アカウントのリストを表で表示させる'''
    df = pd.DataFrame(st.session_state[f'topic_{topic}_account_list'], columns=[f'Account Name ({topic})'], index= st.session_state[f'topic_{topic}_account_list_count'])
    box.table(df)


@st.cache
def get_tweet(account_list, topic):
    '''
    Twitter認証
    '''
    api_key = "NeIkxd7xh8Vi7f0NOBQOAdaFA"
    api_secret = "MTz4oeY2xpXmsm8x8AdtkX3gDC3H2BlpqlO6yFN2mguQ2nvh45"
    access_key = "1516645190949543944-JttxrlpIH8Dqn74GA5SAzJjNpB0PJC"
    access_secret = "9nnmAMcOmafLU3bG1R3N8bY7DpTfRnqaTNDwikE3SVCTD"

    '''
    特定ツイートの取得
    '''
    dir_path = f'./apps/data/tweet_data/topic/{topic}'
    os.makedirs(dir_path, exist_ok=True)

    # パラメータ
    account_list = account_list        # アカウント     
    count = 50                          # 取得する件数
    want_term = 50*24*60*60            # 取得するツイートの期間の秒数

    for account_count, account in enumerate (account_list, 1):
        print(f'---- [{topic}] Account_{account_count} : {account} ----------------------------------')
        api = auth_twitter(api_key, api_secret, access_key, access_secret)
        tweet_count = 0
        tweets_count = 0
        get_time = 0
        tweet_data = []

        tweets = api.user_timeline(screen_name=account, count=count, include_rts=False, exclude_replies=True, tweet_mode='extended')
        max_id = tweets[-1].id
        tweet_data.append(tweets)
        get_time = get_time + get_term_by_tweet(tweets)
        tweets_count = tweets_count + len(tweets)

        while get_time < want_term:
            try:
                print('get next tweets....')
                print(f'term time : {get_time}')
                print(f'tweet count : {tweets_count}')
                next_tweets = api.user_timeline(screen_name=account, count=count, max_id=max_id, include_rts=False, exclude_replies=True, tweet_mode='extended')
                get_time = get_time + get_term_by_tweet(next_tweets)
                tweet_data.append(next_tweets[1:])
                max_id = next_tweets[-1].id
                tweets_count = tweets_count + len(next_tweets[1:])

            except IndexError as e:
                print(e)
                break

        print('✔finished get tweets!!')
        
        # page_dataに指定した期間分のツイートが多次元で格納されているため分割してファイルに書き込む
        print(f'Account{account_count}.csvファイルに書き込んでいます')
        for i, tweets in enumerate(tweet_data):
            for tweet in tweets:
                with open(f'./apps/data/tweet_data/topic/{topic}/Account{account_count}.csv', 'a', encoding="utf8") as f:
                    writer = csv.writer(f)
                    non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), '')
                    remove_emoji =  tweet.full_text.translate(non_bmp_map)
                    tweet_txt = re.sub(r'https?://[\w/:%#\$&\?\(\)~\.=\+\-]+', '', remove_emoji)
                    tweet_time = change_time_JST(tweet.created_at).strftime("%Y-%m-%d %H:%M:%S")
                    writer.writerow(['@' + account, tweet_time, tweet_txt.replace('\n','').replace(',',''), tweet.id])
            tweet_count = tweet_count + len(tweets) 

        print(f'total_get_time : {get_time}')
        print(f'total_tweet_count : {tweet_count}')
        print('データの取得が完了しました。')

    return 'ok'