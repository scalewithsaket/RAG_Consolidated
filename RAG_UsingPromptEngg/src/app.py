from kt_associate import KTAssociate

def test():
    """Test function with sample queries"""
    assistant = KTAssociate()
    
    print("\n--- KT ASSISTANT TEST ---")
    
    # Test 1: A factual question (Should answer correctly)
    q1 = "What is our primary framework and language?"
    print(f"\nUser: {q1}\nAssistant: {assistant.ask(q1)}")
    
    # Test 2: A prohibited tool question (Should show strictness)
    q2 = "Can we use Selenium for new scripts?"
    print(f"\nUser: {q2}\nAssistant: {assistant.ask(q2)}")
    
    # Test 3: An "out of bounds" question (Should refuse to answer)
    q3 = "How do I set up a React project?"
    print(f"\nUser: {q3}\nAssistant: {assistant.ask(q3)}")

    # Test 4: An "out of bounds" question (Should refuse to answer)
    q4 = "How do I set up a backend microservices project?"
    print(f"\nUser: {q4}\nAssistant: {assistant.ask(q4)}")

def main():
    """Main application entry point"""
    assistant = KTAssociate()
    
    print("\n--- KT ASSISTANT ---")
    print("Ask questions about KT. Type 'exit', 'bye', or 'quit' to close.\n")
    
    while True:
        prompt = input("You: ").strip()
        
        if prompt.lower() in ['exit', 'bye', 'quit']:
            print("Assistant: Goodbye!")
            break
            
        if prompt:
            print(f"Assistant: {assistant.ask(prompt)}\n")

if __name__ == "__main__":
    main()