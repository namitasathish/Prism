# Prism- Moderation Bot 

Prism is a Discord bot that uses machine learning to detect and moderate harmful content in real time. It helps server owners keep chats safe from bullying, spam, and scams while reducing manual moderator workload.

## What Prism Looks Like in Action
1. Live Moderation: Prism watches messages in your channels and takes action instantly
2. Moderator Experience: Moderators can inspect every action Prism takes.
3. Analytics Dashboard: A web dashboard gives high level insight into community 

## Key Features
1. Automated Moderation
- Real time message scanning with an ML model
- Smart filtering for harmful categories
- Customizable thresholds for flagging/deletion
- Automatic DM warnings explaining the violation
2. Safety Workflow
- Flag suspicious content for review
- Auto delete high risk messages
- Warn users and encourage better behavior
3. Moderator Tools
- Web dashboard and activity logs
- Commands like !history [n], !dashboard

## Tech Stack
•	Python 3.8+, discord.py
•	Scikit learn (Logistic Regression + TF IDF)
•	Pandas, NLTK/regex for preprocessing
•	Joblib for model persistence

