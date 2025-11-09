from LughaatNLP import LughaatNLP
import mysql.connector
from collections import defaultdict
import json

def setup_database():
    """Create database and tables if they don't exist"""
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database="urdu_search_engine"
        )
        return conn
    except Exception as e:
        print(f"Error setting up database: {e}")
        return None

def create_inverted_index_tables(conn):
    """Create tables for inverted index"""
    cursor = conn.cursor()
    
    # Create terms table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS terms (
            term_id INT AUTO_INCREMENT PRIMARY KEY,
            term VARCHAR(150) UNIQUE NOT NULL,
            document_frequency INT DEFAULT 0
        )
    """)
    print("asdasdasdsd")
    # Create inverted_index table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inverted_index (
            term_id INT,
            doc_id INT,
            term_frequency INT,
            positions JSON,
            PRIMARY KEY (term_id, doc_id),
            FOREIGN KEY (term_id) REFERENCES terms(term_id),
            FOREIGN KEY (doc_id) REFERENCES documents(id)
        )
    """)
    
    # WARNING (this won't work since memory limits)
    # Create indexes for faster search 
    # cursor.execute("CREATE INDEX IF NOT EXISTS idx_terms_term ON terms(term)")
    # cursor.execute("CREATE INDEX IF NOT EXISTS idx_inverted_index_term ON inverted_index(term_id)")
    # cursor.execute("CREATE INDEX IF NOT EXISTS idx_inverted_index_doc ON inverted_index(doc_id)")
    
    conn.commit()
    print("Inverted index tables created successfully")

def process_urdu_text(lughaat, text):
    """Process Urdu text: normalize, remove stopwords, tokenize, and lemmatize"""
    if not text:
        return []
    
    # Remove stopwords
    cleaned_text = lughaat.normalize(
                    lughaat.remove_special_characters(
                    lughaat.remove_diacritics(
                    lughaat.remove_stopwords(text
                ))))
    # Tokenize
    tokens = lughaat.urdu_tokenize(cleaned_text)
    
    # Lemmatize tokens
    lemmatized_tokens = []
    for token in tokens:
        lemmatized = lughaat.lemmatize_sentence(token)
        # Also apply stemming for better coverage
        stemmed = lughaat.urdu_stemmer(token)
        # Use lemmatized version if available, otherwise stemmed
        final_token = lemmatized if lemmatized and lemmatized.strip() else stemmed
        if final_token and final_token.strip():
            lemmatized_tokens.append(final_token.strip())
    
    return lemmatized_tokens

def build_inverted_index(conn, lughaat, documents_data):
    """Build inverted index from documents data"""
    try:
        cursor = conn.cursor()

        # Clear existing index
        cursor.execute("DELETE FROM inverted_index")
        cursor.execute("DELETE FROM terms")
        conn.commit()

        # Temporary storage for building index
        term_to_id = {}
        inverted_index = defaultdict(lambda: defaultdict(lambda: {'frequency': 0, 'positions': []}))

        print("Processing documents and building inverted index...")

        for doc_id, doc_text in documents_data:
            if doc_id % 100 == 0:
                print(f"Processed {doc_id}/{len(documents_data)} documents")

            # Process the Urdu text
            tokens = process_urdu_text(lughaat, doc_text)

            # Build term positions and frequencies
            term_positions = defaultdict(list)
            for position, token in enumerate(tokens):
                term_positions[token].append(position)

            # Update inverted index
            for term, positions in term_positions.items():
                inverted_index[term][doc_id] = {
                    'frequency': len(positions),
                    'positions': positions
                }

        print("Inserting terms and inverted index into database...")

        # Insert terms and get their IDs
        all_terms = list(inverted_index.keys())
        for i, term in enumerate(all_terms):
            if i % 1000 == 0:
                print(f"Inserted {i}/{len(all_terms)} terms")

            try:
                cursor.execute(
                    "INSERT INTO terms (term, document_frequency) VALUES (%s, %s)",
                    (term, len(inverted_index[term]))
                )
                term_to_id[term] = cursor.lastrowid
            except mysql.connector.IntegrityError:
                # Term already exists, get existing ID
                cursor.execute("SELECT term_id FROM terms WHERE term = %s", (term,))
                term_to_id[term] = cursor.fetchone()[0]

        # Insert inverted index entries
        batch_size = 1000
        batch_data = []

        for term, doc_data in inverted_index.items():
            term_id = term_to_id[term]
            for doc_id, data in doc_data.items():
                batch_data.append((
                    term_id,
                    doc_id,
                    data['frequency'],
                    json.dumps(data['positions'])
                ))

                if len(batch_data) >= batch_size:
                    cursor.executemany(
                        "INSERT INTO inverted_index (term_id, doc_id, term_frequency, positions) VALUES (%s, %s, %s, %s)",
                        batch_data
                    )
                    batch_data = []

        # Insert remaining batch
        if batch_data:
            cursor.executemany(
                "INSERT INTO inverted_index (term_id, doc_id, term_frequency, positions) VALUES (%s, %s, %s, %s)",
                batch_data
            )

        conn.commit()
        print("Inverted index built successfully!")
    except Exception as e:
        print(f"Exeption Thrown: {e}")

def search_documents(conn, lughaat, query):
    """Search documents using the inverted index"""
    cursor = conn.cursor()
    
    # Process query the same way as documents
    query_terms = process_urdu_text(lughaat, query)
    
    if not query_terms:
        return []
    
    # Build SQL query for searching
    placeholders = ','.join(['%s'] * len(query_terms))
    
    search_query = f"""
    SELECT d.id, d.title, d.publication_name, d.publication_link, 
           SUM(ii.term_frequency * (1.0 / t.document_frequency)) as relevance_score,
           GROUP_CONCAT(DISTINCT t.term) as matched_terms
    FROM documents d
    JOIN inverted_index ii ON d.id = ii.doc_id
    JOIN terms t ON ii.term_id = t.term_id
    WHERE t.term IN ({placeholders})
    GROUP BY d.id, d.title, d.publication_name, d.publication_link
    ORDER BY relevance_score DESC
    LIMIT 20
    """
    
    cursor.execute(search_query, query_terms)
    results = cursor.fetchall()
    
    return results

def main():
    """Main function to build the inverted index"""
    # Initialize LughaatNLP
    lughaat = LughaatNLP()
    
    # Setup database connection
    connection = setup_database()
    if not connection:
        print("Failed to connect to database")
        return
    
    try:
        # pass
        # # Create inverted index tables
        # create_inverted_index_tables(connection)
        
        # # Fetch all documents
        # cursor = connection.cursor()
        # cursor.execute("SELECT id, full_text FROM documents")
        # documents_data = cursor.fetchall()
        
        # print(f"Found {len(documents_data)} documents to process")
        # # print(documents_data[:3])
        # # documents_data = [(1,'...'),(2,'...'),...]
        # if not documents_data:
        #     print("No documents found in the database")
        #     return
        
        # # Build the inverted index
        # build_inverted_index(connection, lughaat, documents_data)
        
        # Test search functionality
        test_query = "اسلامی قوانین"
        print(f"\nTesting search with query: '{test_query}'")
        
        results = search_documents(connection, lughaat, test_query)
        print(f"Found {len(results)} results:")
        
        for i, (doc_id, title, pub_name, pub_link, score, terms) in enumerate(results[:5], 1):
            print(f"{i}. Document ID: {doc_id}, Score: {score:.4f}")
            print(f"   Title: {title}")
            print(f"   Matched terms: {terms}")
            print()
            
    except Exception as e:
        print(f"Error in main execution: {e}")
        
    finally:
        if connection:
            connection.close()

if __name__ == "__main__":
    main()


# from LughaatNLP import LughaatNLP 
# import mysql.connector

# def setup_database():
#     """Create database and tables if they don't exist"""
#     try:
#         conn = mysql.connector.connect(
#             host='localhost',
#             user='root',
#             password='',
#             database = "urdu_search_engine"
#         )
        
#         return conn
        
#     except Exception as e:
#         print(f"Error setting up database: {e}")
#         return None

# # main action

# lughaat = LughaatNLP() 

# connection = setup_database()
# cursor = connection.cursor()

# cursor.execute("SELECT full_text FROM documents;")
# hugeUrduData = cursor.fetchall()

# hugeUrduData[0][0] ## this accesses the text of first document. data is fetched from the table in this format: [('urdu text...'),(...),(...),...]

# # TODO process the urdu text in every document by normalizing stopword removal and tokenize it and build a reverse index which is easy and fast to search 
# # important functions that Lughaat NLP gives
# # lughaat.remove_stopwords(text)
# # lughaat.urdu_tokenize(text)
# # lughaat.lemmatize_sentence(sentence)
# # lughaat.urdu_stemmer(sentence)

