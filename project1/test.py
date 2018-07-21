import requests
res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "5ccG1d3jk4MQbymFZ4LsdQ", "isbns": "9781632168146"})
print(res.json())
