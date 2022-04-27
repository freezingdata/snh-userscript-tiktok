# TikTok Usermodule
This repository contains a user module for the Social Network Harvester - https://www.socialnetworkharvester.de/.

# Functions
 - Detecting and collecting of TikTok profiles .
 - Collecting of TikTok timelines with videos and wysiwyg screenshot.
 - Collecting of timeline comments (1st level and 2nd level)
 - Fast collecting method, exclusively to save videos

# Configuration
Because of the strict account policy of TikTok, it's necessary to use a current user agent in SNH. You can set the user agent in the file **C:\Users\%USERNAME%\AppData\Roaming\SocialNetworkHarvester**

A current user agent is:

    Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36

The module is configurable via the tiktok_config.py file.

    modul_config = {
        # simple_timeline_collection
        # Type: boolean
        # If its set to True, just the videos will be collected.
        # To collect comments, or save the original posting screenshot, it has set to False
        "simple_timeline_collection": False,
    
        # limit_root_comments
        # Type: boolean
        # True if the count of collected 1st level comments should be resticted
        "limit_root_comments": True,
    
        # limit_root_comment_count
        # Type: integer
        # Max count of 1st level comments, which can be collected,
        "limit_root_comment_count": 400,
    
        # load_comment_answers
        # Type: boolean
        # Indicates whether comment answers should be collected or not
        "load_comment_answers": True,
    
        # limit_comment_answers
        # Type: boolean
        # If is is set True, answers are just collected, if it's root comment is inside the limit_comment_answers_count limit
        "limit_comment_answers": True,    
    
        # limit_comment_answers_count
        # Type: integer
        # Max count of 1st level comments, which are considered for checking of answers
        "limit_comment_answers_count": 100,
    }

# License

Distributed under the GNU General Public License. See `LICENSE.txt` for more information.
Programs described/provided/linked in/to this Project are free software except otherwise stated. You can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details. You should have received a copy of the GNU General Public License along with this program. If not, see http://www.gnu.org/licenses/.


# Imprint
## Angaben gemäß § 5 TMG

Freezingdata GmbH  
Am Riet 3  
47929 Grefrath

vertretungsberechtigte Geschäftsführer:  
Herr Benno Krause, M.Sc.  
Herr Erik Nolte, M.Sc.

## Kontakt:

Telefon: 02158-6998951  
E-Mail: [info@freezingdata.de](mailto:info@freezingdata.de%EF%BB%BF)

Registergericht: Amtsgericht Krefeld  
Registernummer: HRB 17240  
Umsatzsteuer-ID: DE324063969

Inhaltlich verantwortlich gemäß § 55 Abs. 2 RStV:  
Herr Benno Krause, Herr Erik Nolte, M.Sc.  
Kontaktdaten wie oben

Unser Angebot richtet sich ausschließlich an Unternehmer.

Unser Impressum gilt auch für die nachfolgenden Social Media-Präsenzen:

Twitter: [https://twitter.com/snharvester](https://twitter.com/snharvester)  
Linkedin: [https://www.linkedin.com/company/freezingdata](https://www.linkedin.com/company/freezingdata)  
Xing: [https://www.xing.com/companies/freezingdatagmbh](https://www.xing.com/companies/freezingdatagmbh)  
Instagram: [https://www.instagram.com/socialnetworkharvester/](https://www.instagram.com/socialnetworkharvester/)  
Youtube: [https://www.youtube.com/channel/UCZCYsWV7xII8_tyW_pf5o4A/](https://www.youtube.com/channel/UCZCYsWV7xII8_tyW_pf5o4A/)

