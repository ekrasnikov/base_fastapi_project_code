from di import resolve_depends
from domain.hello.usecases.get_hello_info import GetHelloInfoCase, GetHelloInfoOutput
from fastapi import APIRouter, status

router = APIRouter(prefix="/hello", tags=["Hello"])


@router.get(
    "/",
    summary="Get hello info",
    status_code=status.HTTP_200_OK,
    response_model=GetHelloInfoOutput,
)
async def get_hello_info(
    case: GetHelloInfoCase = resolve_depends(GetHelloInfoCase),
):
    return await case()
