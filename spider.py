# !/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import re
import requests
import json
import time
import datetime
import logging
import smtplib
from config import *
from bs4 import BeautifulSoup
from email.mime.text import MIMEText
from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr


def get_response(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    response.encoding = response.apparent_encoding
    return response.text

def get_info_list(text):
    soup = BeautifulSoup(text, 'html.parser')
    soup_category = soup.find_all('a', href=re.compile('\?infotype'), title='')
    soup_organization = soup.find_all('a', href='#')
    soup_title = soup.find_all('td', align='left')
    soup_time = soup.find_all('td', style="font-size: 9pt", align="center")

    res = []

    list_category = [c.text for c in soup_category]
    list_organization = [c.text for c in soup_organization][1:]
    list_title = [c.text for c in soup_title]
    list_time = [c.text for c in soup_time if '-' in c.text]


    for i in range(len(list_category)):
        category = list_category[i]
        organization = list_organization[i]
        title = list_title[i]
        time = list_time[i]
    
        data = {
        'category': category,
        'organization': organization,
        'title': title,
        'time': time
        }

        res.append(data)
    return res



def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))


def get_email_content(data):
    send_str = '<p>以下是最新的公文通，请享用~</p>'
    for el in data:
        send_str += '''
            <table style="font-size:8pt">
                <tr>
                <td>category: </td>
                <td>{}</td>
                </tr>
                <tr>
                <td>organization: </td>
                <td>{}</td>
                </tr>
                <td>title: </td>
                <td>{}</td>
                </tr>
                <td>time: </td>
                <td>{}</td>
                </tr>
            </table>
            </br>
            <hr>
            '''.format(el['category'], el['organization'], el['title'], el['time'])
    return send_str


def send_email(send_str):

    msg = MIMEText(send_str, 'html', 'utf-8')
    msg['From'] = _format_addr('公文通小助手 <%s>' % from_addr)
    msg['To'] = _format_addr('管理员 <%s>' % to_addr)
    msg['Subject'] = Header('快来打开新鲜出炉的公文通叭~', 'utf-8').encode()
    server = smtplib.SMTP(smtp_server, 25)
    # server.starttls()
    server.set_debuglevel(1)
    server.login(from_addr, password)
    
    count = 6
    while count:
        try:
            server.sendmail(from_addr, to_addr, msg.as_string())
            break
        except Exception as e:
            logging.error(e)
            count -= 1

    server.quit()


def get_current_hour():
    return str(datetime.datetime.now())[11: 13]



if __name__ == "__main__":

    url = 'https://www1.szu.edu.cn/board/infolist.asp'
    while True:
        if get_current_hour() == '08' or get_current_hour() == '20':
            msg = get_email_content(get_info_list(get_response(url)))
            send_email(msg)
            logging.info('send successfully!')

        time.sleep(3600)
        
            
        
    
    