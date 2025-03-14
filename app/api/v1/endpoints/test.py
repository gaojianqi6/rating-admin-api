from fastapi import APIRouter
from app.core.security import hash_password, verify_password

router = APIRouter()

@router.get("/test/password")
async def test_password():
    # Plain text password for demonstration purposes.
    plain_password = "123456"

    # Hash the password using the hash_password function from your security module.
    hashed = hash_password(plain_password)

    # Verify the password using verify_password.
    valid = verify_password(plain_password, hashed)
    if not valid:
        # If verification fails, this exception will be caught by the generic handler.
        raise Exception("Password verification failed!")

    # Return the hashed password and verification result.
    # You can store the 'hashed' value in your database for your user record.
    return {
        "code": "200",
        "data": {
            "hashed_password": hashed,
            "verification": valid
        },
        "message": ""
    }
