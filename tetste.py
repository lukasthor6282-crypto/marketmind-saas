import bcrypt

senha = "6282"
hash_senha = bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()
print(hash_senha)