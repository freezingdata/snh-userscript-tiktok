#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   tiktok_posting_html_creator.py
@Time    :   2022/01/07 11:21:18
@Author  :   Benno Krause 
@Contact :   bk@freezingdata.de
@License :   (C)Copyright 2020-2021, Freezingdata GmbH
@Desc    :   None
'''


class TiktokHTMLFactory:
    def __init__(self) -> None:
        pass


    def get_css_simple_posting(self):
        return '''

            .container {
                display: grid;
                grid-template-columns: 100%;
                grid-template-rows: 70% 30%;
                grid-column-gap: 20px
                grid-row-gap: 20px
                justify-items: stretch
                align-items: stretch
            }        

            .image img{
                height: 100%;
                max-width: 400px;
                display: block;
                margin: auto;
            }

            .content {
                font-family: Arial, Helvetica, sans-serif;
                font-size: 17px;
                letter-spacing: -0.4px;
                word-spacing: 2px;
                color: #323232;
                font-weight: normal;
                text-decoration: none;
                font-style: normal;
                font-variant: normal;
                text-transform: none;
            }            
         
        '''   

    def create_simple_posting(self, snh_posting, tt_posting):
        return f'''
            <div class="container">
            <div class="image"><img border="0" src="{tt_posting["video"]["originCover"]}" ></div>
            <div class="content">{snh_posting["Text"]}</div>
            </div>
        
        '''