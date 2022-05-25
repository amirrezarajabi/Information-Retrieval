from search_engine import SEARCH_ENGINE

print("Setting Up ...")
SE = SEARCH_ENGINE(Load=True, Save=False)

while True:
    data = input("Enter your query: ")
    if data == "exit":
        break
    ans = SE.answer(data)
    s = "\n".join(ans)
    print(s)

print("Bye!")
