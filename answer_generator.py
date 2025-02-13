from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from pathlib import Path
import json 
import os
from typing import Dict, List
import argparse
from langchain_groq import ChatGroq
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv

def initialize_models():
    """Initialize the embedding model and vector store"""
    load_dotenv()
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
    vector_store = Chroma(embedding_function=embeddings)
    llm = ChatGroq(model="llama-3.3-70b-versatile")
    
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vector_store.as_retriever(),
        return_source_documents=True
    )
    return qa_chain

def load_questions(assignment_number: int) -> List[Dict]:
    """Load and format questions from JSON file"""
    json_path = f"./questions_{assignment_number}.json"
    formatted_ques = []
    
    with open(json_path, 'r') as file:
        data = json.load(file)
    
    for d in data:
        question = d["question_text"]
        options = []
        input_ids = []
        for i in d['options']:
            options.append(i["text"])
            input_ids.append(i["input_id"])
            
        formatted_ques.append({
            "question": question,
            "options": options,
            "input_ids": input_ids
        })
    
    return formatted_ques

def generate_answers(qa_chain, formatted_ques: List[Dict]) -> List[Dict]:
    """Generate answers using the QA chain"""
    results = []
    
    for q in formatted_ques:
        prompt = f"""{q['question']}
You are a helpful assistant that only responds with a single number.
Based on the question and options above, which option number (1-{len(q['options'])}) is correct?
Important: Respond with only the number itself and nothing else. Do not explain your reasoning.
If you are unsure, make your best guess.
Your response should look like: 1, 2, 3, or 4."""

        response = qa_chain({"query": prompt})
        answer = response['result']
        
        try:
            correct_option = int(answer.strip()) - 1
            correct_input_id = q["input_ids"][correct_option]
            
            results.append({
                'question': q['question'],
                'correct_option': correct_option + 1,
                'correct_input_id': correct_input_id
            })
            
        except (ValueError, IndexError) as e:
            print(f"Error processing question: {e}")
            continue
            
    return results

def save_answers(results: List[Dict], assignment_number: int) -> str:
    """Save answers to a text file and return the filename"""
    output_file = f"answers_{assignment_number}.txt"
    with open(output_file, 'w') as f:
        for result in results:
            f.write(f"{result['correct_input_id']}\n")
    return output_file

def main(assignment_number: int):
    """Main function to orchestrate the answer generation process"""
    qa_chain = initialize_models()
    formatted_questions = load_questions(assignment_number)
    results = generate_answers(qa_chain, formatted_questions)
    output_file = save_answers(results, assignment_number)
    print(f"Answers have been saved to {output_file}")
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-assgn", "--assignment_number", help="The number of the Assignment", type=int)
    args = parser.parse_args()
    main(args.assignment_number)

