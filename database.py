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
    
def search_documents(conn,  query):
    """Search documents using the inverted index"""
    cursor = conn.cursor()
    
    # Process query the same way as documents
    query_terms = query.split(" ") # simple tokenization instead of a whole Tensor flow dependancy
    #TODO add proper input validation
    #TODO add proper input tokenization and lemmentization without NLP library for faster look up
    
    if not query_terms:
        return []
    
    # Build SQL query for searching
    placeholders = ','.join(['%s'] * len(query_terms))

    # * This is the main search look up algorithm written by deepseek for now.
    # * mathes each keyword with the the terms, finds each term in the rev_index and groups the terms back in the results with respective document (ie: website)
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
    LIMIT {20}
    """
    
    cursor.execute(search_query, query_terms)
    results = cursor.fetchall()
    
    return results

# Utils
def process_urdu_text_NLP(lughaat, text):
    """Process Urdu text: normalize, remove stopwords, tokenize, and lemmatize"""
    if not text:
        return []
    
    # Remove stopwords
    cleaned_text = lughaat.normalize(
                    lughaat.remove_special_characters(
                    lughaat.remove_diacritics(
                    lughaat.remove_stopwords( text
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