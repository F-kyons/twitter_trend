# coding: utf-8

import streamlit as st

class MultiApp:
    '''複数のAppに対応'''
    def __init__(self) -> None:
        self.apps = []
    

    def add_app(self, title, func):
        self.apps.append({
            'title': title,
            'function': func
        })

    
    def run(self) -> None:
        st.sidebar.title('Twitter Trend')
        app = st.sidebar.radio(
            'Go To', 
            self.apps,
            format_func=lambda app: app['title']
        )
        app['function']()
        