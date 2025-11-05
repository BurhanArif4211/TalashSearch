from LughaatNLP import LughaatNLP 
import mysql.connector

def setup_database():
    """Create database and tables if they don't exist"""
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database = "urdu_search_engine"
        )
        
        return conn
        
    except Exception as e:
        print(f"Error setting up database: {e}")
        return None

# main action

lughaat = LughaatNLP() 

connection = setup_database()
cursor = connection.cursor()

cursor.execute("SELECT full_text FROM documents;")
hugeUrduData = cursor.fetchall()

hugeUrduData[0][0] ## this accesses the text of first document. data is fetched from the table in this format: [('urdu text...'),(...),(...),...]

# TODO process the urdu text in every document by normalizing stopword removal and tokenize it and build a reverse index which is easy and fast to search 
# important functions that Lughaat NLP gives
# lughaat.remove_stopwords(text)
# lughaat.urdu_tokenize(text)
# lughaat.lemmatize_sentence(sentence)
# lughaat.urdu_stemmer(sentence)

