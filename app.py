# coding: utf-8

from multiapp import MultiApp
from apps import add_topic, search_trend

app = MultiApp()

app.add_app('Sesrch Trend', search_trend.app)
app.add_app('Add Topic', add_topic.app)

app.run()