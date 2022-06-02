# coding: utf-8

import streamlit as st
from .libs import get_tweet, analysis_tweet
st.set_page_config(layout="wide")

def app():
    '''
    トピックを追加・削除しツイートデータを取得する
    '''
    st.title('Add Topic')
    if st.button('更新'):
        pass
    initial_value = ''
    account_num = 10
    topic = st.text_input('トピックを追加', value=initial_value)
    account = st.text_input('アカウントを追加( @を除く )', value=initial_value)
    col1, col2 = st.columns(2)
    account_box = st.empty()

    # トピックを追加するテキストに文字が入力された場合に機能する
    topic_list = analysis_tweet.read_topic_from_csv()
    if not topic == initial_value:
        if not topic in topic_list:
            if f'topic_{topic}' not in st.session_state:
                st.session_state[f'topic_{topic}'] = topic

            if 'topic_list' not in st.session_state:
                st.session_state['topic_list'] = topic_list

            if f'topic_{topic}_account_list' not in st.session_state :
                st.session_state[f'topic_{topic}_account_list'] = []

            if f'topic_{topic}_account_list_count' not in st.session_state:
                st.session_state[f'topic_{topic}_account_list_count'] = []

            with col2:
                table_box = st.empty()
                get_tweet.show_account_table(table_box,topic)
            
            with col1:
                # アカウント追加機能
                if st.button('アカウントを追加'):
                    if account == initial_value:
                        account_box.error('アカウント名を入力してください。')

                    elif not account in st.session_state[f'topic_{topic}_account_list']:
                        st.session_state[f'topic_{topic}_account_list'].append(account)
                        st.session_state[f'topic_{topic}_account_list_count'].append('Account_'+str(len(st.session_state[f'topic_{topic}_account_list'])))
                        print(f'アカウントリストに{account}を追加しました。')
                        account_box.success(f'アカウントリストに{account}を追加しました。')
                        with col2:
                            get_tweet.show_account_table(table_box,topic)

                    else:
                        account_box.error('このアカウントはこのトピックに対して既に登録されています。')
                
                with st.expander('アカウントをまとめて追加する'):
                    account_area = st.text_area('複数のアカウントをカンマ(,)区切りで入力してください。','')
                    if account_area != '':
                        st.session_state.account_list = []
                        st.session_state.account_list = account_area.split(',')
                        st.session_state.add_account = ''
                        add_list = ['全て'] + st.session_state.account_list
                        st.session_state.add_account = st.selectbox('追加したいアカウントを選択してください', add_list)

                        if st.button('アカウントの追加'):
                            if st.session_state.add_account == '全て':
                                for add in st.session_state.account_list:
                                    if not add in st.session_state[f'topic_{topic}_account_list']:
                                        st.session_state[f'topic_{topic}_account_list'].append(add)
                                        st.session_state[f'topic_{topic}_account_list_count'].append('Account_'+str(len(st.session_state[f'topic_{topic}_account_list'])))

                                    else:
                                        account_box.error('このアカウントはこのトピックに対して既に登録されています。')

                                    with col2:
                                        get_tweet.show_account_table(table_box,topic)

                                account_box.success(f'アカウントリストに全てのアカウントを追加しました。')

                            elif not st.session_state.add_account in st.session_state[f'topic_{topic}_account_list']:
                                st.session_state[f'topic_{topic}_account_list'].append(st.session_state.add_account)
                                st.session_state[f'topic_{topic}_account_list_count'].append('Account_'+str(len(st.session_state[f'topic_{topic}_account_list'])))
                                account_box.success(f'アカウントリストに{st.session_state.add_account}を追加しました。')
                                with col2:
                                    get_tweet.show_account_table(table_box,topic)

                            else:
                                account_box.error('このアカウントはこのトピックに対して既に登録されています。')

            with col1:
                # アカウント削除機能
                if len(st.session_state[f'topic_{topic}_account_list']) == 0:
                    pass

                elif 0 < len(st.session_state[f'topic_{topic}_account_list']) < 2:
                    st.session_state.remove_account = ''
                    if st.button('アカウントを削除'):
                        if account in st.session_state[f'topic_{topic}_account_list']:
                            st.session_state[f'topic_{topic}_account_list'].remove(account)
                            st.session_state[f'topic_{topic}_account_list_count'].pop(-1)
                            print(f'アカウントリストから{account}を削除しました。')
                            account_box.success(f'アカウントリストから{account}を削除しました。')
                            with col2:
                                get_tweet.show_account_table(table_box,topic)

                        elif account == '':
                            account_box.error('削除するアカウント名を入力してください。')

                        else:
                            account_box.error('このアカウントはこのトピックに対して登録されていません。')
                            with col2:
                                get_tweet.show_account_table(table_box,topic)

                else:
                    st.session_state.remove_account = st.selectbox('削除したいアカウントを選択してください', ['全て'] + st.session_state[f'topic_{topic}_account_list'])
                    if st.button('アカウントを削除'):
                        if st.session_state.remove_account == '全て':
                            if  len(st.session_state[f'topic_{topic}_account_list']) != 0:
                                st.session_state[f'topic_{topic}_account_list'].clear()
                                st.session_state[f'topic_{topic}_account_list_count'].clear()
                                account_box.success('アカウントリストから全てのアカウントを削除しました。')
                                print('アカウントリストから全てのアカウントを削除しました。')
                                with col2:
                                    get_tweet.show_account_table(table_box,topic)
                            else:
                                account_box.error('アカウントリストには何も登録されていません。')

                        elif st.session_state.remove_account in st.session_state[f'topic_{topic}_account_list']:
                            st.session_state[f'topic_{topic}_account_list'].remove(st.session_state.remove_account)
                            st.session_state[f'topic_{topic}_account_list_count'].pop(-1)
                            print(f'アカウントリストから{st.session_state.remove_account}を削除しました。')
                            account_box.success(f'アカウントリストから{st.session_state.remove_account}を削除しました。')
                            with col2:
                                get_tweet.show_account_table(table_box,topic)

                        else:
                            account_box.error('このアカウントはこのトピックに対して登録されていません。')
                            with col2:
                                get_tweet.show_account_table(table_box,topic)

            with col1:
                # ツイート取得機能
                if len(st.session_state[f'topic_{topic}_account_list']) > 0:
                    if st.button('ツイートを取得'):
                        tweet_box = st.empty()
                        if len(st.session_state[f'topic_{topic}_account_list']) == account_num:
                            tweet_box.info('データを取得しています...')
                            if not topic in st.session_state.topic_list:
                                st.session_state.topic_list.append(topic)
                            get_tweet.write_topic_to_csv(st.session_state.topic_list)
                            scrape_status = get_tweet.get_tweet(st.session_state[f'topic_{topic}_account_list'], topic)
                            if scrape_status == 'ok':
                                tweet_box.success('データの取得が完了しました。')

                        elif len(st.session_state[f'topic_{topic}_account_list']) < account_num:
                            account_box.error('合計10個のアカウントを追加してください。')

                        else:
                            over_num = len(st.session_state[f'topic_{topic}_account_list']) - account_num
                            account_box.error(f'{over_num}個のアカウントを削除してください。')

        else:
            st.error(f'{topic}はすでに登録されています。別名で登録してください。')

    elif account != initial_value:
        st.error('トピックを入力してください。')