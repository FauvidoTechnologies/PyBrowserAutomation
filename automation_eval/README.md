# Evaluation prompts and traceviews

This directory is to hold all the prompts and their tracebacks that `pyba` has been evaluated with.

## Level 1: Simple Navigation & Interaction

Focus: Single-page navigation, simple element actions

1. “Go to example.com.”
2. “Search for ‘laptops’ on Amazon.”
3. “Open Google and search for ‘current weather in London’.”
4. “Visit Wikipedia and go to the page about Artificial Intelligence.”
5. “Go to YouTube and click the first video on the homepage.”
6. “Open Reddit and log in using the saved credentials.”
7. “Go to github.com/openai and click the first repository.”

## Level 2: Multi-step Tasks

Focus: Sequence of actions, form filling, waiting, link handling

1. "Go to Twitter, search for ‘AI trends’, and screenshot the top 3 posts.”
2. “Open Gmail, click Compose, and draft an email to abc@example.com with subject ‘Test’ and message ‘This is a test email.’”
3. “Log in to LinkedIn and search for people named ‘John Smith’.”
4. “Visit Booking.com, search for hotels in Paris, and filter by 4 stars.”
5. “Go to YouTube, search for ‘lofi music’, and copy the link of the top result.”
6. “Fill out the contact form on example.com/contact with name, email, and a short message.”
7. “Open Hacker News and extract all post titles on the front page.”

## Level 3: Conditional & Data Extraction Tasks

Focus: Logic, looping, data handling, dynamic content

1. “Go to Amazon and list the names and prices of the first 10 ‘wireless earbuds’.”
2. “Search Google for ‘Python tutorials’, then open the first result that’s from realpython.com.”
3. “Visit Flipkart, search for ‘mobile phones’, and store links of all products under ₹20,000.”
4. “Check whether example.com has a ‘Contact Us’ link, and click it if it exists.”
5. “Scrape the titles of trending videos on YouTube and download their thumbnails.”
6. “Log in to Instagram, go to my DMs, and screenshot the last 5 messages.”
7. “Open CNN and summarize the headlines on the homepage.”

## Level 4: Multi-site Workflows

Focus: Cross-site context retention, file upload/download, chaining logic

1. “Download the latest report from Google Drive and upload it to Dropbox.”
2. “Find a random Wikipedia article, copy its title, and search it on YouTube.”
3. “Go to Amazon, find the top-rated keyboard, and check its price on Flipkart.”
4. “Extract today’s stock price for Apple from Google, then write it into a Google Sheet.”
5. “Login to Gmail, find unread emails from ‘GitHub’, and save all attachments locally.”
6. “Download a CSV file from example.com/data, open it in Google Sheets, and share it with test@example.com.”

## Level 5: Complex, Contextual, or Semi-Autonomous Workflows

Focus: Goal-driven logic, autonomous navigation, adaptation to layout differences

1. “Find and apply to 3 remote data analyst jobs that match my resume on LinkedIn.”
2. “Find a trending news article about AI, summarize it, and tweet the summary.”
3. “Go to a real estate website and list all 2BHK apartments in Bangalore under ₹50,000/month.”
4. “Monitor price changes for the MacBook Air on Amazon every hour and alert me if it drops below ₹90,000.”
5. “Log into my website’s admin panel, publish a new blog post titled ‘Automation Trends 2025’ with content from a local markdown file.”
6. “Compare the prices of ‘Samsung Galaxy S24’ across Amazon, Flipkart, and Croma, and report the lowest one.”
7. “Automatically fill a web form using data from a CSV file, submitting once per row.”
8. “Go to YouTube, find 5 videos about ‘OpenAI GPT-5’, extract their titles, views, and upload dates, and save them to a JSON file.”

## Level 6: Fully Autonomous Goal-Oriented Tasks

Focus: Generalization, dynamic DOMs, error recovery, semantic reasoning

1. “Find me a cheap flight from Delhi to Bangalore next weekend and send me the booking page link.”
2. “Identify the email signup form on techcrunch.com and subscribe using abc@example.com.”
3. “Monitor Hacker News and alert me when a post mentions ‘WebAssembly’.”
4. “Research top 5 Python frameworks for browser automation, extract details from at least 3 websites, and summarize the findings.”
5. “Log into my CMS, check for broken links in the last 5 posts, and fix them if possible.”