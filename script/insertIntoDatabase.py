# Parses each XML file according to your specified structure
# Handles Urdu text properly (UTF-8 encoding)
# Inserts all data into MySQL database
import os
import xml.etree.ElementTree as ET
import mysql.connector
from mysql.connector import Error

def setup_database():
    """Create database and tables if they don't exist"""
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password=''
        )
        cursor = conn.cursor()
        
        # Create database
        cursor.execute("CREATE DATABASE IF NOT EXISTS urdu_search_engine")
        cursor.execute("USE urdu_search_engine")
        
        # Create documents table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id INT AUTO_INCREMENT PRIMARY KEY,
                file_path VARCHAR(500),
                title TEXT,
                author_name TEXT,
                publication_name TEXT,
                publication_year INT,
                publication_city TEXT,
                publication_link TEXT,
                copyright_holder TEXT,
                contains_non_urdu VARCHAR(10),
                full_text LONGTEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        print("Database setup completed successfully")
        return conn
        
    except Error as e:
        print(f"Error setting up database: {e}")
        return None

def parse_xml_file(file_path):
    """Parse a single XML file and extract data"""
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        # Extract metadata
        meta = root.find('meta')
        title = meta.find('title').text if meta.find('title') is not None else None
        
        # Author information
        author_elem = meta.find('author')
        author_name = author_elem.find('name').text if author_elem is not None and author_elem.find('name') is not None else None
        
        # Publication information
        pub_elem = meta.find('publication')
        pub_name = pub_elem.find('name').text if pub_elem is not None and pub_elem.find('name') is not None else None
        pub_year = pub_elem.find('year').text if pub_elem is not None and pub_elem.find('year') is not None else None
        pub_city = pub_elem.find('city').text if pub_elem is not None and pub_elem.find('city') is not None else None
        pub_link = pub_elem.find('link').text if pub_elem is not None and pub_elem.find('link') is not None else None
        copyright_holder = pub_elem.find('copyright-holder').text if pub_elem is not None and pub_elem.find('copyright-holder') is not None else None
        
        contains_non_urdu = meta.find('contains-non-urdu-languages').text if meta.find('contains-non-urdu-languages') is not None else 'No'
        
        # Extract full text from body
        body = root.find('body')
        full_text_parts = []
        
        if body is not None:
            for section in body.findall('section'):
                for elem in section:
                    if elem.text and elem.text.strip():
                        full_text_parts.append(elem.text.strip())
        
        full_text = ' '.join(full_text_parts)
        
        return {
            'file_path': file_path,
            'title': title,
            'author_name': author_name,
            'publication_name': pub_name,
            'publication_year': int(pub_year) if pub_year and pub_year.isdigit() else None,
            'publication_city': pub_city,
            'publication_link': pub_link,
            'copyright_holder': copyright_holder,
            'contains_non_urdu': contains_non_urdu,
            'full_text': full_text
        }
        
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return None

def insert_document(conn, document_data):
    """Insert document data into database"""
    try:
        cursor = conn.cursor()
        
        insert_query = """
            INSERT INTO documents 
            (file_path, title, author_name, publication_name, publication_year, 
             publication_city, publication_link, copyright_holder, contains_non_urdu, full_text)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(insert_query, (
            document_data['file_path'],
            document_data['title'],
            document_data['author_name'],
            document_data['publication_name'],
            document_data['publication_year'],
            document_data['publication_city'],
            document_data['publication_link'],
            document_data['copyright_holder'],
            document_data['contains_non_urdu'],
            document_data['full_text']
        ))
        
        conn.commit()
        return cursor.lastrowid
        
    except Error as e:
        print(f"Error inserting document: {e}")
        conn.rollback()
        return None

def process_xml_files(directory_path):
    """Process all XML files in the given directory"""
    conn = setup_database()
    if not conn:
        return
    
    processed_count = 0
    error_count = 0
    
    try:
        # Walk through all files in the directory
        for filename in os.listdir(directory_path):
            if filename.endswith('.xml'):
                file_path = os.path.join(directory_path, filename)
                print(f"Processing: {filename}")
                
                # Parse XML file
                document_data = parse_xml_file(file_path)
                
                if document_data:
                    # Insert into database
                    doc_id = insert_document(conn, document_data)
                    if doc_id:
                        processed_count += 1
                        print(f"✓ Inserted document ID: {doc_id}")
                    else:
                        error_count += 1
                        print(f"✗ Failed to insert: {filename}")
                else:
                    error_count += 1
                    print(f"✗ Failed to parse: {filename}")
        
        print(f"\nProcessing completed!")
        print(f"Successfully processed: {processed_count} files")
        print(f"Errors: {error_count} files")
        
    except Exception as e:
        print(f"Error processing directory: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__": #means run this part first when script is executed
    # Specify the path to your /text directory
    text_directory = "C:\\Users\\pc\\Documents\\Burhan Arif Duet\\3rd Semester\\DS\\projects\\SemProj\\App\\Corpus\\text"  # Update this path as needed
    
    if os.path.exists(text_directory):
        process_xml_files(text_directory)
    else:
        print(f"Directory {text_directory} does not exist!")