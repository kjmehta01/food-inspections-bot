# Food Inspections in College Park

## Overview
The code in this repo builds and executes a Slack bot that pulls food inspection data from a csv published by Prince George's county snd updated once a week. Each time the bot runs, a shell script pulls down the latest version of the csv. Then, a python script — labeled app.py — parses the data and cleans it, filtering for new records of establishments in College Park and adding them to a sqlite database named food_inspections.db.  

The bot goes into that db it just added to and retrieves all recent inspections that have an inspection_result of 'Critical Violations Observed" or "non-Compliant - Violations Observed.' If there are new rows (which are defined here as "rows with a date stamp later than the max date last retrieved from the database") the bot uses some for loops, functions and dictionary wrangling to send the channel:  

1. A main message that contains summary information: The number of inspections that resulted in a violation in College Park in the past week, and the names of impacted establishments.  
2. Threaded messages that give users details on each impacted establishment, like the date of the most recent inspection and what triggered it; the number of inspections a business had before and how many of them resulted in a violation; business location (address); the reasons a business failed the inspection; and links to the data and the county's MPIA form, in case reporters want to dig in more.

If there are no new records added to the database, the app still sends a message — it just tells the channel to check back in next week.

## The Journey

Oh, what a journey this Slackbot has been! It began as a shell of what it became, a simple product @rinatorchi and I came up with  to answer the question: "What if we could alert Diamondback reporters about the latest food inspection in one of the dining halls? Or their favorite restaurants?"

The first version of this bot pulled from a json API and changed the data very little before shoving it straight into a sqlite database, courtesy of the sqlite_utils library. "Oh snap," I thought, having written the script to pull from the API and initialize the db within a half hour. "This is going to be so easy!"  

I was, of course, wrong.

Before I figured out that I wasn't pulling recent data because the API stopped updating months before I began using it (more on that in a second), I faced the problem of creating unique row IDs. The Prince Georges County data contains establishment_ids, number sequences that link together all the records for a single, unique establishment. Super helpful for some of the features I gave the bot later, but not awesome for identifying individual inspections. I assumed, however, that a natural key composed of inspection dates and establishment ids would be a foolproof way to go about things.I found that wasn’t the case pretty quickly after I pulled the data into R; there was basically no way to deduplicate rows unless my natural key was comprised of every column. I discarded the idea of a ‘primary key’ after that; I created and kept the unique IDs (estab id + date), but didn’t add them to my schema as a natural key. This way, I was preserving every row in my database, but I still had a way to call most of them up alone. Originally, I’d thought all the data for all the cities in the county could go in the database; I made the decision to narrow it down to just CP here because this city didn’t have any duplicate rows in the data (at least, as of this March). I anticipate that this would cause reporters some concern in the future, because College Park will eventually have duplicates and they’ll show up in my bot’s thread, but I’m planning on calling the data steward at Prince George’s County to talk it through and fix it this week.

I was proud of myself … until a week had gone by and I noticed that the API hadn’t updated. “Huh,” I thought, “Strange. Not a single inspection this past week? Maybe I’ll go peruse the data online to make sure that’s true.” I looked it up: There had been inspections that week. And the week before that. And before that. My data source rendered useless, I hit a minor sticking point. I had to reconfigure the entire backend of my code, after I'd already figured out how to put it in the database and send a Slack message with it via git actions (thanks in no small part to Aadit Taambe, Iris Lee and Ben Walsh's NICAR git actions tutorial). I was annoyed.

It ended up not being a huge deal, though. I looked at my first-web-scraper code, asked Derek a few questions about pulling down csvs with wget, wrote a tiny shell script and added to my main.yml file and boom! I (or rather, the virtual computer I made git actions use) was pulling the most recent version of the county csv to extract data from.

Rather than further refining the backend structures that support my bot, I turned my attention to iteratively designing this app and slowly (but surely) making it better. My original message structure didn’t use markdown or threading, the bot just sent out a single, unformatted text blurb for every impacted establishment every week. I always wanted the bot to give users some background on the establishments it names, but I originally thought reporters would have to use a custom query or slash command to interact with the bot for details. I realized, however, that threading the information would make it both more visually appealing and more accessible — people are more likely to use data sitting right in front of their faces.

My selection of “new” records to be messaged to the channel was originally defined by rowid — records with rowids greater than the maximum one fetched from the db were added to a list then sent out. After a little tussle with the text-string date column, I got the date into a workable format with Python dateparser (thanks, Derek). Now, “new” records are selected by a max date function, so I’m always getting the most recent inspections. When I transformed my message formatting from text to Slack’s block kit, I used bolded text, capitals, emojis and line breaks to make text more digestible. Recently,  I added bullets to listed items in every message and a line for establishment addresses, making summaries and threads longer-but-better.

The app is far from perfect. I’d love to add a link to google maps to every threaded message, so users could just hit a button and head to affected establishments. I haven’t figured out how to display change over time in the number of inspections in CP, and I certainly haven’t yet found a way to bring special, pointed attention to violations caused by insects and rodents (which in my eyes are the worst because EW!). I’m really proud of what I’ve made so far though; I think it’s worth deploying it into the DBK newsroom Slack even as I work to improve it. Building this app has taught me so much, both about the technical realities and paradigm shifts required to develop news applications.
