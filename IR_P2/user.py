from search_engine import SEARCH_ENGINE

print("Setting Up ...")
SE = SEARCH_ENGINE(Load=False, Save=True)

while True:
    data = input("Enter your query: ")
    if data == "exit":
        break
    ans = SE.answer(data)
    s = "\n".join(ans)
    print(s)

print("Bye!")
