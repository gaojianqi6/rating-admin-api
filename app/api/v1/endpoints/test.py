from fastapi import APIRouter
from app.core.security import hash_password, verify_password
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

router = APIRouter(prefix="/test", tags=["test"])

@router.get("/password")
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
        "hashedPassword": hashed,
        "verification": valid
    }

@router.get("/camel-case")
async def test_password():
    from app.models.template import Template

    template = Template(
        name="test_template",
        display_name="Test Display Name",
        description="Test description",
        full_marks=10
    )

    # 尝试不同的序列化方法
    print("model_dump:", template.model_dump(by_alias=True))
    print("dict:", template.dict(by_alias=True))
    print("jsonable_encoder:", jsonable_encoder(template, by_alias=True))

    # 使用jsonable_encoder处理datetime
    serialized_template = jsonable_encoder(template, by_alias=True)

    # 返回处理后的字典
    return serialized_template
