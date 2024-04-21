import jwt

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS512"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

x = jwt.encode({"hello":"world"},SECRET_KEY,ALGORITHM)
z = jwt.encode({"hello":"world"},SECRET_KEY,"HS256")
print(x)
print(z)

# y= jwt.decode(x,  SECRET_KEY, ALGORITHM)
# print(y)

print(len(x))
print(len(z))