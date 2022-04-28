from datetime import datetime, timedelta
from random import randint, choice
import pandas as pd
import os


def generate_random_date(std_time, time_delta_range_start, time_delta_range_end):
    """Generates a random date in past or future within a given time range"""
    past_future = [-1, 1]
    delta = timedelta(days=randint(time_delta_range_start, time_delta_range_end))
    random_date_obj = std_time + delta * choice(past_future)
    return random_date_obj


def random_date_format(date_obj):
    """Randomly choices a datetime format & format the date_obj accordingly"""
    date_time_format_list = [
        "%Y-%m-%d %H:%M:%S",
        "%A, %B %d, %Y %I:%M %p",
        "%Y/%m/%d",
        "%d/%m/%Y",
        "%A %d. %B %Y",
        "%d/%m/%y",
        "%Y %b-%d %H:%M",
        "%m/%d/%Y",
        "%b-%d-%Y",
        "%d %B, %Y",
    ]
    random_format = choice(date_time_format_list)
    random_date = date_obj.strftime(random_format)
    return random_date


def generate_data(row, now_time):
    """Generates appropriate data and inserts them"""
    article, _, _, _, is_deadline, start, end = row
    # Randomly chooses a date and a date-time formate
    rand_dt_obj = generate_random_date(now_time, 1, 100)
    rand_dt = random_date_format(rand_dt_obj)
    article_words = article.split()
    # Randomly chooses a position to insert the date string.
    rand_pos = randint(0, len(article_words))
    article_words.insert(rand_pos, rand_dt)
    # Generates appropriate results
    article = " ".join(article_words)
    is_deadline = 1
    start = rand_pos
    end = start + len(rand_dt)
    return article, is_deadline, start, end


def main():
    if not os.path.exists("data/processed/Processed_Articles.csv"):
        std_time = datetime.now()
        articles = pd.read_csv("data/raw/Articles.csv", encoding="ISO-8859-1")
        # Adding Extra Columns
        new_columns = {"Is_Deadline": 0, "Start": 0, "End": 0}
        articles = articles.assign(**new_columns)
        for index, row in articles.iterrows():
            # Randomly chooses 50% of the data to be positive & 50% of the data negative
            if choice([0, 1]):
                article, is_deadline, start, end = generate_data(row, std_time)
                articles.loc[index, "Article"] = article
                articles.loc[index, "Is_Deadline"] = is_deadline
                articles.loc[index, "Start"] = start
                articles.loc[index, "End"] = end
        # Save Processed Data
        articles.to_csv("data/processed/Processed_Articles.csv")
        print("Data Processing Done!")
    else:
        print("Data Already Processed!")


if __name__ == "__main__":
    main()
