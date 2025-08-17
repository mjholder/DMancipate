import os
import glob
from dotenv import load_dotenv
from langchain_ollama import OllamaEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from pinecone import Pinecone

load_dotenv()

# Initialize Pinecone client
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

# Define file-to-index mapping
file_index_mapping = {
    "HoardDragonQueen_Encounters.pdf": {"index": "campaign-modules", "namespace": None}
}

# Get all PDF files in the assets directory
pdf_files = glob.glob("src/DMancipate/assets/*.pdf")
print(f"Found {len(pdf_files)} PDF files to process")

# Initialize embeddings
embeddings = OllamaEmbeddings(model="nomic-embed-text", base_url="http://localhost:11434")

# Process each PDF file
for pdf_file in pdf_files:
    filename = os.path.basename(pdf_file)
    print(f"Processing {filename}...")
    
    # Get index configuration for this file
    if filename not in file_index_mapping:
        print(f"Warning: No index mapping found for {filename}, skipping...")
        continue
    
    config = file_index_mapping[filename]
    index_name = config["index"]
    namespace = config["namespace"]
    
    # Clear existing documents from this index/namespace
    print(f"Clearing existing documents from index '{index_name}'{f', namespace \'{namespace}\'' if namespace else ''}...")
    index = pc.Index(index_name)
    # if namespace:
    #     index.delete(delete_all=True, namespace=namespace)
    # else:
    #     index.delete(delete_all=True)
    
    # Load and process the PDF
    loader = PyPDFLoader(pdf_file)
    document = loader.load()
    
    # Add filename as metadata to each document
    for doc in document:
        doc.metadata["source_file"] = filename
    
    # Split into chunks
    text_splitter = CharacterTextSplitter(chunk_size=600, chunk_overlap=150)
    texts = text_splitter.split_documents(document)
    print(f"Created {len(texts)} chunks from {filename}")
    
    # Store in the appropriate Pinecone index
    print(f"Uploading to index '{index_name}'{f', namespace \'{namespace}\'' if namespace else ''}...")
    if namespace:
        PineconeVectorStore.from_documents(
            texts,
            embeddings,
            index_name=index_name,
            namespace=namespace,
        )
    else:
        PineconeVectorStore.from_documents(
            texts,
            embeddings,
            index_name=index_name,
        )
    
    print(f"Successfully processed {filename} into {index_name}")

print("All files processed successfully!")