import tiktoken

enc = tiktoken.encoding_for_model("gpt-4o")

text = "Hello world"
tokens = enc.encode(text)
#tokens:[13225,2375]
print("Tokens:", tokens)
print("len(tokens):", len(tokens))
decoded=enc.decode([13225, 2375])  # 'Hello world'
print("Decoded:", decoded)