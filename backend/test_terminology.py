
from backend.rag.terminology_retriever import retrieve_terminology


questions = [
    "What is a round kick called in Korean?",
    "What does Joonbi mean?",
    "Explain the difference between Jireugi and Makki.",
    "What is the Korean term for horse riding stance?",
    "What does Kalyeo mean in Taekwondo?"
]


for question in questions:

    print("\n" + "=" * 60)
    print("QUESTION:", question)

    results = retrieve_terminology(question, k=4)

    for result in results:

        print("\nRetrieved terminology:")
        print(result["content"])
