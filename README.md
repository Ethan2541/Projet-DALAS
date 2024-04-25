# Data Analysis on Books

The goal of this project is to reproduce the whole standard data analysis pipeline on a dataset including books' data. This project is an assignment, which is part of the [DAtascience, Learning and ApplicationS](https://dac.lip6.fr/master/datascience-learning-and-applications-dalas/) course from Sorbonne Université's [Data, Learning and Knowledge](https://dac.lip6.fr/master/) computer science master.


## Data Collection

In order to gather enough books' data to begin my analyses, I have scraped the website [goodreads](https://www.goodreads.com/). I have repeated this process thrice to ensure that I have collected the most books I could. In average, I have found over 8.000 different books, each with their name, author, description, price, ratings, and so on... The webscraping code can be found in `src/webscraping`.

The dataset is likely to have a few bias, as I did not have enough time - unfortunately - to fully scrape [goodreads](https://www.goodreads.com/). For example, one probably won't able to find every book genre listed in [goodreads](https://www.goodreads.com/) as I settled for the ones linked on the homepage; one would find far more recent books than older ones; ... As the database was still quite significant, I have also limited myself to the first ten pages of the books lists (derived from the scraped genres) I have found. Plus, some books' pages couldn't be properly scraped (because they were formatted slighltly differently, ...) and were thus simply ignored.