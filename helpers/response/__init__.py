from django.http import JsonResponse


class ErrorResponse:
    @staticmethod
    def create(status: int, message: str) -> JsonResponse:
        return JsonResponse({"message": message}, status=status)
