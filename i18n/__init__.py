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
            'en': """
            FAQ: How to Play Meme Empire

1. What is Meme Empire? 🌍
Meme Empire is a fun and addictive tap game where you build your own meme empire by collecting meme cards, upgrading them, improving your character and earning coins. Compete with friends to become the ultimate meme tycoon!

2. How do I start playing? 📱
- Follow the on-screen instructions to get started.
- Tap the screen to collect your first coins and begin your journey.
- Upgrade Vaults Upgrade your dark vaults to earn passive income.
- Hourly Income Your dark empire will work for you on its own, even when you are not in the game, for 3 hours.  
📈 Level Up The more memcoins you have on your balance, the higher the level of your empire. The higher the level, the faster you can earn even more memcoins.
3. How do I collect cards?  🎴
- Simply buy them in the shop. The more you tap, the more cards you can collect.

4. What is passive income? ⏳💸
- Passive income is the coins you earn even when you're not actively tapping the screen.
- Purchase upgrades to increase your passive income and earn coins while you're away.

7. How do I invite friends and why should I? 🤳
- Invite friends to join Meme Empire by sharing your invite link from within the game.
- Playing with friends can make the game more enjoyable and you can earn additional rewards and bonuses by inviting friends.

8. How do I claim gifts and rewards? 🎁
- Occasionally, you'll receive gifts and rewards in the game. These can be claimed from the "Rewards" section.
- For example, say thanks to Nursultan and claim your gift of 5000 memecoins.

9. Are there any special events or challenges?  ✨
- Yes! Meme Empire frequently hosts special events and challenges. Keep an eye on the game’s notifications to participate and earn exclusive rewards.

10. Where can I get help if I have issues or questions? 🚨
- If you need assistance, you can reach out to our support team via the "Help" section in the game or visit our official website for more information.

---

🪙 Token Listing: coming soon… 🤫
Happy meme collecting! 🐸✨""",
        },
        'bot.invited_client_welcome_text': {
            'ru': "🎉Привет, {user_nickname}! Это Meme Empire! 🎉\n"
                  "Теперь ты — король мемов! 👑 Тапай по экрану, собирай мемные карточки и развивай свою мемную империю. А если друзей "
                  "позовешь, то вместе вы подниметесь на вершину империи и заработаете больше монет. 🏆"
                  "Скажи спасибо “user_invite_name” и забирай подарок — 5000 мемкоинов 😌",
            'en': " 🎉Hello, {user_nickname}! This is Meme Empire! 🎉\n"
                  "Now you are the king of memes! 👑 Tap on the screen, collect name cards and develop your meme empire. "
                  "And if you make friends, then together you will rise to the top of the empire and earn more coins. 🏆"
        },
        'bot.client_welcome_text': {
            'ru': "🎉Привет, {user_nickname}! Это Meme Empire! 🎉 \n"
                  "Теперь ты — король мемов! 👑 Тапай по экрану, собирай мемные карточки и развивай свою мемную империю. "
                  "А если друзей позовешь, то вместе вы подниметесь на вершину империи и заработаете больше монет. 🏆",
            'en': " 🎉Hello, {user_nickname}! This is Meme Empire! 🎉 \n"
                  "Now you are the king of memes! 👑 Tap on the screen, collect name cards and develop your meme empire. "
                  "And if you make friends, then together you will rise to the top of the empire and earn more coins. 🏆"
        }
    }

    def get_string(self, key, lang = 'en') -> str:
        return self._STRINGS.get(key, {}).get(str(lang), f'[INVALID_TRANSLATION:{lang}:{key}]')


i18n = I18N()