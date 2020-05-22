
# Welcome to HeyMovie!

  

****HeyMovie**** is a movie recommendation platform that helps users to find movies in an easy and ordered way, the project it's composed of a mobile application and a backend service, The API operation it's going to be explained in detail in this document.

# How to Use:

The API has a set of functionalities that allows managing the following objects:

- Movies

- Ratings

- Tags

In each one of those you can perform CRUD operations.

The API service documentation can be found in the following link:

- [http://wfh-movies.herokuapp.com/docs](http://wfh-movies.herokuapp.com/docs)

  

## Manage GET Movies :

In order to let the user to search a movie of interest the get method for all the objects has the following functionalities that should be sent as parameters in the request :

### Limit:

You can send the number of elements that you want to receive, for example, if you want only 20 movies per request you should use this :

  

[http://wfh-movies.herokuapp.com/movie?limit=20](http://wfh-movies.herokuapp.com/movie?limit=20 "http://wfh-movies.herokuapp.com/movie?limit=20")

### Page:

Allows the selection of the result page in a set of results, the total number of pages is sent by the request.

  

[http://wfh-movies.herokuapp.com/movie?limit=20&page=2](http://wfh-movies.herokuapp.com/movie?limit=20&page=2 "http://wfh-movies.herokuapp.com/movie?limit=20&page=2")

### Sort:

The API allows the user to sort the response given a field, you can sort by ascendent or descendent way, just have to send in the parameter sort, the field name, and the keyword asc or desc.

Example :

  

[http://wfh-movies.herokuapp.com/movie?sort=title.asc](http://wfh-movies.herokuapp.com/movie?sort=title.asc "http://wfh-movies.herokuapp.com/movie?sort=title.asc")

  

In this case, we are sorting the tittle in ascending mode.

### Filter:

Allows to filter the information of the object by fields using the following querys:

Filter data. Input format: operation(field, value). Available operations:

- ****exact****: Matches the exact value.

- ****partial****: Matches the value as contained in the field.

- ****start****: Matches the value as start of field.

- ****end****: Matches the value as end of field.

- ****word_start****: Matches the start of any word in the field.

- ****anyOf****: Matches any field whose value is any from the given set.

In the case of movies exist an aditional filter for the genre:

- ****superset****:  Allows to filter by one or more genres.

## Examples:

### Search Movie Title :

[http://wfh-movies.herokuapp.com/movie?filter=partial(title, Toy)](http://wfh-movies.herokuapp.com/movie?filter=partial%28title,%20Toy%29)

### Search Movie by genre:

[http://wfh-movies.herokuapp.com/movie?filter=superset(genres, \[Adventure\])](http://wfh-movies.herokuapp.com/movie?filter=superset%28genres,%20%5BAdventure%5D%29)

[http://wfh-movies.herokuapp.com/movie?filter=superset(genres, \[Adventure|Animation\])](http://wfh-movies.herokuapp.com/movie?filter=superset%28genres,%20%5BAdventure%7CAnimation%5D%29)

