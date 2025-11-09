
# Talash Search

**Talash is a search algorithm that uses techniques such as reverse index lookup to search large amounts of texts in milliseconds speed**
*Currently presented as a prototype **web search engine**, I am planning to generalize this algorithm to work on any Urdu dataset for fast lookups*
## How Does it Work?
 Given a large dataset, we build a [reverse index](https://en.wikipedia.org/wiki/Reverse_index) and store all the terms along with their respective occurrences in each document.
 This reverse index allows us to lookup data significantly fast.
 ![entire workflow]()

## Tools Used:
[Makhzan](https://github.com/zeerakahmed/makhzan/) Used as a text corpus for algorithm development. 
*Thought this dataset is very small i plan to create a crawler to gather Urdu data from different sites to increase the reach*

[LughaatNLP](https://github.com/MuhammadNoman76/LughaatNLP) Urdu NLP library used for processing Urdu text in order to build a good reverse index.
*Though this library is not optimized for any production use yet (tensor flow dependency). Plans for a more efficient tokenizer and normalizer could be made.*

[MySQL](https://dev.mysql.com/doc/) MySQL is very reliable for handling large UTF-8 datasets. Using the built-in Indexing, we can optimize the performance even more. 
*Though, in embedded cases, we may need to use something like SQLite*
 
[Flask](https://flask.palletsprojects.com/en/stable/api/) Web framework for Search Engine Prototype UI.

## Scripts:
*The main power of this algorithm is in the process of forming a reverse index*
- generateInvIndex.py 
-- This builds the reverse index by mapping all the terms in the dataset to it's respective ids. 
-- After that, it checks in which documents (in web search engine case, individual sites) each term occurs in the dataset. 
-- This process is manual for now and will have to be re-run each time dataset is updated.
- insertIntoDatabase.py Since Makhzan corpus had all data in XML, i had to convert and insert the data to MySQL with this script.

## App Structure
*Some features pending*
**/ : Home Page**
- Search bar
- URL Detection and Redirection.
- Search History
- Last visited sites Boxes Grid

  ## API Structure
**/search : Search Route** 
- takes in a UTF-8 String
- process the string
- run algorithms on the pre-built reverse
- generates and returns results