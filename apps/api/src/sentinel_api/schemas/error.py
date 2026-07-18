from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    loc: list[str | int] | None = Field(
        None, description="Location of the validation error"
    )
    msg: str = Field(..., description="Details of the error message")
    type: str = Field(..., description="Type or category of the error")


class ErrorResponse(BaseModel):
    success: bool = Field(False, description="Whether the operation succeeded")
    error_code: str = Field(..., description="Machine-readable application error code")
    message: str = Field(..., description="Human-readable general error message")
    details: list[ErrorDetail] | None = Field(
        None, description="Specific field validation or detailed error items"
    )
