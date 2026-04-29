import asyncio
from mongomock_motor import AsyncMongoMockClient
from api.security import encrypt_field, hash_password, verify_password

async def test():
    db = AsyncMongoMockClient()['cyberStudents']
    email = 'test@test.com'
    password = 'testPassword'
    display_name = 'testDisplayName'
    
    # Insert user with encrypted data
    encrypted_email = encrypt_field(email)
    hashed_password = hash_password(password)
    encrypted_display_name = encrypt_field(display_name)
    
    await db.users.insert_one({
        'email': encrypted_email,
        'password': hashed_password,
        'displayName': encrypted_display_name
    })
    
    # Try to find the user
    user = await db.users.find_one({'email': encrypted_email})
    print('User found:', user is not None)
    if user:
        print('Email match:', user['email'] == encrypted_email)
        
        # Try to verify password
        result = verify_password(password, user['password'])
        print('Password verify:', result)

if __name__ == '__main__':
    asyncio.run(test())