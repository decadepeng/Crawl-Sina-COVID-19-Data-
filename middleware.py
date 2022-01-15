# encoding=utf-8
import random
from cookies import cookies
from user_agents import agents


class UserAgentMiddleware(object):


    def process_request(self, request, spider):
        agent = random.choice(agents)
        request.headers["User-Agent"] = agent


class CookiesMiddleware(object):
   
    def process_request(self, request, spider):
        cookie = random.choice(cookies)
        request.cookies = cookie
