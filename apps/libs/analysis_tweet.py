# coding: utf-8

import os
import csv
from datetime import datetime
import re
import MeCab
import pandas as pd
from wordcloud import WordCloud
from matplotlib import pyplot as plt
import streamlit as st

@st.cache
def plot_wordcloud(word_dict,topic):
    '''
    受け取ったワード辞書からWordCloudを利用して画像出力する
    '''
    font_path = r"./apps/setting/ipaexg.ttf"
    wc= WordCloud(background_color='white', colormap='Set2', font_path=font_path , width=480, height=320).fit_words(word_dict)
    plt.imshow(wc)
    plt.xticks([])
    plt.yticks([])
    plt.subplots_adjust(left=0.04, right=0.95, bottom=0.05, top=0.95)
    plt.savefig(f'./apps/data/img/wordcloud_{topic}.png')


@st.cache
def get_tweet_html(account,tweet_id):
    '''
    Tweetの埋め込むためのhtmlを生成する
    '''
    tweet_html = f"""
                <blockquote class="twitter-tweet" data-theme=”dark”>
                &mdash; {account[1:]} ({account}) 
                <a href="https://twitter.com/{account[1:]}/status/{tweet_id}">
                </blockquote> <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
                """

    return tweet_html


@st.cache
def create_dataframe(trend_word_list):
    '''
    トレンドワードの表を作成するためにデータフレームを作成する
    '''
    list_data = []
    index = []
    columns = ['トレンドワード','アカウント数']
    for i,data in enumerate(trend_word_list, 1):
        data = list(data)
        list_data.append(data)
        index.append(i)

    df_trend = pd.DataFrame(list_data,columns=columns,index=index)

    return df_trend


def read_topic_from_csv():
    '''
    トピックリストをファイルから読み出す
    '''
    if os.path.exists('./apps/data/topic_data/topic_list.csv'):
        with open('./apps/data/topic_data/topic_list.csv', 'r', encoding="utf8") as f:
            reader = csv.reader(f)
            topic_list = [row for row in reader]

        return topic_list[0]
    
    else:
        topic_list = ['選択してください']

        return topic_list


@st.cache
def get_tweet_data(topic):
    '''データ整形
    10アカウントの4週分のツイートから1週間分ずつ抜き取りまとめる→4つの配列となりそれぞれをDocとする(rangeは(1,11))'''
    one_term = 7*24*60*60 # 1週間
    start_time = datetime.strptime('2022-05-20 00:00:00', '%Y-%m-%d %H:%M:%S')
    doc_1 = []
    doc_2 = []
    doc_3 = []
    doc_4 = []
    doc = []
    account_list = []
    account_num = 10
    print(f'Search trend word in {topic}....')

    for i in range(1,account_num+1):
        account_doc = []
        print(f'--- Account{i}のデータを取得します ------------')
        flag = 1
        with open(f'./apps/data/tweet_data/topic/{topic}/Account{i}.csv', 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if flag == 1:
                    tweet_time = datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S')
                    term = (start_time - tweet_time).total_seconds()
                    if term < 0:
                        pass
                    elif 0 < term < one_term:
                        #print(term)
                        doc_1.append(row[2])
                        account_doc.append([row[0],row[2],row[3]])
                    else:
                        flag = 2
                        print(f'1週目取得完了 : {len(doc_1)}件')

                if flag == 2:
                    tweet_time = datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S')
                    term = (start_time - tweet_time).total_seconds()
                    if term < one_term*flag:
                        doc_2.append(row[2])
                    else:
                        flag = 3
                        print(f'2週目取得完了 : {len(doc_2)}件')
                        
                if flag == 3:
                    tweet_time = datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S')
                    term = (start_time - tweet_time).total_seconds()
                    if term < one_term*flag:
                        doc_3.append(row[2])
                    else:
                        flag = 4
                        print(f'3週目取得完了 : {len(doc_3)}件')

                if flag == 4:
                    tweet_time = datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S')
                    term = (start_time - tweet_time).total_seconds()
                    if term < one_term*flag:
                        doc_4.append(row[2])
                    else:
                        flag = 0
                        print(f'4週目取得完了 : {len(doc_4)}件')

        account_list.append(account_doc)
        
    doc.append([doc_1,doc_2,doc_3,doc_4])

    # 形態素分析
    # '-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd'
    mecab = MeCab.Tagger('-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd')
    # mecab = MeCab.Tagger('-r ./apps/setting/mecabrc -d ./apps/setting/ipadic')

    # 全データ(4週分)から各週の単語リストを作成
    dict_list = []
    for i in range(4):
        word_dict = {}
        for text in doc[0][i]:
            node = mecab.parseToNode(text)
            while node:
                word = node.surface
                hinshi = node.feature.split(",")[0]
                if hinshi == '名詞':
                    if word in word_dict:
                        word_dict[word] +=1
                    else:
                        word_dict.setdefault(word, 1)

                node = node.next

        dict_list.append(word_dict)

    # dict1にのみ含まれている単語を抽出
    diff_dict_1 = dict_list[0].keys() - dict_list[1].keys() - dict_list[2].keys() - dict_list[3].keys()

    # 各アカウントが保持している1週分のデータから単語リストを作成
    account_dict_list = []
    for i in range(account_num):
        account_word_dict = {}
        for account_text in account_list[i]:
            node = mecab.parseToNode(account_text[1])
            while node:
                word = node.surface
                hinshi = node.feature.split(",")[0]
                if hinshi == '名詞':
                    if word not in account_word_dict:
                        account_word_dict[word] = list()
                        account_word_dict[word].append([account_text[0],account_text[2]])
                    # 一つのツイートに同じ単語が含まれている場合に複数回同じtweetIDがappendされてしまうのを防ぐ
                    elif account_text[2] == account_word_dict[word][-1][1]:
                        pass
                    else:
                        account_word_dict[word].append([account_text[0],account_text[2]])
                    
                node = node.next

        account_dict_list.append(account_word_dict)

    # 一致するkeysに対して出現回数を付与した新たな辞書を作成(何個のアカウントでdoc1にしか含まれていない単語をツイートしているか)
    new_diff_dict = {}
    re_hiragana = re.compile(r'^[あ-ん]{,1}')
    re_katakana = re.compile(r'[\u30A1-\u30F4]{,1}')
    re_roman = re.compile(r'^[a-zA-Z]{,1}')
    re_kanji = re.compile(r'^[\u4E00-\u9FD0]{,1}')
    re_ascii = re.compile(r'[!-~]{,1}')
    re_nakatenn = re.compile(r'[・]{,1}')

    for i in range(account_num):
        for keys in diff_dict_1:
            if keys in account_dict_list[i].keys():
                if re.fullmatch('[0-9]+',keys) or re_hiragana.fullmatch(keys) or re_katakana.fullmatch(keys) or re_roman.fullmatch(keys) or re_kanji.fullmatch(keys) or  re_ascii.fullmatch(keys) or re_nakatenn.fullmatch(keys):
                    pass
                elif keys in new_diff_dict:
                    new_diff_dict[keys] += 1
                else:
                    new_diff_dict.setdefault(keys,1)

    trend_word_list = sorted(new_diff_dict.items(), key=lambda x:x[1], reverse=True)

    # 上記で作成したtuple型の辞書をlistに変換する
    word_list = []
    for trend_word in trend_word_list:
        trend_word = list(trend_word)
        word_list.append(trend_word[0])

    # アカウント毎にトレンドワードとそのワードを含んだTweetIdを抽出し辞書で保持しておく
    # streamlitでリクエストが入るとここの辞書を参照してtweetidを返す
    word_tweet_dict = {}
    for i in range(account_num):
        for word in word_list:
            for keys in account_dict_list[i].keys():
                if word == keys:
                    if word not in word_tweet_dict:
                        word_tweet_dict[word] = list()
                    word_tweet_dict[word].append(account_dict_list[i][keys])

    return trend_word_list, new_diff_dict, word_tweet_dict
