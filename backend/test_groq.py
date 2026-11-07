from llm import get_llm

llm = get_llm()

response = llm.invoke(
    "Explain three benefits of Taekwondo training."
)

print(response.content)