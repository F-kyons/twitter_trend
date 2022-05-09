# coding: utf-8

from PIL import Image
import streamlit as st
import streamlit.components.v1 as stc
from .libs import analysis_tweet

def app():
    '''
    ツイート情報からトレンドを分析する
    '''
    st.title('Twitter Trend')
    col1, col2 = st.columns(2)
    topic_list = analysis_tweet.read_topic_from_csv()

    with col1:
        topic = st.selectbox('トピックを選択',topic_list)
        if topic in topic_list and topic != '選択してください':
            tweet_data = analysis_tweet.get_tweet_data(topic)
            trend_word_list = tweet_data[0]
            new_diff_dict = tweet_data[1]
            word_tweet_dict = tweet_data[2]

            # WordCloudで画像を埋め込む
            analysis_tweet.plot_wordcloud(new_diff_dict,topic)
            image = Image.open(f'./apps/data/img/wordcloud_{topic}.png')
            st.image(image, caption='トレンドワード')

            # トレンドワードの表を埋め込む
            df_trend = analysis_tweet.create_dataframe(trend_word_list)
            st.write(df_trend)

            with col2:
                initial_value = "キーワードを入力"
                tweet_count = 0
                account_count = 0
                tweet = ''
                search_text = st.text_input('投稿検索', value=initial_value)

                if search_text in word_tweet_dict.keys():
                    for tweet_detail in word_tweet_dict[search_text]:
                        account_count += 1
                        for tweet_account in tweet_detail:
                            tweet_count += 1
                            tweet = tweet + analysis_tweet.get_tweet_html(tweet_account[0],tweet_account[1])

                    st.write('投稿一覧')
                    stc.html(tweet,height=560,scrolling=True)
                
                elif search_text == initial_value:
                    pass
                
                else:
                    st.write('トレンドワードからキーワードを選択してください。')
