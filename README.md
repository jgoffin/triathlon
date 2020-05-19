# triathlon
My motivation for this project was wanting to know, as a first time triathlon competitor, what kind of swim time I could aim for given my age, gender, and expected bike/run times (which I had much better idea of, given I had competed in those sports before). The outcome was a project that did the following:
1) Web-scraped triathlon race results from athlinks.com. They had the most comprehensive results and also easily filterable by distance (I specifically wanted Olympic distance results, since that's what I would be racing in). However, their website structure was not ideal for web-scraping. The relevant data was spread across many web-pages (even within races), and web-pages involved a lot of javascript. Maybe they were intentionally discouraging web-scraping efforts! The main script that completes this part is <a href="scraper.py">scraper.py</a>

2) Built a machine learning model in Scikit-Learn. The data inspection, cleaning, and model building process can all be found in <a href="triathlon.ipynb">triathlon.ipynb</a>

3) Designed a flask application that allows for users to input their own variables (age, gender, bike time, run time, etc.), and get back a predicted swim time. (<a href="app.py">app.py</a>)

4) Deployed web-app to AWS ec2 on a Docker container: http://ec2-34-216-76-122.us-west-2.compute.amazonaws.com/
