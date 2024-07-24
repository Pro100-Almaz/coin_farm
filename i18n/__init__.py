class I18N:
    _STRINGS = {
        'bot.default_text': {
            'ru': """""",
            'kk': """""",
            'en': """
    How to play Coin Earn ⚡️
    
💰 Tap to earn
Tap the screen and collect coins.

⛏ Mine
Upgrade cards that will give you passive income opportunities.

⏰ Profit per hour
The exchange will work for you on its own, even when you are not in the game for 3 hours.
Then you need to log in to the game again.

📈 LVL
The more coins you have on your balance, the higher the level of your exchange is and the faster you can earn more coins.

👥 Friends
Invite your friends and you’ll get bonuses. Help a friend move to the next leagues and you'll get even more bonuses.

🪙 Token listing
At the end of the season, a token will be released and distributed among the players.
Dates will be announced in our announcement channel. Stay tuned!

/help to get this guide
"""
        },
        'bot.error_message': {
            'ru': "",
            'kk': "",
            'en': "Sorry some trouble occurred! Please try again.",
        },
        'bot.success_message': {
            'ru': "",
            'kk': "",
            'en': "You have just get subscriber by ID: {referred_id}!",
        },
        'bot.help_message': {
            'ru': "",
            'kk': "",
            'en': "HELP!",
        }
    }

    def get_string(self, key, lang = 'en') -> str:
        return self._STRINGS.get(key, {}).get(str(lang), f'[INVALID_TRANSLATION:{lang}:{key}]')


i18n = I18N()