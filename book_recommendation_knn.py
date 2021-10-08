# -*- coding: utf-8 -*-
"""Copy of fcc_book_recommendation_knn.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1aGqsZYc0Ap2GVTOtNiIvYkUsu0f55R7h

*Note: You are currently reading this using Google Colaboratory which is a cloud-hosted version of Jupyter Notebook. This is a document containing both text cells for documentation and runnable code cells. If you are unfamiliar with Jupyter Notebook, watch this 3-minute introduction before starting this challenge: https://www.youtube.com/watch?v=inN8seMm7UI*

---

In this challenge, you will create a book recommendation algorithm using **K-Nearest Neighbors**.

You will use the [Book-Crossings dataset](http://www2.informatik.uni-freiburg.de/~cziegler/BX/). This dataset contains 1.1 million ratings (scale of 1-10) of 270,000 books by 90,000 users. 

After importing and cleaning the data, use `NearestNeighbors` from `sklearn.neighbors` to develop a model that shows books that are similar to a given book. The Nearest Neighbors algorithm measures distance to determine the “closeness” of instances.

Create a function named `get_recommends` that takes a book title (from the dataset) as an argument and returns a list of 5 similar books with their distances from the book argument.

This code:

`get_recommends("The Queen of the Damned (Vampire Chronicles (Paperback))")`

should return:

```
[
  'The Queen of the Damned (Vampire Chronicles (Paperback))',
  [
    ['Catch 22', 0.793983519077301], 
    ['The Witching Hour (Lives of the Mayfair Witches)', 0.7448656558990479], 
    ['Interview with the Vampire', 0.7345068454742432],
    ['The Tale of the Body Thief (Vampire Chronicles (Paperback))', 0.5376338362693787],
    ['The Vampire Lestat (Vampire Chronicles, Book II)', 0.5178412199020386]
  ]
]
```

Notice that the data returned from `get_recommends()` is a list. The first element in the list is the book title passed in to the function. The second element in the list is a list of five more lists. Each of the five lists contains a recommended book and the distance from the recommended book to the book passed in to the function.

If you graph the dataset (optional), you will notice that most books are not rated frequently. To ensure statistical significance, remove from the dataset users with less than 200 ratings and books with less than 100 ratings.

The first three cells import libraries you may need and the data to use. The final cell is for testing. Write all your code in between those cells.
"""

# import libraries (you may add additional imports but you may not have to)
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
import matplotlib.pyplot as plt

# get data files
!wget https://cdn.freecodecamp.org/project-data/books/book-crossings.zip

!unzip book-crossings.zip

books_filename = 'BX-Books.csv'
ratings_filename = 'BX-Book-Ratings.csv'

# import csv data into dataframes
df_books = pd.read_csv(
    books_filename,
    encoding = "ISO-8859-1",
    sep=";",
    header=0,
    names=['bookId', 'title', 'author'],
    usecols=['bookId', 'title', 'author'],
    dtype={'bookId': 'str', 'title': 'str', 'author': 'str'})

df_ratings = pd.read_csv(
    ratings_filename,
    encoding = "ISO-8859-1",
    sep=";",
    header=0,
    names=['userId', 'bookId', 'rating'],
    usecols=['userId', 'bookId', 'rating'],
    dtype={'userId': 'int32', 'bookId': 'str', 'rating': 'float32'})

user_ratingCount = (df_ratings.
     groupby(by = ['userId'])['rating'].
     count().
     reset_index().
     rename(columns = {'rating': 'totalRatingCount'})
     [['userId', 'totalRatingCount']]
)
users_to_remove = user_ratingCount.query('totalRatingCount > 200').userId.tolist()

# function to return recommended books - this will be tested
df = pd.merge(df_ratings,df_books,on='bookId')

book_ratingCount = (df.
     groupby(by = ['title'])['rating'].
     count().
     reset_index().
     rename(columns = {'rating': 'totalRatingCount'})
     [['title', 'totalRatingCount']]
    )

rating_with_totalRatingCount = df.merge(book_ratingCount, left_on = 'title', right_on = 'title', how = 'left')
pd.set_option('display.float_format', lambda x: '%.3f' % x)

rating_popular_movie = rating_with_totalRatingCount.query('totalRatingCount > 100')

rating_popular_movie = rating_popular_movie[rating_popular_movie['userId'].isin(users_to_remove)]

book_features_df = rating_popular_movie.pivot_table(index='title',columns='userId',values='rating').fillna(0)
book_features_df_matrix = csr_matrix(book_features_df.values)

def get_recommends(book = ""):
    model_knn = NearestNeighbors(metric = 'cosine', n_neighbors=5, algorithm='auto')
    model_knn.fit(book_features_df_matrix)

    # found book TODO: user a better search
    for query_index in range(len(book_features_df)):
        if book_features_df.index[query_index] == book:
            break

    # creating return structure
    ret = [book_features_df.index[query_index], []]
    distances, indices = model_knn.kneighbors(book_features_df.iloc[query_index,:].values.reshape(1, -1))
    # now we located the book. lets show the recomendations
    for i in range(1, len(distances.flatten())):
        ret[1].insert(0, [book_features_df.index[indices.flatten()[i]], distances.flatten()[i]])
    return ret

"""Use the cell below to test your function. The `test_book_recommendation()` function will inform you if you passed the challenge or need to keep trying."""

books = get_recommends("Where the Heart Is (Oprah's Book Club (Paperback))")
print(books)

def test_book_recommendation():
  test_pass = True
  recommends = get_recommends("Where the Heart Is (Oprah's Book Club (Paperback))")
  if recommends[0] != "Where the Heart Is (Oprah's Book Club (Paperback))":
    test_pass = False
  recommended_books = ["I'll Be Seeing You", 'The Weight of Water', 'The Surgeon', 'I Know This Much Is True']
  recommended_books_dist = [0.8, 0.77, 0.77, 0.77]
  for i in range(2): 
    if recommends[1][i][0] not in recommended_books:
      test_pass = False
    if abs(recommends[1][i][1] - recommended_books_dist[i]) >= 0.05:
      test_pass = False
  if test_pass:
    print("You passed the challenge! 🎉🎉🎉🎉🎉")
  else:
    print("You haven't passed yet. Keep trying!")

test_book_recommendation()